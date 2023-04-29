# bosch-thermostat-mqtt

A MQTT Client connecting to your Bosch Thermostat API, collecting measurments and publishing them as MQTT Messages. Use either the `scan` or `query` mode. The script can be started as a daemon if you like.

## Usage

### query
```
Usage: bosch_mqtt query [OPTIONS]

  Query values of Bosch thermostat.

Options:
  --config PATH                   Read configuration from PATH.  [default:
                                  config.yml]
  --host TEXT                     IP address of gateway or SERIAL for XMPP
                                  [required]
  --token TEXT                    Token from sticker without dashes.
                                  [required]
  --password TEXT                 Password you set in mobile app.
  --protocol [XMPP|HTTP]          Bosch protocol. Either XMPP or HTTP.
                                  [required]
  --device [NEFIT|IVT|EASYCONTROL]
                                  Bosch device type. NEFIT, IVT or
                                  EASYCONTROL.  [required]
  -d, --debug                     Set Debug mode. Single debug is debug of
                                  this lib. Second d is debug of aioxmpp as
                                  well.
  -p, --path TEXT                 Path to run against. Look at rawscan at
                                  possible paths. e.g. /gateway/uuid - Can be
                                  specified multiple times!  [required]
  --daemon                        Start as daemon.
  --interval INTEGER              Specify polling interval in seconds when
                                  started as daemon.  [default: 300]
  --mqtt-host TEXT                Adress of MQTT host.  [required]
  --mqtt-port INTEGER             Port of MQTT host.  [default: 1883]
  --mqtt-username TEXT            Username for MQTT connect.
  --mqtt-password TEXT            Password for MQTT connect.
  --help                          Show this message and exit.
```

### scan

```
Usage: bosch_mqtt scan [OPTIONS]

  Create rawscan of Bosch thermostat.

Options:
  --config PATH                   Read configuration from PATH.  [default:
                                  config.yml]
  --host TEXT                     IP address of gateway or SERIAL for XMPP
                                  [required]
  --token TEXT                    Token from sticker without dashes.
                                  [required]
  --password TEXT                 Password you set in mobile app.
  --protocol [XMPP|HTTP]          Bosch protocol. Either XMPP or HTTP.
                                  [required]
  --device [NEFIT|IVT|EASYCONTROL]
                                  Bosch device type. NEFIT, IVT or
                                  EASYCONTROL.  [required]
  -d, --debug                     Set Debug mode. Single debug is debug of
                                  this lib. Second d is debug of aioxmpp as
                                  well.
  -s, --smallscan [HC|DHW|SENSORS|RECORDINGS]
                                  Scan only single circuit of thermostat.
  --daemon                        Start as daemon.
  --interval INTEGER              Specify polling interval in seconds when
                                  started as daemon.  [default: 300]
  --mqtt-host TEXT                Adress of MQTT host.  [required]
  --mqtt-port INTEGER             Port of MQTT host.  [default: 1883]
  --mqtt-username TEXT            Username for MQTT connect.
  --mqtt-password TEXT            Password for MQTT connect.
  --help                          Show this message and exit.
```
