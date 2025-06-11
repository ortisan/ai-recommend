class DatabaseConfig:
    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        namespace: str,
        database: str,
    ):
        self.url = url
        self.username = username
        self.password = password
        self.namespace = namespace
        self.database = database  

        
        
    