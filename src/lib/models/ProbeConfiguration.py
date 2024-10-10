
class ProbeConfiguration:
  def __init__(self, base: dict = {}):
    self.name = base.get('name', None)
    self.enabled = base.get('enabled', False)
    self.endpoint = base.get('endpoint', None)
    self.pattern = base.get('pattern', None)
