from opentelemetry.metrics import (
    get_meter_provider,
    set_meter_provider,
    UpDownCounter as UpDownCounterOtel,
    Counter as CounterOtel,
    Histogram as HistogramOtel,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)


class Meter:
    def __init__(self, appName: str, appVersion: str):
        exporter = OTLPMetricExporter(insecure=True)
        reader = PeriodicExportingMetricReader(exporter)
        provider = MeterProvider(metric_readers=[reader])
        set_meter_provider(provider)
        self.meter = get_meter_provider().get_meter(appName, appVersion)

    def create_counter(self, name: str, description: str = "", unit: str = "1") -> CounterOtel:
        """
        Create a counter metric.
        :param name: Name of the metric.
        :param description: Description of the metric.
        :param unit: Unit of the metric.
        :return: A counter metric.
        """
        return self.meter.create_counter(name, description=description, unit=unit)

    def create_up_down_counter(
        self, name: str, description: str = "", unit: str = "1"
    ) -> UpDownCounterOtel:
        """
        Create an up-down counter metric.
        :param name: Name of the metric.
        :param description: Description of the metric.
        :param unit: Unit of the metric.
        :return: An up-down counter metric.
        """
        return self.meter.create_up_down_counter(name, description=description, unit=unit)

    def create_histogram(self, name: str, description: str = "", unit: str = "1") -> HistogramOtel:
        """
        Create a histogram metric.
        :param name: Name of the metric.
        :param description: Description of the metric.
        :param unit: Unit of the metric.
        :return: A histogram metric.
        """
        return self.meter.create_histogram(name, description=description, unit=unit)
