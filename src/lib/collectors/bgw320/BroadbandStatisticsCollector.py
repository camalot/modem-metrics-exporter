import typing

import lib.utils as utils
from lib.collectors.bgw320.BGW320Collector import BGW320Collector
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily, Metric


class BroadbandStatisticsCollector(BGW320Collector):
    def __init__(self, modem):
        super().__init__(modem)
        self.subspace = self.safe_name('broadband')

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
        # get each and create an info metric
        for section in data.keys():
            if section == 'metadata':
                continue
            # help = self.get_help(section, metadata)
            section_data = data[section]
            for key in section_data.keys():
                name = section_data[key].get('name', key)
                value = section_data[key].get('value', '')
                help = self.get_help(key, metadata)
                if utils.is_booleanable(value):
                    value = utils.to_boolean(value)
                    g = GaugeMetricFamily(
                        name=self.metric_safe_name(key), documentation=help, labels=['model', 'host', 'modem', 'name']
                    )
                    g.add_metric([self.modem.type, self.modem.host, self.modem.name, name], value)
                    metrics.append(g)
                elif value.isnumeric():
                    value = float(value)

                    g = GaugeMetricFamily(
                        name=self.metric_safe_name(f'{section}_{key}'),
                        documentation=help,
                        labels=['model', 'host', 'modem', 'name'],
                    )
                    g.add_metric([self.modem.type, self.modem.host, self.modem.name, name], value)
                    metrics.append(g)
                else:
                    info = InfoMetricFamily(
                        name=self.metric_safe_name(''), documentation=help, labels=['model', 'host', 'modem', 'name']
                    )
                    info.add_metric(
                        [self.modem.type, self.modem.host, self.modem.name, name],
                        {'value': value, 'key': key}
                    )
                    metrics.append(info)

        return metrics
