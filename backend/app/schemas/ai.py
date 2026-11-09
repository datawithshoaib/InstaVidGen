from pydantic import Field

from app.schemas.common import ApiModel


class QuoteRequest(ApiModel):
    theme: str | None = Field(default=None, max_length=60)
    author: str | None = Field(default=None, max_length=80)
    model: str | None = Field(default=None, max_length=120)
    avoid: list[str] = Field(
        default_factory=list,
        max_length=30,
        description="Recently used quotes the model should not repeat.",
    )


class QuoteResponse(ApiModel):
    quote: str
    author: str | None = None
    model: str


class CaptionRequest(ApiModel):
    quote: str = Field(min_length=1, max_length=600)
    theme: str | None = Field(default=None, max_length=60)
    author: str | None = Field(default=None, max_length=80)
    model: str | None = Field(default=None, max_length=120)


class CaptionResponse(ApiModel):
    caption: str
    hashtags: list[str]
    model: str
