from pydantic import BaseModel, Field

class CommandRequest(BaseModel):
    command: str
    value: int = Field(default=0, ge=0, le=100)

class LoginRequest(BaseModel):
    username: str
    password: str
