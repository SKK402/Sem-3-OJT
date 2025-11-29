import time
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.database import get_db_session
from app.schemas.search import FilterSchema, SearchResponse
from app.services.search import SearchService
from app.services.synonyms import SynonymService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/search", response_model=SearchResponse)
async def search_products(
    q: str | None = Query(default=None, max_length=128),
    min_price: int | None = Query(default=None, ge=0),
    max_price: int | None = Query(default=None, ge=0),
    colors: list[str] = Query(default_factory=list),
    categories: list[str] = Query(default_factory=list),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=12, ge=1, le=50),
    sort: str = Query(default="relevance"),
    session: AsyncSession = Depends(get_db_session),
    cache=Depends(deps.get_cache),
    synonyms: SynonymService = Depends(deps.get_synonyms),
) -> SearchResponse:
    """Search products with filters, pagination, and faceting."""
    filters = FilterSchema(
        q=q,
        min_price=min_price,
        max_price=max_price,
        colors=colors,
        categories=categories,
        page=page,
        limit=limit,
        sort=sort,
    )
    service = SearchService(cache, synonyms)
    return await service.search(session, filters)


@router.get("/search/explain")
async def explain_search(
    q: str | None = Query(default=None, max_length=128),
    min_price: int | None = Query(default=None, ge=0),
    max_price: int | None = Query(default=None, ge=0),
    colors: list[str] = Query(default_factory=list),
    categories: list[str] = Query(default_factory=list),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=12, ge=1, le=50),
    sort: str = Query(default="relevance"),
    session: AsyncSession = Depends(get_db_session),
    cache=Depends(deps.get_cache),
    synonyms: SynonymService = Depends(deps.get_synonyms),
) -> dict:
    """Explain endpoint showing query performance metrics."""
    filters = FilterSchema(
        q=q,
        min_price=min_price,
        max_price=max_price,
        colors=colors,
        categories=categories,
        page=page,
        limit=limit,
        sort=sort,
    )
    
    start_time = time.perf_counter()
    service = SearchService(cache, synonyms)
    
    # Check cache first
    cache_key = service._cache_key(filters)
    cached = await cache.get(cache_key)
    cache_hit = cached is not None
    
    # Execute search
    result = await service.search(session, filters)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    
    return {
        "filters": filters.model_dump(),
        "performance": {
            "response_time_ms": round(elapsed_ms, 2),
            "cache_hit": cache_hit,
            "target_ms": 150,
            "meets_target": elapsed_ms < 150,
        },
        "results": {
            "total": result.pagination.total,
            "returned": len(result.results),
            "page": result.pagination.page,
            "limit": result.pagination.limit,
        },
        "facets": {
            "category_count": len(result.facets.categories),
            "color_count": len(result.facets.colors),
        },
    }


@router.post("/cache/invalidate")
async def invalidate_cache(
    prefix: str = Query(default=""),
    cache=Depends(deps.get_cache),
) -> dict:
    """Invalidate cache entries matching a prefix."""
    if prefix:
        await cache.invalidate(f"search:{prefix}")
        return {"status": "success", "message": f"Invalidated cache entries with prefix: {prefix}"}
    else:
        # Invalidate all search cache entries
        await cache.invalidate("search:")
        return {"status": "success", "message": "Invalidated all search cache entries"}

