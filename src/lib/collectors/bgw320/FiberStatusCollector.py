import typing

from lib.collectors.bgw320.BGW320Collector import BGW320Collector
import lib.utils as utils

from prometheus_client.core import Metric
from prometheus_client.core import InfoMetricFamily
from prometheus_client.core import GaugeMetricFamily


class FiberStatusCollector(BGW320Collector):
    def __init__(self, modem):
        super().__init__(modem)
        self.subspace = self.safe_name('device')

    def collect(self) -> typing.List[Metric]:
        metrics: typing.List[Metric] = []
        collector_state = True
        data = None
        probe_data = self.get_probe_data()
        if not probe_data:
            self.logger.error(f'No data found for {self._config.topic}')
            collector_state = False
        else:
            data = probe_data.data

        metrics.extend(self.get_base_metrics(probe_data=probe_data, collector_state=collector_state))

        if data is None:
            return metrics

        metadata = data.get('metadata', {})
        sections = ['temperature', 'vcc', 'txbias', 'txpower', 'rxpower']
        for section in sections:
            section_data = data.get(section.lower(), None)
            if not section_data:
                continue

            help = self.get_help(section, metadata)

            value = section_data.get('value', '0')
            name = section_data.get('name', section)

            g = GaugeMetricFamily(
                name=self.metric_safe_name(section),
                documentation=help,
                labels=['model', 'host', 'modem', 'name'],
            )
            g.add_metric(
                [self.modem.type, self.modem.host, self.modem.name, name],
                float(value),
            )
            metrics.append(g)

            threshold_gauge = GaugeMetricFamily(
                name=self.metric_safe_name(f'threshold'),
                documentation='',
                labels=['model', 'host', 'modem', 'threshold', 'type', 'sensor', 'name'],
            )

            for level in ['alarm', 'warning']:
                level_gauge = GaugeMetricFamily(
                    name=self.metric_safe_name(level),
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
                fiber_item = fiber[key]

                value = fiber_item.get('value', '0')
                name = fiber_item.get('name', key)

                help = self.get_help(key, metadata)

                if value.isnumeric():
                    g = GaugeMetricFamily(
                        name=self.metric_safe_name(f'{key}'),
                        documentation=help,
                        labels=['model', 'host', 'modem', 'name'],
                    )
                    g.add_metric(
                        [self.modem.type, self.modem.host, self.modem.name, name],
                        float(value),
                    )
                    metrics.append(g)
                elif utils.is_booleanable(value):
                    g = GaugeMetricFamily(
                        name=self.metric_safe_name(f'{key}'),
                        documentation=help,
                        labels=['model', 'host', 'modem', 'name'],
                    )
                    g.add_metric(
                        [self.modem.type, self.modem.host, self.modem.name, name],
                        utils.to_boolean(value),
                    )
                    metrics.append(g)
                else:
                    info = InfoMetricFamily(
                        name=self.metric_safe_name(''),
                        documentation=help,
                        labels=['model', 'host', 'modem', 'name'],
                    )
                    info.add_metric(
                        [self.modem.type, self.modem.host, self.modem.name, name],
                        {'value': value, 'key': key},
                    )
                    metrics.append(info)

        return metrics
