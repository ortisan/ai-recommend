from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer

import ai_recommend.adapter.stub.e_commerce_events_pb2 as ecommerce_events_pb2
from ai_recommend.infrastructure.kafka.config import KafkaConsumerConfig
from ai_recommend.infrastructure.observability.logger.logger import ILogger
from confluent_kafka.serialization import SerializationContext, MessageField


class ECommerceEventsConsumer:
    def __init__(self, config: KafkaConsumerConfig, logger: ILogger):
        self.config = config
        self.logger = logger
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the Kafka consumer and schema registry client."""
        # Create schema registry client
        schema_registry_conf = {"url": self.config.schema_registry_url}
        self.schema_registry_client = SchemaRegistryClient(schema_registry_conf)

        # Create Protobuf deserializer
        self.protobuf_deserializer = ProtobufDeserializer(
            ecommerce_events_pb2.ECommerceEvent,
            {"use.deprecated.format": False},
        )

        # Create Kafka consumer
        consumer_conf = {
            "bootstrap.servers": self.config.bootstrap_servers,
            "group.id": self.config.consumer_group,
            "auto.offset.reset": self.config.auto_offset_reset,
            "enable.auto.commit": self.config.enable_auto_commit,
        }
        self.consumer = Consumer(consumer_conf)
        self.consumer.subscribe([self.config.topic])

        self.logger.log(f"Initialized Ecomerce for topic {self.config.topic}")

    def consume(self):
        """
        Consume events from the Kafka topic and handle them using the provided handler.
        """
        try:
            while True:
                # Poll for new messages
                msg = self.consumer.poll(self.config.poll_timeout)
                if msg is None:
                    continue

                # Deserialize the message
                event = self.protobuf_deserializer(msg.value(), SerializationContext(self.config.topic, MessageField.VALUE))
                if event is None:
                    continue

                # Handle the event
                self.handle_event(event)

        except Exception as e:
            self.logger.error(f"Failed to consume event: {e}")
        finally:
            self.consumer.close()

    def handle_event(self, event):
        """
        Handle the consumed event.
        This method should be overridden by subclasses to implement specific event handling logic.
        """
        self.logger.log(f"Received event: {event}")
        # Implement specific event handling logic here
        # For example, you can process the event and store it in a database or perform some action based on the event type
