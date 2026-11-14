from typing import Annotated,Literal
from pydantic import Field,StrictInt
from ..contracts import Model,Revision,ResourceId

class EvidenceUpload(Model):
    content_b64: str=Field(min_length=1,max_length=2800000)
    media_type: Literal['text/plain','application/json','application/pdf']
    source_job_id: ResourceId|None=None

class EvidenceReview(Revision):
    reason: str=Field(min_length=5,max_length=500)

class EvidenceHold(Revision):
    enabled: bool
    reason: str=Field(min_length=5,max_length=500)
