from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.pipeline.ner_medical import _load_medical_model
from app.pipeline.ner_pii import _load_pii_pipeline


@asynccontextmanager
async def lifespan(app):
    _load_pii_pipeline()
    _load_medical_model()
    yield


app = FastAPI(
    title="PromptGuard",
    description="Microservice de désensibilisation de prompts",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)
