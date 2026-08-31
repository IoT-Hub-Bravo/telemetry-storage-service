import datetime as dt
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TypedDict, Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from db.models import Telemetry, TelemetryValueType
from dto import TelemetryIngestItem


@dataclass(slots=True)
class TelemetryInsertResult:
    created: int = 0  # new valid rows
    skipped: int = 0  # valid rows, already exist in db
    errors: dict[int, Any] = field(default_factory=dict)  # invalid rows


class TelemetryInsertRow(TypedDict):
    device_serial_id: str
    device_metric_id: int
    ts: dt.datetime
    value_type: TelemetryValueType
    value_numeric: float | int | None
    value_bool: bool | None
    value_str: str | None


def insert_telemetry_batch(
        *,
        db: Session,
        items: Sequence[TelemetryIngestItem],
) -> TelemetryInsertResult:
    result = TelemetryInsertResult()

    if not items:
        return result

    rows: list[TelemetryInsertRow] = []

    for i, item in enumerate(items):
        row, error = _to_insert_row(item)
        if error is not None:
            result.errors[i] = error
            continue
        rows.append(row)

    if not rows:
        return result

    query = (
        insert(Telemetry)
        .on_conflict_do_nothing(index_elements=['device_metric_id', 'ts'])
        .returning(Telemetry.device_metric_id, Telemetry.ts)
    )

    db_result = db.execute(query, rows)
    inserted_rows = db_result.fetchall()
    db.commit()

    result.created = len(inserted_rows)
    result.skipped = len(rows) - result.created

    return result


def _to_insert_row(
        item: TelemetryIngestItem,
) -> tuple[TelemetryInsertRow, None] | tuple[None, str]:
    try:
        value_type = TelemetryValueType(item['type'])
    except ValueError:
        return None, f'Unsupported telemetry value_type: {item["type"]}'

    value = item['value']

    row: TelemetryInsertRow = {
        'device_serial_id': item['device_serial_id'],
        'device_metric_id': item['device_metric_id'],
        'ts': item['ts'],
        'value_type': value_type,
        'value_numeric': None,
        'value_bool': None,
        'value_str': None,
    }

    if value_type is TelemetryValueType.NUMERIC:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None, 'numeric telemetry value must be int or float'
        row['value_numeric'] = float(value)

    elif value_type is TelemetryValueType.BOOLEAN:
        if not isinstance(value, bool):
            return None, 'boolean telemetry value must be bool'
        row['value_bool'] = value

    elif value_type is TelemetryValueType.STRING:
        if not isinstance(value, str):
            return None, 'string telemetry value must be str'
        row['value_str'] = value

    return row, None
