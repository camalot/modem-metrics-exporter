from config import ApplicationConfiguration
from lib.enums.DataStoreTypes import DataStoreTypes
from lib.logging import setup_logging


class DatastoreFactory:
    def __init__(self):
        pass

    def create(self, type: DataStoreTypes):
        config = ApplicationConfiguration
        logger = setup_logging(self.__class__.__name__, config.logging)
        if type == DataStoreTypes.REDIS:
            logger.debug("Creating Redis Datastore")
            from lib.datastores.redis import RedisDataStore

            return RedisDataStore()
        elif type == DataStoreTypes.FILE:
            logger.debug("Creating File Datastore")
            from lib.datastores.file import FileDataStore

            return FileDataStore()
        elif type == DataStoreTypes.MQTT:
            logger.debug("Creating MQTT Datastore")
            from lib.datastores.mqtt import MqttDataStore

            return MqttDataStore()
        elif type == DataStoreTypes.MONGODB:
            logger.debug("Creating MongoDB Datastore")
            from lib.datastores.mongodb import MongoDBDatastore

            return MongoDBDatastore()
        elif type == DataStoreTypes.HTTP:
            logger.debug("Creating HTTP Datastore")
            from lib.datastores.http import HttpDataStore

            return HttpDataStore()
        elif type == DataStoreTypes.NONE:
            logger.debug("Creating Null Datastore")
            from lib.datastores.null import NullDataStore

            return NullDataStore()
        else:
            raise Exception("DataStore type not supported")
