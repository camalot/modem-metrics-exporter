import typing

from lib.logging import setup_logging
from prometheus_client.core import Metric
from config import ApplicationConfiguration
class Collector:
    def __init__(self):
        self.config = ApplicationConfiguration
        self.namespace = self.config.presentation.namespace
        self.logger = setup_logging(self.__class__.__name__, self.config.logging)

        # find the config for this collector
        for cc in self.config.modem.collectors:
            if cc.type == self.__class__.__name__:
                print(f'Found config for {self.__class__.__name__}')
                self._config = cc
                break


    def safe_name(self, name):
        return name.replace(' ', '_').replace('.', '_').replace('-', '_').lower()

    def metric_safe_name(self, name):
        safe_name = self.safe_name(name)
        return f'{self.namespace}_{safe_name}'

    def collect(self) -> typing.List[Metric]:
        return []
