from pydantic import UUID7, BaseModel, ConfigDict

from src.common.domain.models.project_base_model import ProjectBaseModel


class EmailLogBase(BaseModel):
    id_control: str | None
    receiver_id: UUID7
    sender_id: UUID7 | None
    subject: str
    body: str
    error: str | None


class EmailLogModel(EmailLogBase, ProjectBaseModel):
    model_config = ConfigDict(from_attributes=True)  # pyright: ignore[reportUnannotatedClassAttribute]
