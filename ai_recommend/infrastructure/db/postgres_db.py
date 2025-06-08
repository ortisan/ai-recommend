from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ai_recommend.infrastructure.db.config import DatabaseConfig


class PostgresDb:
    def __init__(self, config: DatabaseConfig):
        self.config = config

        self.engine = create_engine(
            f"postgresql+psycopg://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"
        )

    def __get_connection__(self):
        return self.engine.connect()

    def __get_session__(self):
        return Session(self.engine)

    @contextmanager
    def get_session(self):
        """Context manager for automatic session management

        Yields:
            SQLAlchemy Session

        Automatically closes session on exit (success or exception)
        """
        session = self.__get_session__()
        try:
            yield session
        finally:
            session.close()

    @contextmanager
    def get_connection(self):
        """Context manager for automatic connection management

        Yields:
            SQLAlchemy Session

        Automatically closes connection on exit (success or exception)
        """
        connection = self.__get_connection__()
        try:
            yield connection
        finally:
            connection.close()

    def execute_query(self, query):
        with self.connection() as conn:
            result = conn.execute(query)
            return result.fetchall()
