from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    host: str
    port: str = Field(pattern=r"^[0-9]+$")
    username: str
    password: str
    database: str
