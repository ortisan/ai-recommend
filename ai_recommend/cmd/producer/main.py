from ai_recommend.adapter.output.e_commerce.e_commerce_events_producer import ECommerceEventsProducer
from ai_recommend.adapter.stub import e_commerce_events_pb2
from ai_recommend.cmd.producer.containers import CmdContainer
from dependency_injector.wiring import Provide, inject
from uuid import uuid4
from google.protobuf.timestamp_pb2 import Timestamp


def main(producer: ECommerceEventsProducer = Provide[CmdContainer.e_commerce_events_producer]):
    """
    Main function to start the ECommerceEventsProducer.
    """

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

    result = producer.produce(e_commerce_event)
    if result:
        print(f"Produced message: {result}")
    else:
        print("Failed to produce message.")


if __name__ == "__main__":
    container = CmdContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    main()
