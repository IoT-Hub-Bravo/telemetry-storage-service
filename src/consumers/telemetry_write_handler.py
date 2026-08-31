from typing import Any
import logging

from sqlalchemy.orm import Session, sessionmaker

from serializers import TelemetryBatchSerializer
from services.telemetry import insert_telemetry_batch

logger = logging.getLogger(__name__)


class TelemetryWriteHandler:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

    def handle(self, payload: Any) -> None:
        if isinstance(payload, dict):
            payload = [payload]
        elif isinstance(payload, list):
            pass
        else:
            logger.error(f'payload must be of type dict or list, got {type(payload).__name__}')
            return

        s = TelemetryBatchSerializer(payload)

        if not s.is_valid() and not s.valid_items:  # no valid items exist
            logger.warning('Telemetry ingestion task rejected: errors=%s', len(s.errors))
            return

        with self.session_factory() as db:
            result = insert_telemetry_batch(db=db, items=s.valid_items)

        logger.info(
            'Telemetry batch processed: created=%s skipped=%s invalid=%s',
            result.created,
            result.skipped,
            len(result.errors),
        )

        if result.errors:
            logger.warning('Telemetry batch item errors: %s', result.errors)
