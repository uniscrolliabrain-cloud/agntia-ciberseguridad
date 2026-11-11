"""Server-curated tariffs. Decimal input strings, ceil after tax/FX, never floats."""
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from typing import Literal
from pydantic import Field, StrictInt, field_validator, model_validator
from ..contracts import Model, OpaqueId
from ..util import digest

CAPS = {'Lite': 3000, 'L': 7000, 'XL': 30000}

class Rate(Model):
    version: OpaqueId
    provider_ref: OpaqueId
    source_ref: OpaqueId
    reviewed_by_ref: OpaqueId
    valid_until: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    currency: Literal['EUR', 'USD'] = 'EUR'
    unit_price_minor: str = Field(max_length=30)
    fx_to_eur: str = Field(default='1', max_length=30)
    tax_basis_points: StrictInt = Field(default=0, ge=0, le=10000)
    minimum_minor: str = Field(default='0', max_length=30)
    hard_limit_verified: bool = False
    uncertainty_margin_cents: StrictInt = Field(default=0, ge=0, le=30000)
    commercial_use_review_ref: OpaqueId
    @field_validator('unit_price_minor', 'fx_to_eur', 'minimum_minor')
    @classmethod
    def decimal_string(cls, value):
        import re
        if not re.fullmatch(r'\d{1,12}(?:\.\d{1,8})?', value):
            raise ValueError('Bounded nonnegative decimal string required')
        try: number = Decimal(value)
        except InvalidOperation: raise ValueError('Invalid decimal') from None
        if not number.is_finite(): raise ValueError('Finite decimal required')
        return value
    @model_validator(mode='after')
    def bounds(self):
        from datetime import date
        date.fromisoformat(self.valid_until)
        if Decimal(self.fx_to_eur) <= 0 or (self.currency == 'EUR' and Decimal(self.fx_to_eur) != 1):
            raise ValueError('Invalid FX')
        return self
    def worst_case(self, units):
        cost = max(Decimal(self.minimum_minor), Decimal(self.unit_price_minor) * units)
        cost *= Decimal(self.fx_to_eur) * (Decimal(1) + Decimal(self.tax_basis_points) / 10000)
        return int(cost.to_integral_value(rounding=ROUND_CEILING)) + self.uncertainty_margin_cents
    @property
    def content_hash(self): return digest(self.model_dump(mode='json'))

class BudgetPolicy(Model):
    plan: Literal['Lite', 'L', 'XL']
    fixed_commitment_cents: StrictInt = Field(default=0, ge=0, le=30000)
    reserve_margin_cents: StrictInt = Field(default=0, ge=0, le=30000)
    allocation_review_ref: OpaqueId
    # Includes shared infrastructure, annual cash commitments and minimums if any.
    rates: dict[OpaqueId, Rate] = Field(default_factory=dict, max_length=32)
    @model_validator(mode='after')
    def cap(self):
        if self.fixed_commitment_cents + self.reserve_margin_cents > CAPS[self.plan]:
            raise ValueError('Commitments exceed cap')
        return self
