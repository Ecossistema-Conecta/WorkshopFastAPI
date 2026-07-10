from datetime import datetime

from pydantic import UUID7, BaseModel


class ProjectBaseModel(BaseModel, validate_assignment=True):
    id: UUID7
    status: bool
    created_at: datetime
    updated_at: datetime
