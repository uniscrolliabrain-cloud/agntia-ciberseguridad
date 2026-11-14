"""Official CycloneDX1.5 bundle, bounded import, no remote schema resolution."""
from importlib.resources import files
import json
from jsonschema import Draft7Validator,FormatChecker
from referencing import Registry,Resource
from referencing.exceptions import NoSuchResource
from .adapters.common import load_json,InvalidReport
from .util import digest

def validator():
    def refuse(uri):raise NoSuchResource(ref=uri)
    registry=Registry(retrieve=refuse)
    root=files('agntia_ciberseguridad').joinpath('data/cyclonedx');main=None
    for name in ('bom-1.5.schema.json','spdx.schema.json','jsf-0.82.schema.json'):
        schema=json.loads(root.joinpath(name).read_text(encoding="utf-8"))
        registry=registry.with_resource(schema['$id'],Resource.from_contents(schema))
        if name.startswith('bom-'):main=schema
    return Draft7Validator(main,registry=registry,format_checker=FormatChecker())

def validate(raw):
    document=load_json(raw,maximum=2*1024*1024)
    try:
        if not isinstance(document,dict) or document.get('bomFormat')!='CycloneDX' or document.get('specVersion')!='1.5':raise InvalidReport('Unsupported SBOM format')
        if len(document.get('components',[]))>10000:raise InvalidReport('Component limit')
        if next(validator().iter_errors(document),None)is not None:raise InvalidReport('Invalid CycloneDX1.5')
        return document
    except (RecursionError,TypeError,KeyError):raise InvalidReport('Invalid CycloneDX1.5') from None

def import_observed(raw):
    document=validate(raw);components=[];seen=set();warnings=[]
    for item in document.get('components',[]):
        if item.get('components'):warnings.append('nested_components_not_imported')
        if not item.get('version'):warnings.append('unversioned_component_not_imported');continue
        identity=digest({'type':item['type'],'name':item['name'],'version':item['version'],'purl':item.get('purl')})
        if identity in seen:continue
        seen.add(identity)
        components.append({'id':identity,'name':item['name'],'version':item['version'],'purl':item.get('purl'),
            'licenses':'unknown','relationship':'unknown','source':'imported_sbom_unverified'})
    return {'schema_version':1,'status':'partial' if warnings else 'imported_unverified','components':components,
        'source_hash':digest(document),'warnings':sorted(set(warnings)),'notice':'Schema-valid does not prove completeness, licenses or deployment.'}
