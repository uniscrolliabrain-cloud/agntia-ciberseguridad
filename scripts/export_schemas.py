"""Export closed wire contracts; schemas do not enable pending capabilities."""
import json
from pathlib import Path
from agntia_ciberseguridad import contracts

ROOT=Path(__file__).resolve().parents[1]
MODELS=('Tenant','PrincipalPublic','AssetPublic','AssetCreate','GrantCreate','GrantApproval','GrantRevocation','AuditPreview','Job','Evidence','Finding','Approval','BudgetReservation')
def main():
    folder=ROOT/'docs/implementation/schemas'
    folder.mkdir(parents=True,exist_ok=True)
    for name in MODELS:
        (folder/(name+'.json')).write_text(json.dumps(getattr(contracts,name).model_json_schema(),indent=2,sort_keys=True)+'\n')
    print(json.dumps({'schemas_exported':len(MODELS),'schema_version':1,'runtime_workers_enabled':False}))
if __name__=='__main__':main()
