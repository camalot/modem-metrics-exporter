import json
import typing

from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.EnvVars import EnvVars
from lib.enums.YamlVars import YamlVars
from lib.models.CollectorConfiguration import CollectorConfiguration
from lib.models.ProbeConfiguration import ProbeConfiguration

class ModemConfiguration:
    def __init__(self, base: dict = {}, load: bool = True):
        self.name = YamlVars.MODEM_NAME.string(base, ConfigurationDefaults.MODEM_TYPE)
        self.host = YamlVars.MODEM_HOST.string(base, ConfigurationDefaults.MODEM_HOST)
        self.port = YamlVars.MODEM_PORT.integer(base, ConfigurationDefaults.MODEM_PORT)
        self.username = YamlVars.MODEM_USERNAME.string(base, ConfigurationDefaults.MODEM_USERNAME)
        self.password = YamlVars.MODEM_PASSWORD.string(base, ConfigurationDefaults.MODEM_PASSWORD)
        self.scheme = YamlVars.MODEM_SCHEME.string(base, ConfigurationDefaults.MODEM_SCHEME)
        self.type = YamlVars.MODEM_TYPE.string(base, ConfigurationDefaults.MODEM_TYPE)

        self.collectors: typing.List[CollectorConfiguration] = []
        self.probes: typing.List[ProbeConfiguration] = []

        if load:
            self._load_collectors(base)
            self._load_probes(base)

    def _load_collectors(self, base: dict):
        collectors = YamlVars.MODEM_COLLECTORS.expand(base, [])
        if collectors:
            for collector in collectors:
                self.collectors.append(CollectorConfiguration(base=collector))

    def _load_probes(self, base: dict):
        probes = YamlVars.MODEM_PROBES.expand(base, [])
        if probes:
            for probe in probes:
                self.probes.append(ProbeConfiguration(base=probe))

    def merge(self, config: dict):
        self.__dict__.update(config)
