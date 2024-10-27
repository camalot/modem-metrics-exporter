import typing

from prometheus_client.core import GaugeMetricFamily
from prometheus_client.core import Metric
from prometheus_client.core import InfoMetricFamily
from lib.collectors.bgw320.BGW320Collector import BGW320Collector
import lib.utils as utils


class HomeNetworkStatsCollector(BGW320Collector):
    def __init__(self, modem):
        super().__init__(modem)
        self.subspace = self.safe_name('lan')

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
        for section in data.keys():
            if section == 'metadata':
                continue
            section_data = data[section]
            if section == "interfaces":
                interface_metrics = self.process_interfaces(section_data, metadata)
                metrics.extend(interface_metrics)

            elif section == "lan":
                lan_metrics = self.process_lan(section_data, metadata)
                metrics.extend(lan_metrics)

            elif section == 'wifistatus' or section == 'wifistatistics':
                wifi_metrics = self.process_wifi(section, section_data, metadata)
                metrics.extend(wifi_metrics)
            else:
                generic_metrics = self.process_generic(section, section_data, metadata)
                metrics.extend(generic_metrics)

        return metrics

    def process_generic(self, section: str, data: dict, metadata: dict) -> typing.List[Metric]:
        metrics = []
        for group in data.keys():
            key = group
            g = GaugeMetricFamily(
                name=self.metric_safe_name(f'{section}_{group}'),
                documentation=self.get_help(key, metadata),
                labels=['model', 'host', 'modem', 'name'],
            )

            value = data[group].get('value', '')
            name = utils.strip_string(data[group].get('name', key))

            if utils.is_booleanable(value):
                value_bool = utils.to_boolean(value)
                g.add_metric([self.modem.type, self.modem.host, self.modem.name, name], 1 if value_bool else 0)
                metrics.append(g)
            elif value.isnumeric():
                g.add_metric([self.modem.type, self.modem.host, self.modem.name, name], float(value))
                metrics.append(g)
            else:
                info = InfoMetricFamily(
                    name=self.metric_safe_name(f'{section}'),
                    documentation=self.get_help(name, metadata),
                    labels=['model', 'host', 'modem', 'name'],
                )
                info.add_metric(
                    [self.modem.type, self.modem.host, self.modem.name, name], {'key': group, 'value': value}
                )
                metrics.append(info)
        return metrics

    def process_lan(self, data: dict, metadata: dict) -> typing.List[Metric]:
        metrics = []
        for section in data.keys():
            name = utils.strip_string(data[section]['name'])
            ports = ['port1', 'port2', 'port3', 'port4']
            lookup = {'port1': 'Port 1', 'port2': 'Port 2', 'port3': 'Port 3', 'port4': 'Port 4'}
            for port in ports:
                g = GaugeMetricFamily(
                    name=self.metric_safe_name(f'{name}'),
                    documentation=self.get_help('lan', metadata),
                    labels=['model', 'host', 'modem', 'name', 'port'],
                )
                value = data[section][port]
                if utils.is_booleanable(value):
                    value_bool = utils.to_boolean(value)
                    g.add_metric(
                        [self.modem.type, self.modem.host, self.modem.name, name, lookup[port]], 1 if value_bool else 0
                    )
                else:
                    g.add_metric([self.modem.type, self.modem.host, self.modem.name, name, lookup[port]], float(value))
                metrics.append(g)
        return metrics

    def process_wifi_item(self, value, section, group, name, metadata, freq) -> typing.List[Metric]:
        metrics = []
        if utils.is_booleanable(value):
            g = GaugeMetricFamily(
                name=self.metric_safe_name(f'{section}_{group}'),
                documentation=self.get_help(name, metadata),
                labels=['model', 'host', 'modem', 'name', 'frequency'],
            )

            value_bool = utils.to_boolean(value)
            g.add_metric([self.modem.type, self.modem.host, self.modem.name, name, freq], 1 if value_bool else 0)
            metrics.append(g)
        elif utils.is_string_list(value, '/'):
            i = InfoMetricFamily(
                name=self.metric_safe_name(f'{section}'),
                documentation=self.get_help(name, metadata),
                labels=['model', 'host', 'modem', 'name', 'frequency'],
            )
            group_plural = f'{group}s'
            name_plural = f'{name}s'
            i.add_metric(
                [self.modem.type, self.modem.host, self.modem.name, name_plural, freq],
                {'key': group_plural, 'value': value},
            )
            for v in utils.to_string_list(value, '/'):
                i.add_metric(
                    [self.modem.type, self.modem.host, self.modem.name, name, freq], {'key': group, 'value': v}
                )
            metrics.append(i)
        elif utils.is_string_list(value, ','):
            for v in utils.to_string_list(value):
                if v.isnumeric():
                    g = GaugeMetricFamily(
                        name=self.metric_safe_name(f'{section}_{group}'),
                        documentation=self.get_help(name, metadata),
                        labels=['model', 'host', 'modem', 'name', 'frequency'],
                    )
                    g.add_metric([self.modem.type, self.modem.host, self.modem.name, name, freq], float(v))
                    metrics.append(g)
                else:
                    i = InfoMetricFamily(
                        name=self.metric_safe_name(f'{section}'),
                        documentation=self.get_help(name, metadata),
                        labels=['model', 'host', 'modem', 'name', 'frequency'],
                    )
                    i.add_metric([self.modem.type, self.modem.host, self.modem.name, name, freq], {'key': group, 'value': v})
                    metrics.append(i)
        elif value.isnumeric():
            g = GaugeMetricFamily(
                name=self.metric_safe_name(f'{section}_{group}'),
                documentation=self.get_help(name, metadata),
                labels=['model', 'host', 'modem', 'name', 'frequency'],
            )
            g.add_metric([self.modem.type, self.modem.host, self.modem.name, name, freq], float(value))
            metrics.append(g)
        else:
            i = InfoMetricFamily(
                name=self.metric_safe_name(f'{section}'),
                documentation=self.get_help(name, metadata),
                labels=['model', 'host', 'modem', 'name', 'frequency'],
            )
            i.add_metric(
                [self.modem.type, self.modem.host, self.modem.name, name, freq], {'key': group, 'value': value}
            )
            metrics.append(i)
        return metrics

    def process_wifi(self, section: str, data: dict, metadata: dict) -> typing.List[Metric]:
        metrics = []
        for group in data.keys():
            frequencies = ['ghz24', 'ghz5']
            lookup = {'ghz24': '2.4GHz', 'ghz5': '5GHz'}
            for f in frequencies:

                value = data[group][f]
                if value is None:
                    continue

                if isinstance(value, list):
                    # loop through the list
                    for i, v in enumerate(value):
                        names = data[group]['name']
                        if isinstance(names, list):
                            name = utils.strip_string(names[i])
                        else:
                            name = utils.strip_string(names)

                        wifi_metrics = self.process_wifi_item(v, section, group, name, metadata, lookup[f])
                        metrics.extend(wifi_metrics)
                else:
                    name = utils.strip_string(data[group]['name'])
                    # single value
                    wifi_metrics = self.process_wifi_item(value, section, group, name, metadata, lookup[f])
                    metrics.extend(wifi_metrics)


        return metrics

    def process_interfaces(self, data: dict, metadata: dict) -> typing.List[Metric]:
        metrics = []

        for section in data.keys():
            interface = data[section]
            for x in ['active', 'inactive']:
                g = GaugeMetricFamily(
                    name=self.metric_safe_name(f'interface'),
                    documentation=self.get_help('interfaces', metadata),
                    labels=['model', 'host', 'modem', 'interface', 'status', 'mode', 'name'],
                )
                g.add_metric(
                    [self.modem.type, self.modem.host, self.modem.name, interface['name'], interface['status'], x],
                    interface[x],
                )
                metrics.append(g)
        return metrics
