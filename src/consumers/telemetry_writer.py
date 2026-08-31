import logging
import signal

from decouple import config
from iot_hub_shared.kafka_kit import KafkaConsumer
from iot_hub_shared.kafka_kit import ConsumerConfig

from db import get_db_settings, create_sync_db_engine, create_sync_session_factory
from utils.logging import setup_logging
from consumers.telemetry_write_handler import TelemetryWriteHandler

CLEAN_TOPIC = config('KAFKA_TOPIC_TELEMETRY_CLEAN', default='telemetry.clean')
EXPIRED_TOPIC = config('KAFKA_TOPIC_TELEMETRY_EXPIRED', default='telemetry.expired')
CONSUME_TIMEOUT = config('KAFKA_CONSUMER_CONSUME_TIMEOUT', default=1.0, cast=float)
DECODE_JSON = config('KAFKA_CONSUMER_DECODE_JSON', default=True, cast=bool)
CONSUME_BATCH = config('KAFKA_CONSUMER_CONSUME_BATCH', default=True, cast=bool)
BATCH_MAX_SIZE = config('KAFKA_CONSUMER_BATCH_MAX_SIZE', default=100, cast=int)

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()

    settings = get_db_settings()
    engine = create_sync_db_engine(settings)
    session_factory = create_sync_session_factory(engine)

    consumer = KafkaConsumer(
        config=ConsumerConfig(),
        topics=[CLEAN_TOPIC, EXPIRED_TOPIC],
        handler=TelemetryWriteHandler(session_factory=session_factory),
        consume_timeout=CONSUME_TIMEOUT,
        decode_json=DECODE_JSON,
        consume_batch=CONSUME_BATCH,
        batch_max_size=BATCH_MAX_SIZE,
    )

    def _stop(*_) -> None:
        consumer.stop()
        engine.dispose()

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    consumer.start()


if __name__ == '__main__':
    main()
