from fastapi import APIRouter

router = APIRouter(
    prefix="/api",
    tags=["Health"],
)


@router.get("/health")
def health():
    return {
        "status": "UP",
        "service": "RUSI Trader AI Backend",
        "version": "1.0.0",
    }
