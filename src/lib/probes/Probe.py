import json
import requests
import signal
import time
import traceback

from config import ApplicationConfiguration
from lib.datastores.factory import DatastoreFactory
from lib.enums.DataStoreTypes import DataStoreTypes
from lib.logging import setup_logging
from lib.models.ProbeResult import ProbeResult

class Probe:
    def __init__(self, modem):
        self.config = ApplicationConfiguration
        self.logger = setup_logging(self.__class__.__name__, self.config.logging)

        self.enabled = False
        self.endpoint = None
        self.name = 'Probe'
        signal.signal(signal.SIGTERM, self.sighandler)
        self.modem = modem
        self._run_loop = True

        # find the config for this collector
        for pc in modem.probes:
            if pc.type == self.__class__.__name__:
                self._config = pc
                break
        if self._config is None:
            self.logger.error(f'No config found for {self.__class__.__name__}')
            raise Exception(f'No config found for {self.__class__.__name__}')

        self.enabled = self._config.enabled
        self.interval = self._config.interval
        self.topic = self._config.topic
        self.timeout = self._config.timeout
        self.datastore = DataStoreTypes.from_str(self._config.datastore)

    def sighandler(self, signum, frame):
        self.logger.warning('<SIGTERM received>')
        self._run_loop = False


    def parse(self, response) -> dict:
        raise NotImplementedError('You must implement the parse method')


    def run(self):
        self.logger = setup_logging(self.__class__.__name__, self.config.logging)

        if not self.enabled:
            self.logger.debug(f'{self.name} is disabled')
            return
        self.logger.debug(f'Running {self.name}')
        while self._run_loop:
            result = {}
            errors = []
            retry = 0
            retry_limit = 3
            while retry < retry_limit:
                try:
                    url = f'{self.modem.scheme}://{self.modem.host}:{self.modem.port}{self.endpoint}'
                    self.logger.debug(f'Fetching {self.name} data from {url}')
                    response = requests.get(url, timeout=self.timeout)
                    self.logger.debug(f'Response: {response.status_code}')
                    if response.status_code == 200:
                        result = self.parse(response.text)
                    else:
                        self.logger.error(f'Failed to fetch data from {url}')
                        errors.append({'message': f'Failed to fetch data from {url}', 'status_code': response.status_code})
                    self.logger.debug(f'{json.dumps(result, indent=2)}')
                    break
                except Exception as e:
                    self.logger.error(f'Failed to fetch data from {url}')
                    self.logger.error(e)
                    self.logger.error(traceback.format_exc())
                    errors.append({'message': f'Failed to fetch data from {url}', 'error': str(e)})
                    retry += 1
                    time.sleep(5)

                    if retry >= retry_limit:
                        self.logger.error(f'{self.name} reached retry limit')
                        errors.append({'message': f'{self.name} reached retry limit'})
                        break

            try:
                data_store = DatastoreFactory().create(self.datastore)
                cache_interval = self.interval + 15  # Set the cache TTL slightly longer than the probe interval
                topic = self.topic if self.topic else self.name
                probe_data = ProbeResult(modem=self.modem.name, probe=self.name, data=result, errors=errors).to_dict()
                data_store.write(topic, probe_data, cache_interval)
                self.logger.debug('Probe results successfully written to data store')
            except Exception as e:
                self.logger.error('Could not connect to data store')
                self.logger.error(e)
                self.logger.error(traceback.format_exc())

            self.logger.debug(f'{self.name} sleeping for {self.interval} seconds')

            time.sleep(self.interval)
        self.logger.debug(f'Exiting {self.name}')
