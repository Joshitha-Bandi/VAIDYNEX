from fastapi import APIRouter
from ..models.schemas import OCRRequest, OCRResponse
from ..services.ai_service import ai_service

router = APIRouter(prefix="/documents", tags=["Documents OCR"])

@router.post("/ocr", response_model=OCRResponse)
async def process_ocr(req: OCRRequest):
    return ai_service.extract_document_ocr(req.encounter_id, req.document_type)
