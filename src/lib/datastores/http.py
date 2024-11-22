import hashlib
import json
import typing

import requests
from config import ApplicationConfiguration
from lib.datastores.datastore import DataStore


class HttpDataStore(DataStore):
    def __init__(self):
        super().__init__()
        self.base_config = ApplicationConfiguration
        self.config = self.base_config.datastore.http

    def checksum(self, data: dict) -> str:
        # calculate md5 checksum of the data
        return hashlib.md5(json.dumps(data).encode()).hexdigest()

    def build_url(self, url: str, topic: str) -> str:
        return url.replace(":topic", topic)

    def read(self, topic: str) -> typing.Optional[dict]:
        # add topic to the params
        if self.config.read.params is None:
            self.config.read.params = {}

        self.config.read.params["topic"] = topic

        url: str = self.build_url(self.config.read.url, topic)
        self.logger.debug(f"Reading data from {url}")
        response = requests.request(
            url=url,
            method=self.config.read.method,
            headers=self.config.read.headers,
            cookies=self.config.read.cookies,
            auth=self.config.read.auth,
            timeout=self.config.read.timeout,
            params=self.config.read.params,
            verify=self.config.verify_ssl,
        )

        # response object:
        # { topic, data, ttl }
        try:
            result = response.json()
            if result and "data" in result:
                self.logger.debug(json.dumps(result["data"], indent=2))
                return result["data"]
            else:
                return None
        except Exception as e:
            self.logger.error(f"Error reading data from HTTP: {e}")
            self.logger.debug(response.text)
            return None

    def write(self, topic: str, data: dict, ttl: int) -> bool:
        checksum = self.checksum(data)
        payload = {"topic": topic, "data": data, "ttl": ttl, "checksum": checksum}
        url: str = self.build_url(self.config.read.url, topic)
        self.logger.debug(f"Writing data to {url}")

        response = requests.request(
            url=self.build_url(self.config.write.url, topic),
            method=self.config.write.method,
            headers=self.config.write.headers,
            cookies=self.config.write.cookies,
            auth=self.config.write.auth,
            timeout=self.config.write.timeout,
            verify=self.config.verify_ssl,
            json=payload,
        )
        # self.logger.debug(json.dumps(payload, indent=2))
        try:
            result = response.json()
            # response object: { topic, success, checksum, ttl }
            # payload: { topic, data, ttl, checksum }
            return True if result and "success" in result and result["success"] else False
        except Exception as e:
            self.logger.error(f"Error writing data to HTTP: {e}")
            self.logger.debug(response.text)
            return False
