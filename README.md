# bosch-thermostat-mqtt

A MQTT Client connecting to your Bosch Thermostat API, collecting measurments and publishing them as MQTT Messages. Use either the `scan` or `query` mode. The script can be started as a daemon if you like.
The Client is inspired and based on [bosch-thermostat-client-python](https://github.com/bosch-thermostat/bosch-thermostat-client-python).

## Usage

The easiest way to use this MQTT Client is to create a configuration file containing all the Bosch and MQTT parameters. It might also not be reasonable to scan all Bosch endpoints and publish them all via MQTT. Said that you can also add specific endpoints to query and publish via MQTT.

### Configuration

Example of a config.yml:
```
token: your-bosch-token
password: your-bosch-password
host: ip-adress-of-your-bosch-thermostat
protocol: HTTP
device: IVT
path:
  - /system/sensors/temperatures/outdoor_t1
  - /system/sensors/temperatures/supply_t1
  - /system/sensors/temperatures/return
  - /heatSources/actualPower
  - /system/appliance/actualSupplyTemperature
  - /heatSources/actualModulation
  - /heatSources/CHpumpModulation
  - /heatSources/energyMonitoring/consumption
  - /heatSources/systemPressure
  - /dhwCircuits/dhw1/actualTemp
  - /heatingCircuits/hc1/roomtemperature
mqtt_host: ip-adress-of-your-mqtt-server
mqtt_username: your-mqtt-user
mqtt_password: your-mqtt-password
```

By default the MQTT Client will pick up the config.yml in your current directory. You can also specify its location by using the --config option.

### Start
You can now start bosch-mqtt as a daemon if you like:

```
# bosch_mqtt.py query --daemon
2023-05-28 13:42:21 INFO (MainThread) [__main__] Connecting to 10.0.2.71 with 'HTTP'
2023-05-28 13:42:22 INFO (MainThread) [__main__] Successfully connected to gateway. Found UUID: <your-UUID>
2023-05-28 13:42:22 INFO (MainThread) [__main__] Executing as daemon, interval is 300 seconds.
2023-05-28 13:42:23 INFO (MainThread) [__main__] Successfully connected to MQTT broker.
2023-05-28 13:42:23 INFO (MainThread) [__main__] Publishing bosch/RC300-<your-UUID>/system/sensors/temperatures/outdoor_t1
2023-05-28 13:42:23 INFO (MainThread) [__main__] Publishing bosch/RC300-<your-UUID>/system/sensors/temperatures/supply_t1
2023-05-28 13:42:23 INFO (MainThread) [__main__] Publishing bosch/RC300-<your-UUID>/system/sensors/temperatures/return
2023-05-28 13:42:23 INFO (MainThread) [__main__] Publishing bosch/RC300-<your-UUID>/heatSources/actualPower
2023-05-28 13:42:23 INFO (MainThread) [__main__] Publishing bosch/RC300-<your-UUID>/system/appliance/actualSupplyTemperature
2023-05-28 13:42:23 INFO (MainThread) [__main__] Publishing bosch/RC300-<your-UUID>/heatSources/actualModulation
2023-05-28 13:42:23 INFO (MainThread) [__main__] Publishing bosch/RC300-<your-UUID>/heatSources/CHpumpModulation
2023-05-28 13:42:23 INFO (MainThread) [__main__] Publishing bosch/RC300-<your-UUID>/heatSources/energyMonitoring/consumption
2023-05-28 13:42:23 INFO (MainThread) [__main__] Publishing bosch/RC300-<your-UUID>/heatSources/systemPressure
2023-05-28 13:42:23 INFO (MainThread) [__main__] Publishing bosch/RC300-<your-UUID>/dhwCircuits/dhw1/actualTemp
2023-05-28 13:42:23 INFO (MainThread) [__main__] Publishing bosch/RC300-<your-UUID>/heatingCircuits/hc1/roomtemperature
2023-05-28 13:42:23 INFO (MainThread) [__main__] Sleeping 300 seconds...
```

### MQTT-Explorer

![grafik](https://github.com/OlliL/bosch-thermostat-mqtt/assets/4688427/882791f0-5f92-4b8b-a2ec-ac4a9934b4c5)
