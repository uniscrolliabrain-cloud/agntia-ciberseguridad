"""Private trusted-code scope, never extracted from headers, model text or a bearer."""
from contextlib import contextmanager
from contextvars import ContextVar
_SCOPE=ContextVar('agntia_verified_scope',default=None)

@contextmanager
def verified_scope(actor,tenant,capability):
    token=_SCOPE.set((actor.binding_id,tenant,capability))
    try:yield
    finally:_SCOPE.reset(token)

def permits(actor,tenant,capability):return _SCOPE.get()==(actor.binding_id,tenant,capability)
