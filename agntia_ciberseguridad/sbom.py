"""Minimal observed CycloneDX1.5 producer; unknown licenses/reachability stay unknown."""
import re
from urllib.parse import quote
from .util import digest

ECOSYSTEMS={'PyPI':'pypi','npm':'npm','Go':'golang','Maven':'maven','crates.io':'cargo','NuGet':'nuget','RubyGems':'gem'}

def purl(ecosystem,name,version):
    if ecosystem not in ECOSYSTEMS:return None
    package=quote(name,safe='/')
    return 'pkg:'+ECOSYSTEMS[ecosystem]+'/'+package+'@'+quote(version,safe='')

def build(components,snapshot_id):
    items=[]
    for component in components:
        ref=component['purl'] or 'urn:agntia:component:'+component['id']
        item={'type':'library','bom-ref':ref,'name':component['name'],'version':component['version'],
              'properties':[{'name':'agntia:ecosystem','value':component['ecosystem']},
                            {'name':'agntia:relationship','value':'unknown'},
                            {'name':'agntia:license-observation','value':'unknown'}]}
        if component['purl']:item['purl']=component['purl']
        items.append(item)
    return {'bomFormat':'CycloneDX','specVersion':'1.5','version':1,
            'metadata':{'properties':[{'name':'agntia:snapshot','value':snapshot_id},
                                      {'name':'agntia:producer','value':'agntia-ciberseguridad/0.1.0a1'}]},
            'components':items}

def diff(previous,current):
    old={c['id']:c for c in previous};new={c['id']:c for c in current}
    return {'added':[new[k] for k in sorted(new.keys()-old.keys())],
            'not_observed':[old[k] for k in sorted(old.keys()-new.keys())],
            'notice':'Not observed does not mean fixed; compare acquisition and scanner coverage.'}
