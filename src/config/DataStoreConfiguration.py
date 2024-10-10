from config.FileDataStoreConfiguration import FileDataStoreConfiguration
from config.HttpDataStoreConfiguration import HttpDataStoreConfiguration
from config.MongoDBDataStoreConfiguration import MongoDBDataStoreConfiguration
from config.MqttDataStoreConfiguration import MqttDataStoreConfiguration
from config.RedisDataStoreConfiguration import RedisDataStoreConfiguration
from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.DataStoreTypes import DataStoreTypes
from lib.enums.EnvVars import EnvVars
from lib.enums.YamlVars import YamlVars


class DataStoreConfiguration:
    def __init__(self, base: dict = {}):

        self.file = FileDataStoreConfiguration(base)
        self.redis = RedisDataStoreConfiguration(base)
        self.mongodb = MongoDBDataStoreConfiguration(base)
        self.http = HttpDataStoreConfiguration(base)
        self.mqtt = MqttDataStoreConfiguration(base)

    def merge(self, config: dict):
        self.__dict__.update(config)
