from pydantic import BaseModel


class ResponseId(BaseModel):
    id: int