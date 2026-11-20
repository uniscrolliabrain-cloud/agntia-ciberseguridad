"""Export closed wire contracts; schemas do not enable pending capabilities."""
import json
from pathlib import Path
from agntia_ciberseguridad import contracts
from agntia_ciberseguridad.install import InstallManifest

ROOT=Path(__file__).resolve().parents[1]
MODELS=('Tenant','PrincipalPublic','AssetPublic','AssetCreate','GrantCreate','GrantApproval','GrantRevocation','AuditPreview','Job','Evidence','Finding','Approval','BudgetReservation')
EXTRA=(InstallManifest,)
def main():
    folder=ROOT/'docs/implementation/schemas'
    folder.mkdir(parents=True,exist_ok=True)
    for model in (*(getattr(contracts,name) for name in MODELS),*EXTRA):
        (folder/(model.__name__+'.json')).write_text(json.dumps(model.model_json_schema(),indent=2,sort_keys=True)+'\n')
    print(json.dumps({'schemas_exported':len(MODELS)+len(EXTRA),'schema_version':1,'runtime_workers_enabled':False}))
if __name__=='__main__':main()
