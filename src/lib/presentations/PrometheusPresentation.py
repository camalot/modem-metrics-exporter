import time

from config import ApplicationConfiguration
from lib.collectors.PrometheusCollector import PrometheusCollector
from lib.logging import setup_logging
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY


class PrometheusPresentation:
    def __init__(self):
        config = ApplicationConfiguration
        self.logger = setup_logging(self.__class__.__name__, config.logging)
        self.presentation = config.presentation

    def run(self):
        interface = self.presentation.interface
        port = self.presentation.port
        self.logger.debug('Starting presentation service')
        start_http_server(port, addr=interface)
        self.logger.info(f'Listening => {interface}:{port}')
        REGISTRY.register(PrometheusCollector())

        # run forever
        while True:
            time.sleep(1)
