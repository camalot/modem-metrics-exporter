from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.EnvVars import EnvVars
from lib.enums.YamlVars import YamlVars


class MongoDBDataStoreConfiguration:
    def __init__(self, base: dict = {}):
        self.url = EnvVars.MONGODB_URL.string(YamlVars.MONGODB_URL.string(base, ConfigurationDefaults.MONGODB_URL))
        self.db = EnvVars.MONGODB_DB.string(YamlVars.MONGODB_DB.string(base, ConfigurationDefaults.MONGODB_DB))
        self.collection = EnvVars.MONGODB_COLLECTION.string(
            YamlVars.MONGODB_COLLECTION.string(base, ConfigurationDefaults.MONGODB_COLLECTION)
        )

    def merge(self, config: dict):
        self.__dict__.update(config)
