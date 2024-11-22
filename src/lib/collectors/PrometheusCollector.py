import traceback

from config import ApplicationConfiguration
from lib.collectors.CollectorFactory import CollectorFactory
from lib.logging import setup_logging
from prometheus_client.registry import Collector


class PrometheusCollector(Collector):
    def __init__(self):
        # Namespace for the metrics
        self.config = ApplicationConfiguration
        self.logger = setup_logging(self.__class__.__name__, self.config.logging)

        self.namespace = self.safe_name(self.config.presentation.namespace)
        pass

    def safe_name(self, name):
        return name.replace(' ', '_').replace('.', '_').replace('-', '_').lower()

    def metric_safe_name(self, name):
        safe_name = self.safe_name(name)
        return f'{self.namespace}_{safe_name}'

    def collect(self):
        for modem in self.config.modems:
            self.logger.debug(f'creating collectors for {modem.name} : {modem.type}')
            collectors = modem.collectors
            for collector in collectors:
                try:
                    collector_instance = CollectorFactory.create(modem, collector.type)
                    metrics = collector_instance.collect() or []
                    for metric in metrics:
                        if metric:
                            yield metric

                except Exception as e:
                    self.logger.error(e)
                    self.logger.error(traceback.format_exc())
                    continue
