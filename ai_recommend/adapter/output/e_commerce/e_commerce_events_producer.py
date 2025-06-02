from uuid import uuid4

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    StringSerializer,
)

import ai_recommend.adapter.stub.e_commerce_events_pb2 as e_commerce_events_pb2
from ai_recommend.infrastructure.kafka.config import KafkaProducerConfig
from ai_recommend.infrastructure.observability.logger.logger import Logger


class ECommerceEventsProducer:
    """
    EcomerceEventsProducer is responsible for producing events to a Kafka topic.
    """

    def __init__(self, config: KafkaProducerConfig, logger: Logger):
        self.config = config
        self.logger = logger

        self._initialize()

    def _initialize(self) -> None:
        """Initialize the Kafka consumer and schema registry client."""

        schema_registry_conf = {"url": self.config.schema_registry_url}
        self.schema_registry_client = SchemaRegistryClient(schema_registry_conf)

        self.string_serializer = StringSerializer("utf8")

        self.protobuf_serializer = ProtobufSerializer(
            e_commerce_events_pb2.ECommerceEvent,
            self.schema_registry_client,
            {"use.deprecated.format": False},
        )

        # Create Kafka producer
        producer_conf = {
            "bootstrap.servers": self.config.bootstrap_servers,
        }
        self.producer = Producer(producer_conf)

    def produce(self, message: e_commerce_events_pb2.ECommerceEvent):
        """
        Consume events from the Kafka topic and handle them using the provided handler.
        """

        try:
            self.producer.produce(
                topic=self.config.topic,
                partition=0,
                key=self.string_serializer(str(uuid4())),
                value=self.protobuf_serializer(
                    message,
                    SerializationContext(self.config.topic, MessageField.VALUE),
                ),
                on_delivery=self.delivery_report,
            )
            self.producer.flush()
            self.logger.log(
                f"Produced message to topic {self.config.topic}: {message}"
            )

        except Exception as e:
            self.logger.error(f"Failed to produce message: {e}")

    def delivery_report(self, err, msg):
        """
        Reports the failure or success of a message delivery.

        Args:
            err (KafkaError): The error that occurred on None on success.
            msg (Message): The message that was produced or failed.
        """

        if err is not None:
            print(
                f"Delivery failed for message record {msg.key()}: {err}"
            )
            return
        print(
            f"User record {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
        )
