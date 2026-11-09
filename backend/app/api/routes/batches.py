from fastapi import APIRouter, status

from app.api.deps import GroqKeyDep, ServicesDep
from app.schemas.batch import BatchJob, BatchRequest

router = APIRouter(prefix="/batches", tags=["batches"])


@router.post("", response_model=BatchJob, status_code=status.HTTP_202_ACCEPTED)
def create_batch(req: BatchRequest, services: ServicesDep, api_key: GroqKeyDep) -> BatchJob:
    return services.batches.submit(req, api_key)


@router.get("/{job_id}", response_model=BatchJob)
def get_batch(job_id: str, services: ServicesDep) -> BatchJob:
    return services.batches.get(job_id)
