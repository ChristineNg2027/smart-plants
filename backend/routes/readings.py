from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database import get_db, Reading as ReadingRow
from models import ReadingIn, ReadingOut

router = APIRouter(prefix="/readings", tags=["readings"])

DRY_THRESHOLD = 30.0  # % — water immediately if below this


@router.post("", response_model=ReadingOut)
async def ingest_reading(payload: ReadingIn, db: AsyncSession = Depends(get_db)):
    row = ReadingRow(
        moisture=payload.moisture,
        temperature=payload.temperature,
        humidity=payload.humidity,
        light=payload.light,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)

    should_water = payload.moisture < DRY_THRESHOLD

    return ReadingOut(
        id=row.id,
        moisture=row.moisture,
        temperature=row.temperature,
        humidity=row.humidity,
        light=row.light,
        created_at=row.created_at,
        water=should_water,
    )


@router.get("", response_model=list[ReadingOut])
async def get_readings(limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ReadingRow).order_by(desc(ReadingRow.created_at)).limit(limit)
    )
    rows = result.scalars().all()
    return [
        ReadingOut(
            id=r.id,
            moisture=r.moisture,
            temperature=r.temperature,
            humidity=r.humidity,
            light=r.light,
            created_at=r.created_at,
        )
        for r in rows
    ]
