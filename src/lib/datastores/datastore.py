import typing

from config import ApplicationConfiguration
from lib.logging import setup_logging


class DataStore:
    def __init__(self):
        config = ApplicationConfiguration
        self.logger = setup_logging(self.__class__.__name__, config.logging)

    def read(self, topic: str) -> typing.Any:
        return None

    def write(self, topic: str, data: dict, ttl: int) -> bool:
        return False
