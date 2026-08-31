from datetime import datetime

from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from api.schemas.telemetry import TelemetryListResponse, TelemetryResponse
from db.models import Telemetry
from db.queries.telemetry import get_device_telemetry

router = APIRouter(prefix='/telemetry', tags=['telemetry'])


@router.get(
    '/{device_serial_id}/',
    response_model=TelemetryListResponse,
)
async def device_telemetry(
        device_serial_id: str,
        device_metric_id: int | None = Query(default=None),
        date_from: datetime | None = Query(default=None),
        date_to: datetime | None = Query(default=None),
        limit: int = Query(default=100, ge=1, le=5000),
        db: AsyncSession = Depends(get_db),
):
    items = await get_device_telemetry(
        db=db,
        device_serial_id=device_serial_id,
        device_metric_id=device_metric_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )

    response_items = [to_telemetry_response(item) for item in items]

    return TelemetryListResponse(
        items=response_items,
        total=len(response_items),
    )


def to_telemetry_response(model: Telemetry) -> TelemetryResponse:
    return TelemetryResponse(
        device_serial_id=model.device_serial_id,
        device_metric_id=model.device_metric_id,
        ts=model.ts,
        value_type=model.value_type.value,
        value=model.value,
    )
