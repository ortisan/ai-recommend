class KafkaConsumerConfig:
    """Configuration for Kafka consumer."""

    def __init__(
        self,
        bootstrap_servers: str,
        consumer_group: str,
        auto_offset_reset: str,
        schema_registry_url: str,
        topic: str,
        poll_timeout_ms: float,
        enable_auto_commit: bool = True,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.consumer_group = consumer_group
        self.auto_offset_reset = auto_offset_reset
        self.schema_registry_url = schema_registry_url
        self.topic = topic
        self.poll_timeout = poll_timeout_ms
        self.enable_auto_commit = enable_auto_commit


class KafkaProducerConfig:
    """Configuration for Kafka consumer."""

    def __init__(
        self,
        bootstrap_servers: str,
        schema_registry_url: str,
        topic: str,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.schema_registry_url = schema_registry_url
        self.topic = topic
