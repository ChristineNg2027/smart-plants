from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReadingIn(BaseModel):
    moisture: float = Field(..., ge=0, le=100, description="Soil moisture %")
    temperature: float = Field(..., description="Temperature °C")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity %")
    light: Optional[float] = Field(None, ge=0, description="Light level (lux)")
    timestamp: Optional[int] = Field(None, description="Device millis — ignored if None")


class ReadingOut(BaseModel):
    id: int
    moisture: float
    temperature: float
    humidity: float
    light: Optional[float]
    created_at: datetime
    water: bool = False


class PredictionOut(BaseModel):
    forecast: list[float]
    horizon_hours: int
    dry_threshold: float
    predicted_dry_at_hours: Optional[float]


class PumpCommandIn(BaseModel):
    duration_ms: int = Field(3000, ge=500, le=30000)
    triggered_by: str = Field("manual", description="'manual' | 'model' | 'emergency'")


class PumpEventOut(BaseModel):
    id: int
    duration_ms: int
    triggered_by: str
    created_at: datetime
