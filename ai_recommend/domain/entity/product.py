from ai_recommend.domain.entity.product_category import ProductCategory


class Product:
    def __init__(self, id: str, name: str, category: ProductCategory):
        self.sku = id
        self.name = name
        self.category = category
