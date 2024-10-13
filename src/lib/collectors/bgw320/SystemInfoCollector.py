import traceback
import typing

from prometheus_client.core import CounterMetricFamily
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.core import Metric
from prometheus_client.core import InfoMetricFamily
from lib.enums.DataStoreTypes import DataStoreTypes
from lib.datastores.factory import DatastoreFactory
from lib.collectors.Collector import Collector
from lib.models.ProbeResult import ProbeResult
import lib.utils as utils

class SystemInfoCollector(Collector):
    def __init__(self, modem):
        super().__init__(modem)
        self.subspace = self.safe_name('system')

    def collect(self) -> typing.List[Metric]:
        metrics: typing.List[Metric] = []
        collector_state = 1
        data = None
        probe_data = None
        try:
            # get datastore
            datastore = DatastoreFactory().create(DataStoreTypes.from_str(self._config.datastore))
            # get data
            data_result = datastore.read(topic=str(self._config.topic))
            probe_data = ProbeResult.from_dict(data_result)

            if probe_data:
                data = probe_data.data
            else:
                self.logger.error(f'No data found for {self._config.topic}')
                collector_state = 0
        except Exception as e:
            self.logger.error(e)
            self.logger.error(traceback.format_exc())
            collector_state = 0

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
            [self.__class__.__name__, self.modem.type, self.modem.host, self.modem.name], collector_state
        )
        metrics.append(collector_metric)

        if probe_data:
            probe_metric.add_metric([probe_data.probe, self.modem.type, self.modem.host, self.modem.name], 1)
            metrics.append(probe_metric)
            probe_errors_metric.add_metric(
                [probe_data.probe, self.modem.type, self.modem.host, self.modem.name], len(probe_data.errors)
            )
            metrics.append(probe_errors_metric)

        if data is None:
            return metrics

        # get each and create an info metric
        for key in data.keys():
            if key == 'metadata':
                continue
            help = ''
            if key in data['metadata']['help']:
                help = data['metadata']['help'][key]

            value = data[key]
            if utils.is_datetime(value, '%Y/%m/%d %H:%M:%S'):
                value = utils.diff_now(utils.to_datetime(value, '%Y/%m/%d %H:%M:%S'))
                g = GaugeMetricFamily(
                    name=self.metric_safe_name(key),
                    documentation=help,
                    labels=['model', 'host', 'modem'],
                )
                g.add_metric([self.modem.type, self.modem.host, self.modem.name], value)
                metrics.append(g)
            elif utils.is_timedelta(value):
                value = utils.to_timedelta(value)
                g = GaugeMetricFamily(
                    name=self.metric_safe_name(key),
                    documentation=help,
                    labels=['model', 'host', 'modem'],
                )
                g.add_metric([self.modem.type, self.modem.host, self.modem.name], value.total_seconds())
                metrics.append(g)
            else:
                info = InfoMetricFamily(
                    name=self.metric_safe_name(''),
                    documentation=help,
                    labels=['model', 'host', 'modem'],
                )
                info.add_metric(
                    [self.modem.type, self.modem.host, self.modem.name],
                    {'value': data[key], 'key': key}
                )
                metrics.append(info)

        return metrics
