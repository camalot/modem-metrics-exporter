# MODEM-METRICS-EXPORTER

Currently only supports the AT&T [BGW320](https://help.sonic.com/hc/en-us/articles/1500000066642-BGW320)

## MODEM SUPPORT

| Modem Model | Info Link |
|-------------|-----------|
| [BGW320](docs/BGW320.md) | [BGW320 Info](https://help.sonic.com/hc/en-us/articles/1500000066642-BGW320) |

## CONFIGURATION

The [modemprobe.yaml](modemprobe.yaml) is a sample configuration file. This file is set with defaults.

### LOGGING

The `logging` block lets you define the log level, message format, and date format of the logs.

#### LEVELS

> [!NOTE]
> See [logging.levels](https://docs.python.org/3/library/logging.html#levels) for more information.

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

``` yaml
logging:
  level: INFO
  format: '%(asctime)s [%(levelname)s] [%(name)s] %(message)s'
  date_format: '%Y-%m-%d %H:%M:%S'
```

### PRESENTATION

The `presentation` block is used for the prometheus metrics http server.

``` yaml

presentation:
  port: 5000  # the port used to serve
  interface: '0.0.0.0'  # the interface to bind
  namespace: 'modemprobe'  # the "namespace" used for all metrics
```

### DATASTORE

The configuration section for all supported datastore types

#### DATASTORE TYPES

- `file`
- `http`
- `mongodb`
- `mqtt`
- `null`
- `redis`

``` yaml
datastore:
  mqtt:
    host: 'localhost'
    port: 1883
    username: 'modemprobe'
    password: 'modemprobe'
  file:
    path: '/data/cache'
  redis:
    host: 'localhost'
    port: 6379
    db: 0
    # password: ''
  mongodb:
    url: 'mongodb://modemprobe:modemprobe@localhost:27017/admin'
    db: 'modemprobe'
    collection: 'modemprobe'
  http:
    verify_ssl: no
    read:
      url: 'https://localhost/modemprobe/data/:topic'
      method: 'GET'
      timeout: 5
      headers: {}
      cookies: {}
      params: {}
      auth: {}
    write:
      url: 'https://localhost/modemprobe/data/:topic'
      method: 'POST'
      timeout: 5
      headers: {}
      cookies: {}
      params: {}
      auth: {}
```

### MODEMS

This section defines the modems that you would like probed.

``` yaml
modems:
  - name: AT&T BGW320
    host: 192.168.1.254
    enabled: true
    scheme: http
    port: 80
    type: bgw320

    collectors:
      # Collectors can only read from a single datastore.
      - type: FiberStatusCollector
        enabled: true
        topic: modemprobe/fiberstatus
        datastore: FILE

      - type: HomeNetworkStatsCollector
        enabled: true
        topic: modemprobe/lanstats
        datastore: FILE

      - type: SystemInfoCollector
        enabled: true
        topic: modemprobe/systeminfo
        datastore: FILE

      - type: BroadbandStatisticsCollector
        enabled: true
        topic: modemprobe/broadbandstats
        datastore: FILE

    probes:
      # Probes can have multiple datastores
      # this will store the data in those datastores
      # in the order they are defined
      # A collector can only read from a single datastore
      - type: FiberStatusProbe
        enabled: true  # Enables the probe
        interval: 120  # how frequent it will probe for the data
        datastores:  # array of datastores
          - type: FILE
            topic: modemprobe/fiberstatus
            # enabled: true  # default is true. enables/disables the specific datastore

        # if you don't specify multiple datastores, you can use singular datastore
        # topic: modemprobe/fiberstatus
        # datastore: FILE

      - type: HomeNetworkStatsProbe
        enabled: true
        interval: 120
        datastores:
          - type: FILE
            topic: modemprobe/lanstats

      - type: SystemInfoProbe
        enabled: true
        interval: 600
        datastores:
          - type: FILE
            topic: modemprobe/systeminfo

      - type: BroadbandStatisticsProbe
        enabled: true
        interval: 120
        datastores:
          - type: FILE
            topic: modemprobe/broadbandstats
```