from datetime import datetime

from pydantic import BaseModel


class ComponentProfile(BaseModel):
    component_id: str
    repository_id: str
    language: str
    ownership: str
    last_modified_at: datetime
