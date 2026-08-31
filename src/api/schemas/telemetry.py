from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

TelemetryValueType = Literal['numeric', 'boolean', 'string']


class TelemetryResponse(BaseModel):
    device_serial_id: str
    device_metric_id: int
    ts: datetime
    value_type: TelemetryValueType
    value: float | bool | str


class TelemetryListResponse(BaseModel):
    items: list[TelemetryResponse]
    total: int


class DeviceTelemetryQueryParams(BaseModel):
    device_metric_id: int | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = Field(default=100, ge=1, le=5000)
