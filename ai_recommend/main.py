from uuid import uuid4

from google.protobuf.timestamp_pb2 import Timestamp

import ai_recommend.adapter.stub.e_commerce_events_pb2 as e_commerce_events_pb2
from ai_recommend.adapter.input.ecomerce.e_commerce_events_consumer import ECommerceEventsConsumer
from ai_recommend.adapter.output.ecomerce.e_commerce_events_producer import (
    ECommerceEventsProducer,
)
from ai_recommend.infrastructure.kafka.config import KafkaProducerConfig, KafkaConsumerConfig
from ai_recommend.infrastructure.observability.logger.loguru.loguru import (
    Loguru,
)

topic = "e-commerce-events"

if __name__ == "__main__":
    logger = Loguru()
    logger.log("AI Recommendation System is starting...")

    producer_config = KafkaProducerConfig(
        bootstrap_servers="localhost:9092",
        topic=topic,
        schema_registry_url="http://localhost:8081",
    )

    timestamp = Timestamp()

    base_event = e_commerce_events_pb2.BaseEvent(
        event_id=str(uuid4()),
        user_id=str(uuid4()),
        session_id=str(uuid4()),
        timestamp=timestamp,
        device_type="web",
        ip_address="127.0.0.1",
    )

    product_viewed_event = e_commerce_events_pb2.ProductViewEvent(
        base=base_event,
        product_sku="sku_12345",
        view_duration_seconds=30,
        referrer_url="teste.com",
        page_url="teste.com/product/12345",
    )
    e_commerce_event = e_commerce_events_pb2.ECommerceEvent(
        product_view=product_viewed_event
    )

    producer = ECommerceEventsProducer(config=producer_config, logger=logger)
    producer.produce(message=e_commerce_event)


    consumer_config = KafkaConsumerConfig(
        bootstrap_servers="localhost:9092",
        group_id="main_group",
        auto_offset_reset="earliest",
        schema_registry_url="http://localhost:8081",
        topic=topic,
        poll_timeout=1.0,
        enable_auto_commit=True,
    )
    consumer = ECommerceEventsConsumer(config=consumer_config, logger=logger)
    consumer.consume()