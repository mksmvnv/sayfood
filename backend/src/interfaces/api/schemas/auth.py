from pydantic import BaseModel, EmailStr, Field


class UserRegisterSchema(BaseModel):
    """User Register schema."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
