from pydantic import BaseModel, Field


class ProviderAuthPayload(BaseModel):
    provider: str = Field(pattern="^(github|gitlab)$")
    access_token: str = Field(min_length=1)
    scopes: list[str] = Field(min_length=1)
