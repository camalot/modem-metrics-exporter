
class ProbeDataStoreConfiguration:
    def __init__(self, **kwargs):
        self.type = kwargs.get('type', 'FILE')
        self.topic = kwargs.get('topic', None)
        self.enabled = kwargs.get('enabled', True)
