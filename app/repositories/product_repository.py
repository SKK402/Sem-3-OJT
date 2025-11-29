from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.schemas.search import FilterSchema
from app.services.synonyms import SynonymService


class ProductRepository:
    def __init__(self, session: AsyncSession, synonyms: SynonymService) -> None:
        self.session = session
        self.synonyms = synonyms

    def _base_query(self) -> Select:
        return select(Product)

    def _apply_filters(self, stmt: Select, filters: FilterSchema) -> Select:
        if filters.q:
            terms = self.synonyms.expand(filters.q)
            text_filters = [Product.searchable_text.ilike(f"%{term}%") for term in terms]
            stmt = stmt.where(or_(*text_filters))

        if filters.min_price is not None:
            stmt = stmt.where(Product.price_cents >= filters.min_price)
        if filters.max_price is not None:
            stmt = stmt.where(Product.price_cents <= filters.max_price)
        if filters.colors:
            stmt = stmt.where(Product.color.in_([color.lower() for color in filters.colors]))
        if filters.categories:
            stmt = stmt.where(
                Product.category.in_([category.lower() for category in filters.categories])
            )
        return stmt

    def _apply_sort(self, stmt: Select, filters: FilterSchema) -> Select:
        if filters.sort == "price_asc":
            stmt = stmt.order_by(Product.price_cents.asc())
        elif filters.sort == "price_desc":
            stmt = stmt.order_by(Product.price_cents.desc())
        elif filters.sort == "newest":
            stmt = stmt.order_by(Product.created_at.desc())
        else:
            stmt = stmt.order_by(Product.updated_at.desc())
        return stmt

    async def search(self, filters: FilterSchema) -> tuple[Sequence[Product], int]:
        stmt = self._apply_sort(self._apply_filters(self._base_query(), filters), filters)
        total_stmt = select(func.count()).select_from(stmt.subquery())
        page = filters.page
        limit = filters.limit
        stmt = stmt.offset((page - 1) * limit).limit(limit)
        result = await self.session.execute(stmt)
        products = result.scalars().all()

        total_result = await self.session.execute(total_stmt)
        total = total_result.scalar_one()
        return products, total

    async def facets(self, filters: FilterSchema) -> dict[str, Any]:
        stmt = self._apply_filters(self._base_query(), filters)
        category_stmt = (
            select(Product.category, func.count(Product.id))
            .select_from(stmt.subquery())
            .group_by(Product.category)
        )
        color_stmt = (
            select(Product.color, func.count(Product.id))
            .select_from(stmt.subquery())
            .group_by(Product.color)
        )
        categories = (await self.session.execute(category_stmt)).all()
        colors = (await self.session.execute(color_stmt)).all()

        return {
            "categories": {category: count for category, count in categories},
            "colors": {color: count for color, count in colors},
        }

