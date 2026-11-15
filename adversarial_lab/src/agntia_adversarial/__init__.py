"""Independent Adversarial Lab.

This package never imports ``agntia_ciberseguridad``. All execution is confined to synthetic
twins, network egress is denied by default, and every effect is authorized by a deterministic
policy layer before it happens.
"""

from .config import LabConfig

__all__ = ["LabConfig"]
__version__ = "0.1.0"
