from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, conint, field_validator

from app.config import get_settings


settings = get_settings()


class FilterSchema(BaseModel):
    q: Optional[str] = Field(None, max_length=128)
    min_price: Optional[int] = Field(None, ge=0)
    max_price: Optional[int] = Field(None, ge=0)
    colors: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    page: conint(ge=1) = 1
    limit: conint(ge=1, le=settings.max_page_size) = settings.default_page_size
    sort: Literal["relevance", "price_asc", "price_desc", "newest"] = "relevance"

    @field_validator("max_price")
    @classmethod
    def validate_price_range(cls, v: Optional[int], info: dict) -> Optional[int]:
        min_price = info.data.get("min_price")
        if v is not None and min_price is not None and v < min_price:
            raise ValueError("max_price must be >= min_price")
        return v


class ProductHit(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str]
    category: str
    color: str
    price_cents: int
    currency: str
    stock_qty: int


class FacetCounts(BaseModel):
    categories: dict[str, int] = Field(default_factory=dict)
    colors: dict[str, int] = Field(default_factory=dict)


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    has_next: bool


class SearchResponse(BaseModel):
    filters: FilterSchema
    results: list[ProductHit]
    facets: FacetCounts
    pagination: PaginationMeta
    cached: bool = False

