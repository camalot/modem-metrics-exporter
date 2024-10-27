import re
import traceback
import typing

from lib.datastores.factory import DatastoreFactory
from lib.enums.DataStoreTypes import DataStoreTypes
from lib.logging import setup_logging
from lib.models.ProbeResult import ProbeResult
from prometheus_client.core import GaugeMetricFamily

from prometheus_client.core import Metric
from config import ApplicationConfiguration
class Collector:
    METRIC_SAFE_RE = re.compile(r'^[a-zA-Z_:][a-zA-Z0-9_:]*$')
    METRIC_ALLOWED_PATTERN = re.compile(r'[a-zA-Z0-9_:]')

    
    def __init__(self, modem):
        self.config = ApplicationConfiguration
        self.namespace = self.config.presentation.namespace
        self.subspace = ''
        self.logger = setup_logging(self.__class__.__name__, self.config.logging)
        self.modem = modem
        # find the config for this collector
        for cc in self.modem.collectors:
            if cc.type == self.__class__.__name__:
                # self.logger.debug(f'Found config for {self.__class__.__name__}')
                self._config = cc
                break


    def safe_name(self, name):
        name = name.replace(' ', '_').replace('.', '_').replace('-', '_').lower()
        if not self.METRIC_SAFE_RE.match(name):
            # replace all invalid characters that match METRIC_ALLOWED_PATTERN with _
            name = ''.join(c if self.METRIC_ALLOWED_PATTERN.match(c) else '_' for c in name).strip('_')
        # replace all __ with _
        name = re.sub(r'_+', '_', name)
        return name

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

    def get_probe_data(self) -> typing.Optional[ProbeResult]:
        try:
            # get datastore
            datastore = DatastoreFactory().create(DataStoreTypes.from_str(self._config.datastore))
            # get data
            data_result = datastore.read(topic=str(self._config.topic))
            probe_data = ProbeResult.from_dict(data_result)

            if probe_data:
                return probe_data
            else:
                self.logger.error(f'No data found for {self._config.topic}')
                return None
        except Exception as e:
            self.logger.error(e)
            self.logger.error(traceback.format_exc())
            return None

    def get_base_metrics(self, probe_data: typing.Optional[ProbeResult], collector_state: bool) -> typing.List[Metric]:
        metrics = []
        probe_metric = GaugeMetricFamily(
            name=self.metric_root_safe_name('probe'),
            documentation='Probe info that collected the data',
            labels=['type', 'model', 'host', 'modem'],
        )
        probe_errors_metric = GaugeMetricFamily(
            name=self.metric_root_safe_name('probe_errors'),
            documentation='Probe errors',
            labels=['type', 'model', 'host', 'modem'],
        )

        collector_metric = GaugeMetricFamily(
            name=self.metric_root_safe_name('collector'),
            documentation='Indicates if the collector was initiated',
            labels=['type', 'model', 'host', 'modem'],
        )
        collector_metric.add_metric(
            [self.__class__.__name__, self.modem.type, self.modem.host, self.modem.name], 1 if collector_state else 0
        )
        metrics.append(collector_metric)

        if probe_data:
            probe_metric.add_metric([probe_data.probe, self.modem.type, self.modem.host, self.modem.name], 1)
            metrics.append(probe_metric)
            probe_errors_metric.add_metric(
                [probe_data.probe, self.modem.type, self.modem.host, self.modem.name], len(probe_data.errors)
            )
            metrics.append(probe_errors_metric)

        return metrics
