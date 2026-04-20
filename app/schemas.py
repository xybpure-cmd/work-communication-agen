from pydantic import BaseModel, Field


class GenerateReplyRequest(BaseModel):
    incoming_message: str = ""
    communication_background: str = Field(min_length=1)
    reference_material: str = Field(min_length=1)
    my_intent: str = Field(min_length=1)


class GenerateReplyResponse(BaseModel):
    draft_reply: str
