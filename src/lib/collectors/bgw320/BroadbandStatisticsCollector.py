import typing
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.core import Metric
from prometheus_client.core import InfoMetricFamily
from lib.enums.DataStoreTypes import DataStoreTypes
from lib.datastores.factory import DatastoreFactory
from lib.collectors.Collector import Collector
import lib.utils as utils

class BroadbandStatisticsCollector(Collector):
    def __init__(self, modem):
        super().__init__(modem)
        self.subspace = self.safe_name('broadband')

    def collect(self) -> typing.List[Metric]:
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
        # get each and create an info metric
        for section in data.keys():
            if section == 'metadata':
                continue
            # help = self.get_help(section, metadata)
            section_data = data[section]
            for key in section_data.keys():
                value = section_data[key]
                help = self.get_help(key, metadata)
                if utils.is_booleanable(value):
                    value = utils.to_boolean(value)
                    g = GaugeMetricFamily(
                        name=self.metric_safe_name(key),
                        documentation=help,
                        labels=['model', 'host', 'modem'],
                    )
                    g.add_metric([self.modem.type, self.modem.host, self.modem.name], value)
                    metrics.append(g)
                elif value.isnumeric():
                    value = float(value)

                    g = GaugeMetricFamily(
                        name=self.metric_safe_name(f'{section}_{key}'),
                        documentation=help,
                        labels=['model', 'host', 'modem'],
                    )
                    g.add_metric([self.modem.type, self.modem.host, self.modem.name], value)
                    metrics.append(g)
        return metrics

    def get_help(self, key: str, metadata: dict) -> str:
        if key in metadata['help']:
            return metadata['help'][key]
        return ''
