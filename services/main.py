import paho.mqtt.client as mqtt
import time
import datetime
import logging
import json
from influxdb import InfluxDBClient

MQTT_ADDRESS = 'mosquitto'
MQTT_USER = 'mqttuser'
MQTT_PASSWORD = 'mqttpassword'
MQTT_CLIENT_ID = 'AdapterToInfluxDB'
MQTT_TOPIC = '+/+'
MQTT_REGEX = '([^/]+)/([^/]+)'

INFLUXDB_ADDRESS = 'influxdb'
INFLUXDB_USER = 'root'
INFLUXDB_PASSWORD = 'root'
INFLUXDB_DATABASE = 'iot_db'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))
    client.subscribe("#")


def log(topic, data_dict, timestamp, time_now, location, station):
    print(time_now + " Received a message by topic " + "[" + topic + "]")
    if timestamp == time_now:
        print(time_now + " Data timestamp is NOW")
    else:
        print(time_now + " Data timestamp is: " + timestamp)
    for key in data_dict:
        print(time_now + " " + location + "." + station + "." + key + " " + str(data_dict[key]))
    print("\n")


def _send_sensor_data_to_influxdb(topic, sensor_data):
    x = topic.split("/")
    location = x[0]
    station = x[1]

    data_dict = json.loads(sensor_data)
    time_now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    if "timestamp" not in data_dict:
        timestamp = time_now
    else:
        timestamp = data_dict["timestamp"]
        del data_dict["timestamp"]

    remove_keys = []
    rename_keys = []
    for key in data_dict:
        if type(data_dict[key]) != int:
            if type(data_dict[key]) != float:
                remove_keys.append(key)

    for key in remove_keys:
        del data_dict[key]

    log(topic, data_dict, timestamp, time_now, location, station)

    for key in data_dict:
        measurement = location + "." + station + "." + key
        json_body = [
            {
                "measurement": measurement,
                "tags": {
                    "location": location,
                    "station": station,
                },
                "time": timestamp,
                "fields": {
                    "value": data_dict[key],
                }
            }
        ]
        influxdb_client.write_points(json_body)



# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    sensor_data = msg.payload.decode('utf-8')
    if sensor_data is not None:
        _send_sensor_data_to_influxdb(msg.topic, sensor_data)


def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)


def main():
    _init_influxdb_database()

    print("Connect MQTT client")
    client = mqtt.Client(MQTT_CLIENT_ID)
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_ADDRESS, 1883, 60)
    client.loop_forever()

if __name__ == '__main__':
    print('MQTT to InfluxDB bridge')
    main()