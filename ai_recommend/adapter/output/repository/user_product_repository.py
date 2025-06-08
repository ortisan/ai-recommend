# from ai_recommend.infrastructure.db.surreal_db import SurrealDb
from ai_recommend.domain.entity.viewed_product import ViewedProduct


class RelationshipRepository:
    def __init__(self, db: SurrealDb):
        self.db = db.db

    def upsert(self, table: str, data: dict):
        pass

    # def viewed(self, viewed_product: ViewedProduct):
    #     user_record = self.db.upsert(
    #         "user",
    #         {
    #             "id": viewed_product.user.id,
    #             "name": viewed_product.user.name,
    #             "email": viewed_product.user.email,
    #         },
    #     )
    #
    #     product_record = self.db.upsert(
    #         "product", {
    #             "sku": viewed_product.product.sku,
    #             "name": viewed_product.product.name,
    #             "timestamp": viewed_product.timestamp,
    #         }
    #     )
    #
    #     view_relation = self.db.insert_relation("viewed", {
    #         "in": user_record['id'],
    #         "out": product_record['id'],
    #         "params": {
    #             "timestamp": view_relation.timestamp
    #         }
    #     })
