import datetime as dt
from typing import Any, Optional

from iot_hub_shared.serializer_kit import JSONSerializer, BaseSerializer
from iot_hub_shared.utils_kit import normalize_str, parse_iso8601_utc

from dto import TelemetryIngestItem

ValueType = int | float | bool | str


class TelemetrySerializer(JSONSerializer):
    REQUIRED_FIELDS = {
        'device_serial_id': str,
        'device_metric_id': int,
        'ts': str,
        'type': str,
        'value': ValueType,
    }

    def _validate_fields(self, data: dict[str, Any]) -> Optional[TelemetryIngestItem]:
        device_serial_id = normalize_str(data['device_serial_id'])
        if device_serial_id is None:
            self._errors['device_serial_id'] = 'device_serial_id must be a non-empty field.'

        value_type = normalize_str(data['type'])
        if value_type is None:
            self._errors['type'] = 'type must be a non-empty field.'

        value = self._validate_value(data['value'])
        if value is None:
            self._errors['value'] = 'value must be a non-empty field.'

        ts = self._validate_ts(data['ts'])

        if self._errors:
            return None

        return TelemetryIngestItem(
            device_serial_id=device_serial_id,
            device_metric_id=data['device_metric_id'],
            ts=ts,
            type=value_type,
            value=value,
        )

    @staticmethod
    def _validate_value(value_raw: ValueType) -> Optional[ValueType]:
        if value_raw is None:
            return None
        if isinstance(value_raw, bool):
            return value_raw
        if isinstance(value_raw, (int, float)):
            return value_raw
        if isinstance(value_raw, str):
            return normalize_str(value_raw)
        return None

    def _validate_ts(self, ts_raw: Optional[str]) -> Optional[dt.datetime]:
        if ts_raw is None:
            return None

        ts = parse_iso8601_utc(ts_raw)
        if ts is None:
            self._errors['ts'] = 'ts must be a valid ISO-8601 datetime.'
            return None

        return ts


class TelemetryBatchSerializer(BaseSerializer):
    def __init__(self, data: Any):
        super().__init__(data)
        self._valid_items: list[TelemetryIngestItem] = []
        self._item_errors: dict[int, Any] = {}

    @property
    def valid_items(self) -> list[TelemetryIngestItem]:
        return self._valid_items

    @property
    def item_errors(self) -> dict[int, Any]:
        return self._item_errors

    def _validate(self, data: Any) -> Optional[list[TelemetryIngestItem]]:
        if not isinstance(data, list):
            self._errors['non_field_errors'] = 'Payload must be a JSON array.'
            return None

        if not data:
            self._errors['items'] = {'non_field_errors': 'Empty batch.'}
            return None

        for index, item in enumerate(data):
            s = TelemetrySerializer(item)
            if s.is_valid():
                self._valid_items.append(s.validated_data)
            else:
                self._item_errors[index] = s.errors

        if self._item_errors:
            self._errors['items'] = self._item_errors
            return None

        return self._valid_items
