from pydantic import BaseModel, Field, field_validator


class ProviderAuthPayload(BaseModel):
    provider: str = Field(pattern="^(github|gitlab)$")
    access_token: str = Field(min_length=1)
    scopes: list[str] = Field(min_length=1)

    @field_validator("access_token")
    @classmethod
    def validate_access_token(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("access_token must not be blank")
        return trimmed
