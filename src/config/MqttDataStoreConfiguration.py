from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.YamlVars import YamlVars


class MqttDataStoreConfiguration:
    def __init__(self, base: dict = {}, *args, **kwargs):
        self.host = YamlVars.MQTT_HOST.string(base, ConfigurationDefaults.MQTT_HOST)
        self.port = YamlVars.MQTT_PORT.integer(base, ConfigurationDefaults.MQTT_PORT)
        self.username = YamlVars.MQTT_USERNAME.nullable(base, None)
        self.password = YamlVars.MQTT_PASSWORD.nullable(base, None)

        self.topics = kwargs.get("topics", [])

    def merge(self, config: dict):
        self.__dict__.update(config)
