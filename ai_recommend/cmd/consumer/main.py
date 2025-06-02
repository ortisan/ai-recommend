from ai_recommend.adapter.input.e_commerce.e_commerce_events_consumer import ECommerceEventsConsumer
from ai_recommend.cmd.consumer.containers import CmdContainer
from dependency_injector.wiring import Provide, inject

def main(consumer: ECommerceEventsConsumer = Provide[CmdContainer.e_commerce_events_consumer]):
    """
    Main function to start the ECommerceEventsConsumer.
    """
    msg = consumer.consume()
    if msg:
        print(f"Consumed message: {msg.value}")
    else:
        print("No messages consumed.")


if __name__ == "__main__":
    container = CmdContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    main()
