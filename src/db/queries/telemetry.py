from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Telemetry


async def get_device_telemetry(
        *,
        db: AsyncSession,
        device_serial_id: str,
        device_metric_id: int | None = None,
        date_from=None,
        date_to=None,
        limit: int = 100,
) -> list[Telemetry]:
    query = (
        select(Telemetry)
        .where(Telemetry.device_serial_id == device_serial_id)
        .order_by(Telemetry.ts.desc())
        .limit(limit)
    )

    if device_metric_id is not None:
        query = query.where(Telemetry.device_metric_id == device_metric_id)

    if date_from is not None:
        query = query.where(Telemetry.ts >= date_from)

    if date_to is not None:
        query = query.where(Telemetry.ts <= date_to)

    result = await db.execute(query)
    return list(result.scalars().all())
