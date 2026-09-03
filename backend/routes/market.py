import logging

from fastapi import APIRouter, HTTPException, Query

from backend.services.mandi_market import SUPPORTED_COMMODITIES, get_mandi_prices

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/market", tags=["Market"])


@router.get("/mandi-prices")
async def mandi_prices(
    commodity: str | None = Query(default=None),
    state: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
):
    if commodity and commodity not in SUPPORTED_COMMODITIES:
        raise HTTPException(
            status_code=400,
            detail=f"commodity must be one of: {', '.join(SUPPORTED_COMMODITIES)}",
        )
    try:
        return get_mandi_prices(commodity=commodity, state=state, limit=limit)
    except RuntimeError as exc:
        logger.error("Mandi configuration error: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Mandi market feed is not configured",
        ) from exc
    except Exception:
        logger.exception("Mandi market feed failed")
        raise HTTPException(
            status_code=502,
            detail="Mandi market feed temporarily unavailable",
        )
