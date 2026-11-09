from fastapi import APIRouter

from app.api.deps import GroqKeyDep, ServicesDep
from app.schemas.ai import CaptionRequest, CaptionResponse, QuoteRequest, QuoteResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/quote", response_model=QuoteResponse)
async def generate_quote(
    req: QuoteRequest, services: ServicesDep, api_key: GroqKeyDep
) -> QuoteResponse:
    [content] = await services.ai.generate(
        count=1,
        theme=req.theme,
        author=req.author,
        avoid=req.avoid,
        model=req.model,
        api_key=api_key,
    )
    return QuoteResponse(
        quote=content.quote, author=req.author, model=services.ai.model_name(req.model)
    )


@router.post("/caption", response_model=CaptionResponse)
async def generate_caption(
    req: CaptionRequest, services: ServicesDep, api_key: GroqKeyDep
) -> CaptionResponse:
    result = await services.ai.caption(
        quote=req.quote, theme=req.theme, author=req.author, model=req.model, api_key=api_key
    )
    return CaptionResponse(caption=result.caption, hashtags=result.hashtags, model=result.model)
