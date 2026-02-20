from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database import get_db, Prediction as PredictionRow
from models import PredictionOut
import json

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/latest", response_model=PredictionOut)
async def get_latest_prediction(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PredictionRow).order_by(desc(PredictionRow.created_at)).limit(1)
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="No predictions available yet")

    return PredictionOut(
        forecast=json.loads(row.forecast_json),
        horizon_hours=row.horizon_hours,
        dry_threshold=30.0,
        predicted_dry_at_hours=row.predicted_dry_at_hours,
    )


@router.get("", response_model=list[PredictionOut])
async def get_predictions(limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PredictionRow).order_by(desc(PredictionRow.created_at)).limit(limit)
    )
    rows = result.scalars().all()
    return [
        PredictionOut(
            forecast=json.loads(r.forecast_json),
            horizon_hours=r.horizon_hours,
            dry_threshold=30.0,
            predicted_dry_at_hours=r.predicted_dry_at_hours,
        )
        for r in rows
    ]
