import json
import time
import typing

import paho.mqtt.client as mqtt
from config import ApplicationConfiguration
from lib.datastores.datastore import DataStore


class MqttDataStore(DataStore):
    def __init__(self):
        super().__init__()
        self.messages = {}

        self.base_config = ApplicationConfiguration
        self.config = self.base_config.datastore.mqtt
        self.logger.debug(f"Initializing MQTT Data Store with broker {self.config.host}:{self.config.port}")
        self.client = self.create()
        self.client.loop_start()
        count = 0
        found = 0
        # Wait for all topics to be subscribed to and received or timeout after 3 seconds
        while count < 3:
            for topic in self.config.topics:
                if topic in self.messages:
                    found += 1
            if found == len(self.config.topics):
                break

            count += 1
            found = 0
            time.sleep(1)
        self.logger.debug(f"Subscribed to {found} of {len(self.config.topics)} topics")
        if found < len(self.config.topics):
            self.logger.warning(f"Failed to retrieve all expected topics: {found} of {len(self.config.topics)}")
            self.logger.warning(f"Topics found: {self.messages.keys()}")
            self.logger.warning(f"Expected topics: {self.config.topics}")
        self.client.loop_stop()

    def create(self) -> mqtt.Client:
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect
        client.on_log = self.on_log
        client.on_connect_fail = self.on_connect_fail

        self.logger.debug("========================================")
        self.logger.debug(f"user: {self.config.username}")
        self.logger.debug("password: ********")
        self.logger.debug(f"host: {self.config.host}")
        self.logger.debug(f"port: {self.config.port}")
        self.logger.debug("========================================")

        client.username_pw_set(self.config.username, self.config.password)
        client.connect(self.config.host, self.config.port, 60)
        return client

    def on_connect_fail(self, client, userdata):
        self.logger.error(f"Connection failed: {json.dumps(userdata)}")

    def on_log(self, client, userdata, level, buf):
        self.logger.debug(buf)

    def on_connect(self, client, userdata, flags, rc):
        if rc > 0:
            self.logger.error(f"Disconnected with result code {rc}")
            self.logger.debug(self._get_rc_message(rc))

        for topic in self.config.topics:
            self.logger.debug(f"Subscribing to topic '{topic}'")
            client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        self.logger.debug(f"Message received on topic '{msg.topic}'")
        self.logger.debug(msg.payload)
        self.messages[msg.topic] = msg.payload

    def on_disconnect(self, client, userdata, rc):
        if rc > 0:
            self.logger.error(f"Disconnected with result code {rc}")
            self.logger.debug(self._get_rc_message(rc))

    def _get_rc_message(self, rc: int) -> str:
        if rc == 0:
            msg = "Success"
        elif rc == 1:
            msg = "Connection refused because of a bad protocol version"
        elif rc == 2:
            msg = "Connection refused because the identifier was rejected"
        elif rc == 3:
            msg = "Connection refused because the server is unavailable"
        elif rc == 4:
            msg = "Connection refused because the user name or password is incorrect"
        elif rc == 5:
            msg = "Connection refused because the client is not authorized"
        else:
            msg = f"Unknown error code: {rc}"
        return msg

    def read(self, topic: str) -> typing.Any:
        if topic in self.messages:
            self.logger.debug(f"Read from topic '{topic}'")
            result = json.loads(self.messages[topic])
            self.logger.debug(result)
            return result
        else:
            self.logger.debug(f"Topic '{topic}' not found")
        return None

    def write(self, topic: str, data: typing.Union[dict, str], ttl: int) -> bool:
        try:
            self.logger.debug(f"Publishing to topic '{topic}'")
            if isinstance(data, dict):
                data = json.dumps(data)

            self.client.publish(topic, data, qos=1, retain=True)
            return True
        except Exception as e:
            self.logger.error(f"Error publishing to topic {topic}")
            self.logger.error(e)
            return False
