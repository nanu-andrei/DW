import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from interfaces.api.middleware.error_handler import ErrorHandlerMiddleware
from interfaces.api.routers import assets, data_sources, data, ingestion, analytics
from infrastructure.adapters.cassandra.session import shutdown_cassandra
from infrastructure.adapters.cassandra.schema import initialize_schema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Nanu Financial Data Warehouse starting up...")
    try:
        initialize_schema()
        logger.info("Cassandra schema initialized")
    except Exception as e:
        logger.warning(f"Could not initialize schema (Cassandra may not be ready): {e}")
    yield
    logger.info("Shutting down...")
    shutdown_cassandra()


app = FastAPI(
    title="Nanu Financial Data Warehouse",
    description="Acme Ltd Financial Data Warehouse API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handler
app.add_middleware(ErrorHandlerMiddleware)

# Routers
app.include_router(assets.router)
app.include_router(data_sources.router)
app.include_router(data.router)
app.include_router(ingestion.router)
app.include_router(analytics.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
