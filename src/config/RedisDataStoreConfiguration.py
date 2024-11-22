from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.YamlVars import YamlVars


class RedisDataStoreConfiguration:
    def __init__(self, base: dict = {}):
        self.host = YamlVars.REDIS_HOST.string(base, ConfigurationDefaults.REDIS_HOST)
        self.port = YamlVars.REDIS_PORT.integer(base, ConfigurationDefaults.REDIS_PORT)
        self.password = YamlVars.REDIS_PASSWORD.nullable(base, None)
        self.db = YamlVars.REDIS_DB.string(base, ConfigurationDefaults.REDIS_DB)

    def merge(self, config: dict):
        self.__dict__.update(config)
