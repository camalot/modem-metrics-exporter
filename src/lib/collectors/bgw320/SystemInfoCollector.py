import typing
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.core import Metric
from prometheus_client.core import InfoMetricFamily
from lib.enums.DataStoreTypes import DataStoreTypes
from lib.datastores.factory import DatastoreFactory
from lib.collectors.Collector import Collector
import lib.utils as utils

class SystemInfoCollector(Collector):
    def __init__(self):
        super().__init__()

    def collect(self) -> typing.List[Metric]:
        # get datastore
        datastore = DatastoreFactory().create(DataStoreTypes.from_str(self._config.datastore))
        # get data
        data = datastore.read(self._config.topic)
        metrics = []

        g = GaugeMetricFamily(
            name=self.metric_safe_name('collector'),
            documentation='Indicates if the collector was initiated',
            labels=['type'],
        )
        g.add_metric([self.__class__.__name__], 1)
        metrics.append(g)

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
                value = utils.datetime_to_epoch(utils.to_datetime(value, '%Y/%m/%d %H:%M:%S'))
                g = GaugeMetricFamily(
                    name=self.metric_safe_name(key),
                    documentation=help,
                    labels=['model', 'host'],
                )
                g.add_metric([self.config.modem.type, self.config.modem.host], value)
                print('epoch value')
                metrics.append(g)
            elif utils.is_timedelta(value):
                value = utils.to_timedelta(value)
                g = GaugeMetricFamily(
                    name=self.metric_safe_name(key),
                    documentation=help,
                    labels=['model', 'host'],
                )
                g.add_metric([self.config.modem.type, self.config.modem.host], value.total_seconds())
                print('delta value')
                metrics.append(g)
            else:

                info = InfoMetricFamily(
                    name=self.metric_safe_name('system'),
                    documentation=help,
                    labels=['model', 'host'],
                )
                info.add_metric(
                    [self.config.modem.type, self.config.modem.host],
                    {key: data[key]}
                )
                metrics.append(info)

        return metrics
