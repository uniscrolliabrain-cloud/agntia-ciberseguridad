from typing import Annotated,Literal
from pydantic import Field,StrictInt
from ..contracts import Model,ResourceId,Hash,Profile,Revision
from ..runners.base import Tool

class AuditJobCreate(Model):
    schema_version: Literal[1]=1
    asset_id: ResourceId
    grant_id: ResourceId
    snapshot_id: ResourceId
    snapshot_hash: Hash
    expected_grant_revision: Annotated[StrictInt,Field(ge=0)]
    profile: Literal[Profile.static_read]=Profile.static_read
    tool: Tool
    max_attempts: Annotated[StrictInt,Field(ge=1,le=3)]=1
    maximum_cost_cents: Annotated[StrictInt,Field(ge=0,le=0)]=0

class CancelJob(Revision):pass
TERMINAL=frozenset({'completed','partial','failed','cancelled','blocked','reconciliation_required'})
