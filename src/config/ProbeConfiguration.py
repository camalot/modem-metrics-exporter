
class ProbeConfiguration:
  def __init__(self, *args, **kwargs):
        base:dict = kwargs.get('base', {})

        self.type = base.get('type', None)
        self.enabled = base.get('enabled', False)
        self.topic = base.get('topic', None)
        self.interval = base.get('interval', 60)
        self.datastore = base.get('datastore', 'FILE')
        self.timeout = base.get('timeout', 5)
