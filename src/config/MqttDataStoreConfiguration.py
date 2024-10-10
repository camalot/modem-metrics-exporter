from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.EnvVars import EnvVars
from lib.enums.YamlVars import YamlVars


class MqttDataStoreConfiguration:
    def __init__(self, base: dict = {}, *args, **kwargs):
        self.host = EnvVars.MQTT_HOST.string(YamlVars.MQTT_HOST.string(base, ConfigurationDefaults.MQTT_HOST))
        self.port = EnvVars.MQTT_PORT.integer(YamlVars.MQTT_PORT.integer(base, ConfigurationDefaults.MQTT_PORT))
        self.username = EnvVars.MQTT_USERNAME.nullable(YamlVars.MQTT_USERNAME.nullable(base, None))
        self.password = EnvVars.MQTT_PASSWORD.nullable(YamlVars.MQTT_PASSWORD.nullable(base, None))

        self.topics = kwargs.get("topics", [])


    def merge(self, config: dict):
        self.__dict__.update(config)
