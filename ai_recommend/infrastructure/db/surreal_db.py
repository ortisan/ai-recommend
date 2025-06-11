from ai_recommend.infrastructure.db.config import DatabaseConfig
from surrealdb import Surreal

class SurrealDb:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.db = Surreal(config.url)
        self.db.signin({"username": self.config.username, "password": self.config.password})
        self.db.use(self.config.namespace, self.config.database)


