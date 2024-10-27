class CollectorConfiguration:
    def __init__(self, *args, **kwargs):
        base: dict = kwargs.get('base', {})

        self.type = base.get('type', None)
        self.enabled = base.get('enabled', False)
        self.datastore = base.get('datastore', 'FILE')
        self.topic = base.get('topic', None)
