from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database import get_db, PumpEvent as PumpEventRow
from models import PumpCommandIn, PumpEventOut

router = APIRouter(prefix="/pump", tags=["pump"])


@router.post("", response_model=PumpEventOut)
async def log_pump_event(payload: PumpCommandIn, db: AsyncSession = Depends(get_db)):
    row = PumpEventRow(
        duration_ms=payload.duration_ms,
        triggered_by=payload.triggered_by,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)

    return PumpEventOut(
        id=row.id,
        duration_ms=row.duration_ms,
        triggered_by=row.triggered_by,
        created_at=row.created_at,
    )


@router.get("", response_model=list[PumpEventOut])
async def get_pump_events(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PumpEventRow).order_by(desc(PumpEventRow.created_at)).limit(limit)
    )
    rows = result.scalars().all()
    return [
        PumpEventOut(
            id=r.id,
            duration_ms=r.duration_ms,
            triggered_by=r.triggered_by,
            created_at=r.created_at,
        )
        for r in rows
    ]
