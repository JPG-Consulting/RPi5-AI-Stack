from fastapi import APIRouter
from ai_api.observability.metrics import metrics

router = APIRouter()

@router.get("/metrics")
def get_metrics():
    return metrics.snapshot()
