from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.EnvVars import EnvVars
from lib.enums.YamlVars import YamlVars


class RedisDataStoreConfiguration:
    def __init__(self, base: dict = {}):
        self.host = EnvVars.REDIS_HOST.string(YamlVars.REDIS_HOST.string(base, ConfigurationDefaults.REDIS_HOST))
        self.port = EnvVars.REDIS_PORT.integer(YamlVars.REDIS_PORT.integer(base, ConfigurationDefaults.REDIS_PORT))
        self.password = EnvVars.REDIS_PASSWORD.nullable(YamlVars.REDIS_PASSWORD.nullable(base, None))
        self.db = EnvVars.REDIS_DB.string(YamlVars.REDIS_DB.string(base, ConfigurationDefaults.REDIS_DB))

    def merge(self, config: dict):
        self.__dict__.update(config)
