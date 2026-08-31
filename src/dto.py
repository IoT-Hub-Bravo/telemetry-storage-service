import datetime as dt
from typing import TypedDict

ValueType = int | float | bool | str


class TelemetryIngestItem(TypedDict):
    device_serial_id: str
    device_metric_id: int
    ts: dt.datetime
    type: str
    value: ValueType
