from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.pipeline.run_pipeline import run_pipeline
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
