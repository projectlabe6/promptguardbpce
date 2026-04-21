from fastapi import UploadFile

from app.schemas.ingestion import IngestedContent


async def ingest_file(file: UploadFile) -> IngestedContent:
    raise NotImplementedError
