from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.YamlVars import YamlVars


class PresentationConfiguration:
    def __init__(self, base: dict = {}):
        self.port = YamlVars.PRESENTATION_PORT.integer(base, ConfigurationDefaults.PRESENTATION_PORT)
        self.interface = YamlVars.PRESENTATION_INTERFACE.string(base, ConfigurationDefaults.PRESENTATION_INTERFACE)
        self.namespace = YamlVars.PRESENTATION_NAMESPACE.string(base, ConfigurationDefaults.PRESENTATION_NAMESPACE)
