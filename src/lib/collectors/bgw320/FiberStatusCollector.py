import traceback
import typing

from lib.collectors.Collector import Collector
from lib.datastores.factory import DatastoreFactory
from lib.enums.DataStoreTypes import DataStoreTypes
import lib.utils as utils

from prometheus_client.core import Metric
from prometheus_client.core import InfoMetricFamily
from prometheus_client.core import GaugeMetricFamily


class FiberStatusCollector(Collector):
    def __init__(self, modem):
        super().__init__(modem)
        self.subspace = self.safe_name('device')

    def collect(self) -> typing.List[Metric]:
        try:
            # get datastore
            datastore = DatastoreFactory().create(DataStoreTypes.from_str(self._config.datastore))
            # get data
            data = datastore.read(self._config.topic)
            metrics = []

            g = GaugeMetricFamily(
                name=self.metric_root_safe_name('collector'),
                documentation='Indicates if the collector was initiated',
                labels=['type', 'model', 'host', 'modem'],
            )
            g.add_metric([self.__class__.__name__, self.modem.type, self.modem.host, self.modem.name], 1)
            metrics.append(g)

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

                g = GaugeMetricFamily(
                    name=self.metric_safe_name(f'threshold'),
                    documentation='',
                    labels=['model', 'host', 'modem', 'threshold', 'type', 'sensor'],
                )

                for level in ['alarm', 'warning']:
                    group = section_data.get(level, {})
                    for key in ['high', 'low']:
                        g.add_metric(
                            [self.modem.type, self.modem.host, self.modem.name, key, level, section],
                            float(group.get(f'{key}T', '0')),
                        )
                metrics.append(g)
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

        except Exception as e:
            self.logger.error(e)
            self.logger.error(traceback.format_exc())
            return []

    def get_help(self, key: str, metadata: dict) -> str:
        if key in metadata['help']:
            return metadata['help'][key]
        return ''
