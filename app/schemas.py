from pydantic import BaseModel, Field


class GenerateReplyRequest(BaseModel):
    person_id: int
    matter_id: int
    incoming_message: str = Field(min_length=1)
    communication_goal: str = Field(min_length=1)
    modifiers: list[str] = []


class GenerateReplyResponse(BaseModel):
    prudent: str
    concise: str
    push_forward: str
    memory_context: str


class SaveReplyRequest(BaseModel):
    person_id: int
    matter_id: int
    incoming_message: str
    communication_goal: str
    modifiers: list[str] = []
    prudent: str
    concise: str
    push_forward: str
    selected_reply: str
