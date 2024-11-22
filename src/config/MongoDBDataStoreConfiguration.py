from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.YamlVars import YamlVars


class MongoDBDataStoreConfiguration:
    def __init__(self, base: dict = {}):
        self.url = YamlVars.MONGODB_URL.string(base, ConfigurationDefaults.MONGODB_URL)
        self.db = YamlVars.MONGODB_DB.string(base, ConfigurationDefaults.MONGODB_DB)
        self.collection = YamlVars.MONGODB_COLLECTION.string(base, ConfigurationDefaults.MONGODB_COLLECTION)

    def merge(self, config: dict):
        self.__dict__.update(config)
