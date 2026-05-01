import logging
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI

from config import get_settings
from database import engine, Base
from routers import health, webhooks_vapi

settings = get_settings()

if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1)

logging.basicConfig(
    level=logging.INFO if settings.APP_ENV == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Project Sole backend starting up")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    logger.info("Project Sole backend shutting down")


app = FastAPI(
    title="Project Sole",
    description="AI-Powered Customer Support Agent for Indian D2C Brands",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(webhooks_vapi.router)
