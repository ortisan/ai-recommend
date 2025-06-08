# from ai_recommend.adapter.output.e_commerce.e_commerce_events_producer import ECommerceEventsProducer
# from ai_recommend.adapter.stub import e_commerce_events_pb2
# from ai_recommend.cmd.producer.containers import CmdContainer
# from dependency_injector.wiring import Provide, inject
# from uuid import uuid4
# from google.protobuf.timestamp_pb2 import Timestamp
#
#
# def main(producer: ECommerceEventsProducer = Provide[CmdContainer.e_commerce_events_producer]):
#     """
#     Main function to start the ECommerceEventsProducer.
#     """
#
#     timestamp = Timestamp()
#
#     user = e_commerce_events_pb2.User(
#         id: str(uuid4()),
#         email: "teste@teste.com",
#         name: "Marcelo Ortiz de Santana",
#     )
#
#     product = e_commerce_events_pb2.Product(
#         sku: str(uuid4()),
#         name: "Iphone 16",
#         description: "Smartphone Iphone 16",
#         price: 10000.0,
#         category: "Eletronics",
#     )
#
#     product_viewed_event = e_commerce_events_pb2.ProductViewEvent(
#         user: user,
#         product: product,
#         timestamp: timestamp
#     )
#     e_commerce_event = e_commerce_events_pb2.ECommerceEvent(
#         product_view=product_viewed_event
#     )
#
#     result = producer.produce(e_commerce_event)
#     if result:
#         print(f"Produced message: {result}")
#     else:
#         print("Failed to produce message.")
#
#
# if __name__ == "__main__":
#     container = CmdContainer()
#     container.init_resources()
#     container.wire(modules=[__name__])
#     main()
