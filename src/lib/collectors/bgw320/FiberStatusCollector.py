import traceback
import typing

from lib.collectors.Collector import Collector
from lib.datastores.factory import DatastoreFactory
from lib.enums.DataStoreTypes import DataStoreTypes
from lib.models.ProbeResult import ProbeResult
import lib.utils as utils

from prometheus_client.core import CounterMetricFamily
from prometheus_client.core import Metric
from prometheus_client.core import InfoMetricFamily
from prometheus_client.core import GaugeMetricFamily


class FiberStatusCollector(Collector):
    def __init__(self, modem):
        super().__init__(modem)
        self.subspace = self.safe_name('device')

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

        metadata = data.get('metadata', {})
        sections = ['temperature', 'vcc', 'txbias', 'txpower', 'rxpower']
        for section in sections:
            section_data = data.get(section.lower(), None)
            if not section_data:
                continue

            help = self.get_help(section, metadata)

            g = GaugeMetricFamily(
                name=self.metric_safe_name(section),
                documentation=help,
                labels=['model', 'host', 'modem'],
            )
            g.add_metric(
                [self.modem.type, self.modem.host, self.modem.name],
                float(section_data.get('value', '0')),
            )
            metrics.append(g)

            threshold_gauge = GaugeMetricFamily(
                name=self.metric_safe_name(f'threshold'),
                documentation='',
                labels=['model', 'host', 'modem', 'threshold', 'type', 'sensor'],
            )

            for level in ['alarm', 'warning']:
                level_gauge = GaugeMetricFamily(
                    name=self.metric_safe_name({level}),
                    documentation='',
                    labels=['model', 'host', 'modem', 'type', 'sensor'],
                )

                group = section_data.get(level, {})
                for key in ['high', 'low']:
                    level_gauge.add_metric(
                        [self.modem.type, self.modem.host, self.modem.name, key, section],
                        float(group.get(f'{key}', '0')),
                    )
                    threshold_gauge.add_metric(
                        [self.modem.type, self.modem.host, self.modem.name, key, level, section],
                        float(group.get(f'{key}T', '0')),
                    )
                metrics.append(level_gauge)
            metrics.append(threshold_gauge)
        fiber = data.get('fiber', {})
        for key in fiber.keys():
                value = fiber[key]
                help = self.get_help(key, metadata)

                if value.isnumeric():
                    g = GaugeMetricFamily(
                        name=self.metric_safe_name(f'{key}'),
                        documentation=help,
                        labels=['model', 'host', 'modem'],
                    )
                    g.add_metric(
                        [self.modem.type, self.modem.host, self.modem.name],
                        float(value),
                    )
                    metrics.append(g)
                elif utils.is_booleanable(value):
                    g = GaugeMetricFamily(
                        name=self.metric_safe_name(f'{key}'),
                        documentation=help,
                        labels=['model', 'host', 'modem'],
                    )
                    g.add_metric(
                        [self.modem.type, self.modem.host, self.modem.name],
                        utils.to_boolean(value),
                    )
                    metrics.append(g)
                else:
                    g = InfoMetricFamily(
                        name=self.metric_safe_name(key),
                        documentation=help,
                        labels=['model', 'host', 'modem'],
                    )
                    g.add_metric(
                        [self.modem.type, self.modem.host, self.modem.name],
                        {key: fiber[key]},
                    )
                    metrics.append(g)

        return metrics

    def get_help(self, key: str, metadata: dict) -> str:
        if key in metadata['help']:
            return metadata['help'][key]
        return ''
