import typing
import traceback

from prometheus_client.core import CounterMetricFamily
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.core import Metric
from prometheus_client.core import InfoMetricFamily
from lib.collectors.Collector import Collector
from lib.datastores.factory import DatastoreFactory
from lib.enums.DataStoreTypes import DataStoreTypes
from lib.models.ProbeResult import ProbeResult
import lib.utils as utils

class HomeNetworkStatsCollector(Collector):
    def __init__(self, modem):
        super().__init__(modem)
        self.subspace = self.safe_name('lan')


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
            name = group
            g = GaugeMetricFamily(
                name=self.metric_safe_name(f'{section}_{group}'),
                documentation=self.get_help(name, metadata),
                labels=['model', 'host', 'modem', 'name'],
            )
            value = data[group]
            if utils.is_booleanable(value):
                value_bool = utils.to_boolean(value)
                g.add_metric([self.modem.type, self.modem.host, self.modem.name, name], 1 if value_bool else 0)
            elif value.isnumeric():
                g.add_metric([self.modem.type, self.modem.host, self.modem.name,name], float(value))
            else:
                g = InfoMetricFamily(
                    name=self.metric_safe_name(f'{section}'),
                    documentation=self.get_help(name, metadata),
                    labels=['model', 'host', 'modem', 'name'],
                )
                g.add_metric([self.modem.type, self.modem.host, self.modem.name, name], {'key': group, 'value': value})
            metrics.append(g)
        return metrics

    def process_lan(self, data: dict, metadata: dict) -> typing.List[Metric]:
        metrics = []
        for section in data.keys():
            name = data[section]['name']
            ports = ['port1', 'port2', 'port3', 'port4']
            lookup = {
                'port1': 'Port 1',
                'port2': 'Port 2',
                'port3': 'Port 3',
                'port4': 'Port 4',
            }
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

    def process_wifi(self, section: str, data: dict, metadata: dict) -> typing.List[Metric]:
        metrics = []
        for group in data.keys():
            name = data[group]['name']
            frequencies = ['ghz24', 'ghz5']
            lookup = {
                'ghz24': '2.4GHz',
                'ghz5': '5GHz'
            }
            for f in frequencies:

                value = data[group][f]
                if value is None:
                    continue

                if utils.is_booleanable(value):
                    g = GaugeMetricFamily(
                        name=self.metric_safe_name(f'{section}_{group}'),
                        documentation=self.get_help(name, metadata),
                        labels=['model', 'host', 'modem', 'name', 'frequency'],
                    )

                    value_bool = utils.to_boolean(value)
                    g.add_metric(
                        [self.modem.type, self.modem.host, self.modem.name, name, lookup[f]], 1 if value_bool else 0
                    )
                    metrics.append(g)
                elif utils.is_string_list(value, '/'):
                    i = InfoMetricFamily(
                        name=self.metric_safe_name(f'{section}_{group}'),
                        documentation=self.get_help(name, metadata),
                        labels=['model', 'host', 'modem', 'name', 'frequency'],
                    )
                    i.add_metric([self.modem.type, self.modem.host, self.modem.name, name, lookup[f]], {group: value})
                    for v in utils.to_string_list(value, '/'):
                        i.add_metric([self.modem.type, self.modem.host, self.modem.name, name, lookup[f]], {group: v})
                    metrics.append(i)
                elif utils.is_string_list(value, ','):
                    for v in utils.to_string_list(value):
                        if v.isnumeric():
                            g = GaugeMetricFamily(
                                name=self.metric_safe_name(f'{section}_{group}'),
                                documentation=self.get_help(name, metadata),
                                labels=['model', 'host', 'modem', 'name', 'frequency'],
                            )
                            g.add_metric([self.modem.type, self.modem.host, self.modem.name, name, lookup[f]], float(v))
                            metrics.append(g)
                        else:
                            i = InfoMetricFamily(
                                name=self.metric_safe_name(f'{section}_{group}'),
                                documentation=self.get_help(name, metadata),
                                labels=['model', 'host', 'modem', 'name', 'frequency'],
                            )
                            i.add_metric([self.modem.type, self.modem.host, self.modem.name, name, lookup[f]], {group: v})
                            metrics.append(i)
                elif value.isnumeric():
                    g = GaugeMetricFamily(
                        name=self.metric_safe_name(f'{section}_{group}'),
                        documentation=self.get_help(name, metadata),
                        labels=['model', 'host', 'modem', 'name', 'frequency'],
                    )
                    g.add_metric([self.modem.type, self.modem.host, self.modem.name, name, lookup[f]], float(value))
                    metrics.append(g)
                else:
                    i = InfoMetricFamily(
                        name=self.metric_safe_name(f'{section}_{group}'),
                        documentation=self.get_help(name, metadata),
                        labels=['model', 'host', 'modem', 'name', 'frequency'],
                    )
                    i.add_metric([self.modem.type, self.modem.host, self.modem.name, name, lookup[f]], {group: value})
                    metrics.append(i)
        return metrics

    def process_interfaces(self, data: dict, metadata: dict) -> typing.List[Metric]:
        metrics = []

        for section in data.keys():
            interface = data[section]
            for x in ['active', 'inactive']:
                g = GaugeMetricFamily(
                    name=self.metric_safe_name(f'interface'),
                    documentation=self.get_help('interfaces', metadata),
                    labels=['model', 'host', 'modem', 'interface', 'status', 'mode'],
                )
                g.add_metric(
                    [self.modem.type, self.modem.host, self.modem.name, interface['name'], interface['status'], x],
                    interface[x],
                )
                metrics.append(g)


        return metrics

    def get_help(self, key: str, metadata: dict) -> str:
        if key in metadata['help']:
            return metadata['help'][key]
        return ''
