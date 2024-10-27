import typing

from config.ProbeDataStoreConfiguration import ProbeDataStoreConfiguration


class ProbeConfiguration:
    def __init__(self, **kwargs):
        base: dict = kwargs.get('base', {})

        self.type = base.get('type', None)
        self.enabled = base.get('enabled', False)
        self.interval = base.get('interval', 60)
        self.timeout = base.get('timeout', 5)

        datastores: typing.List[ProbeDataStoreConfiguration] = []
        for ds in base.get('datastores', []):
            datastore = ProbeDataStoreConfiguration(**ds)
            datastores.append(datastore)

        if 'topic' in base and 'datastore' in base:
            topic = base.get('topic', None)
            datastore = base.get('datastore', None)
            # if topic exists in the array, then do not add it to the datastore array
            if f'{datastore}:{topic}' not in [f'{ds.type}:{ds.topic}' for ds in datastores] and datastore:
                print(f'Adding {datastore}:{topic} to datastores')
                datastore_config = ProbeDataStoreConfiguration(
                    **{'type': datastore, 'topic':topic, 'enabled': self.enabled}
                )
                datastores.append(datastore_config)
        self.datastores = datastores
