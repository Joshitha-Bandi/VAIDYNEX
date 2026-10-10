from fastapi import APIRouter
from ..models.schemas import CoverageEligibilityCheckRequest, CoverageEligibilityResponse
from ..services.abdm_service import abdm_service

router = APIRouter(prefix="/insurance", tags=["NHCX Insurance"])

@router.post("/coverage-eligibility/check", response_model=CoverageEligibilityResponse)
async def check_insurance(req: CoverageEligibilityCheckRequest):
    return abdm_service.check_coverage_eligibility(req.abha_number)
