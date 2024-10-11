import typing

from lib.logging import setup_logging
from prometheus_client.core import Metric
from config import ApplicationConfiguration
class Collector:
    def __init__(self):
        self.config = ApplicationConfiguration
        self.namespace = self.config.presentation.namespace
        self.subspace = ''
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
        safe_sub = self.safe_name(self.subspace)
        safe_namespace = self.safe_name(self.namespace)
        if self.subspace:
            if safe_name:
                return f'{safe_namespace}_{safe_sub}_{safe_name}'
            else:
                return f'{safe_namespace}_{safe_sub}'
        return self.metric_root_safe_name(name)

    def metric_root_safe_name(self, name):
        safe_name = self.safe_name(name)
        safe_namespace = self.safe_name(self.namespace)
        if safe_name:
            return f'{safe_namespace}_{safe_name}'
        else:
            return safe_namespace

    def collect(self) -> typing.List[Metric]:
        return []
