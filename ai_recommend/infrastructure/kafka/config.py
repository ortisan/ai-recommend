class KafkaConsumerConfig:
    """Configuration for Kafka consumer."""

    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        auto_offset_reset: str,
        schema_registry_url: str,
        topic: str,
        poll_timeout: float,
        enable_auto_commit: bool = True,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset
        self.schema_registry_url = schema_registry_url
        self.topic = topic
        self.poll_timeout = poll_timeout
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
