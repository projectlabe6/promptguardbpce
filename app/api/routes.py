import json

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_weights, update_weights
from app.pipeline.evaluator import evaluate_dataset
from app.pipeline.ingestion import ingest_file
from app.pipeline.run_pipeline import run_pipeline
from app.schemas.config import WeightsUpdate
from app.schemas.evaluation import EvalCase, EvalResult
from app.schemas.sanitize import SanitizeRequest, SanitizeResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/sanitize", response_model=SanitizeResponse)
async def sanitize(request: SanitizeRequest):
    try:
        return run_pipeline(request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sanitize-file", response_model=SanitizeResponse)
async def sanitize_file(file: UploadFile = File(...)):
    try:
        ingested = await ingest_file(file)
        return run_pipeline(ingested.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate", response_model=EvalResult)
async def evaluate(file: UploadFile = File(...)):
    try:
        content = await file.read()
        cases = [EvalCase(**c) for c in json.loads(content)]
        return evaluate_dataset(cases)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Fichier JSON invalide")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/weights")
async def get_config_weights():
    return get_weights()


@router.post("/config/weights")
async def update_config_weights(payload: WeightsUpdate):
    update_weights(payload.weights)
    return {"message": "Poids mis à jour"}
