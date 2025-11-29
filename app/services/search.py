from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import Cache
from app.repositories.product_repository import ProductRepository
from app.schemas.search import FacetCounts, FilterSchema, PaginationMeta, ProductHit, SearchResponse
from app.services.synonyms import SynonymService


class SearchService:
    def __init__(self, cache: Cache, synonyms: SynonymService) -> None:
        self.cache = cache
        self.synonyms = synonyms

    def _cache_key(self, filters: FilterSchema) -> str:
        # Use model_dump with sort_keys, then json.dumps for consistent ordering
        data = filters.model_dump()
        json_str = json.dumps(data, sort_keys=True)
        fingerprint = hashlib.sha1(json_str.encode()).hexdigest()
        return f"search:{fingerprint}"

    async def search(self, session: AsyncSession, filters: FilterSchema) -> SearchResponse:
        key = self._cache_key(filters)
        cached = await self.cache.get(key)
        if cached:
            cached['cached'] = True
            return SearchResponse(**cached)

        repository = ProductRepository(session, self.synonyms)
        products, total = await repository.search(filters)
        facets_raw = await repository.facets(filters)
        facets = FacetCounts(**facets_raw)

        hits = [
            ProductHit(
                id=product.id,
                sku=product.sku,
                name=product.name,
                description=product.description,
                category=product.category,
                color=product.color,
                price_cents=product.price_cents,
                currency=product.currency,
                stock_qty=product.stock_qty,
            )
            for product in products
        ]

        pagination = PaginationMeta(
            total=total,
            page=filters.page,
            limit=filters.limit,
            has_next=(filters.page * filters.limit) < total,
        )

        response = SearchResponse(
            filters=filters,
            results=hits,
            facets=facets,
            pagination=pagination,
            cached=False,
        )

        await self.cache.set(key, json.loads(response.model_dump_json()))
        return response

    async def invalidate_filters(self, prefix: str) -> None:
        await self.cache.invalidate(f"search:{prefix}")

