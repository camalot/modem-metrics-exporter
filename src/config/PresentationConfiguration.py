from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.EnvVars import EnvVars
from lib.enums.YamlVars import YamlVars


class PresentationConfiguration:
    def __init__(self, base: dict = {}):
        self.port = EnvVars.PRESENTATION_PORT.integer(
            YamlVars.PRESENTATION_PORT.integer(base, ConfigurationDefaults.PRESENTATION_PORT)
        )
        self.interface = EnvVars.PRESENTATION_INTERFACE.string(
            YamlVars.PRESENTATION_INTERFACE.string(base, ConfigurationDefaults.PRESENTATION_INTERFACE)
        )
        self.namespace = EnvVars.PRESENTATION_NAMESPACE.string(
            YamlVars.PRESENTATION_NAMESPACE.string(base, ConfigurationDefaults.PRESENTATION_NAMESPACE)
        )
