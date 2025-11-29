from fastapi import FastAPI
from structlog import get_logger

from app.api.routes import search

log = get_logger()

app = FastAPI(title="Product Search API", version="0.1.0")


@app.on_event("startup")
async def on_startup() -> None:
    log.info("api.startup")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    log.info("api.shutdown")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(search.router)

