from ai_recommend.domain.entity.user import User
from ai_recommend.domain.entity.product import Product
from datetime import datetime


class ViewedProduct:
    def __init__(self, user: User, product: Product, timestamp: datetime):
        self.user = user
        self.product = product
        self.timestamp = timestamp
