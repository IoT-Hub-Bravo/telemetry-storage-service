import datetime as dt
from enum import Enum
from typing import Optional

from sqlalchemy import (
    String,
    DateTime,
    BigInteger,
    Enum as SAEnum,
    Float,
    Boolean,
    Text,
    PrimaryKeyConstraint,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from db import Base


class TelemetryValueType(str, Enum):
    NUMERIC = 'numeric'
    STRING = 'string'
    BOOLEAN = 'boolean'


class Telemetry(Base):
    __tablename__ = 'telemetries'
    __table_args__ = (
        PrimaryKeyConstraint(
            'device_metric_id',
            'ts',
            name='pk_telemetries',
        ),
        CheckConstraint(
            """
            (
                value_type = 'numeric'
                AND value_numeric IS NOT NULL
                AND value_bool IS NULL
                AND value_str IS NULL
            )
            OR
            (
                value_type = 'boolean'
                AND value_numeric IS NULL
                AND value_bool IS NOT NULL
                AND value_str IS NULL
            )
            OR
            (
                value_type = 'string'
                AND value_numeric IS NULL
                AND value_bool IS NULL
                AND value_str IS NOT NULL
            )
            """,
            name='ck_telemetries_exactly_one_value',
        ),
        Index(
            'ix_telemetries_device_serial_ts',
            'device_serial_id',
            'ts',
        ),
    )

    device_serial_id: Mapped[str] = mapped_column(String(255))
    device_metric_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ts: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    value_type: Mapped[TelemetryValueType] = mapped_column(
        SAEnum(
            TelemetryValueType,
            name='telemetry_value_type',
            native_enum=False,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
    )
    value_numeric: Mapped[Optional[float | int]] = mapped_column(Float(16))
    value_bool: Mapped[Optional[bool]] = mapped_column(Boolean)
    value_str: Mapped[Optional[str]] = mapped_column(Text)

    @property
    def value(self) -> float | bool | str | None:
        if self.value_numeric is not None:
            return self.value_numeric
        if self.value_bool is not None:
            return self.value_bool
        if self.value_str is not None:
            return self.value_str
        return None

    def set_typed_value(
            self,
            *,
            value: float | int | bool | str,
            value_type: TelemetryValueType,
    ) -> None:
        self.value_numeric = None
        self.value_bool = None
        self.value_str = None

        if value_type is TelemetryValueType.NUMERIC:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError('numeric telemetry value must be int or float')
            self.value_numeric = float(value)

        elif value_type is TelemetryValueType.BOOLEAN:
            if not isinstance(value, bool):
                raise ValueError('boolean telemetry value must be bool')
            self.value_bool = value

        elif value_type is TelemetryValueType.STRING:
            if not isinstance(value, str):
                raise ValueError('string telemetry value must be str')
            self.value_str = value

        else:
            raise ValueError(f'Unsupported telemetry value type: {value_type}')

        self.value_type = value_type
