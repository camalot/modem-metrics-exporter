import typing

from lib.datastores.datastore import DataStore


class NullDataStore(DataStore):
    def __init__(self):
        super().__init__()

        self.logger.debug("Initializing Null Data Store")

    def read(self, topic) -> typing.Any:
        return None

    def write(self, topic, data, ttl) -> bool:
        return True
