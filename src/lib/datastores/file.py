import json
import os
import time
import typing

from config import ApplicationConfiguration
from lib.datastores.datastore import DataStore


class FileDataStore(DataStore):
    def __init__(self):
        super().__init__()
        self.config = ApplicationConfiguration
        data_path = self.config.datastore.file.path
        # if data_path is empty, set it to the current directory
        if not data_path:
            data_path = os.getcwd()
        # if data_path ends with a /, remove it
        if data_path.endswith("/"):
            data_path = data_path[:-1]
        self.data_path = data_path

        # check that the path exists. If it doesn't, create it
        if not os.path.exists(data_path):
            os.makedirs(data_path)

        self.logger.debug(f"Initializing File Data Store with path {data_path}")

    def __check_ttl(self, topic: str) -> bool:
        topic = self.__normalize_topic(topic)
        ttl_file = f"{topic}.ttl"
        expired = False
        ttl = 60 * 60 * 24  # default ttl is 24 hours
        # check if the ttl file exists
        if os.path.exists(ttl_file):
            with open(ttl_file, "r") as file:
                try:
                    ttl = int(file.read())
                except ValueError:
                    ttl = 60 * 60 * 24

        if os.path.exists(topic):
            # get the file creation time
            creation_time = os.path.getctime(topic)
            # get the current time
            current_time = time.time()
            # get the difference between the current time and the creation time
            diff = current_time - creation_time
            # if the difference is greater than the ttl, return True
            expired = diff > ttl

        if expired:
            self.logger.debug(f"File '{topic}' has expired. Removing it.")
            # remove the file and the ttl file
            os.remove(topic)
            os.remove(ttl_file)

        return expired

    def __normalize_topic(self, topic: str) -> str:
        # check if topic is a relative path. If it is, make it an absolute path
        if not topic.startswith("/"):
            topic = f"{self.data_path}/{topic}"
        return topic

    def read(self, topic: str) -> typing.Any:
        data = None
        try:
            topic = self.__normalize_topic(topic)
            expired = self.__check_ttl(topic)
            if expired:
                return data

            try:
                self.logger.debug(f"Reading file {topic}")
                with open(topic, "r") as file:
                    data = json.loads(file.read())
            except FileNotFoundError:
                self.logger.warning(f"File {topic} not found")
                data = None
            return data
        except Exception as e:
            self.logger.error(f"Error reading file {topic}")
            self.logger.error(e)
            return data

    def write(self, topic: str, data: dict, ttl: int) -> bool:
        try:
            topic = self.__normalize_topic(topic)

            # remove the file from the topic and create the folder structure
            folder = os.path.dirname(topic)
            if not os.path.exists(folder):
                os.makedirs(folder)

            self.logger.debug(f"Writing to file {topic}")
            with open(topic, "w") as file:
                file.write(json.dumps(data))

            # write the ttl file
            ttl_file = f"{topic}.ttl"
            self.logger.debug(f"Writing ttl file {ttl_file}")
            with open(ttl_file, "w") as file:
                file.write(str(ttl))

            return True
        except Exception as e:
            self.logger.error(f"Error writing to file {topic}")
            self.logger.error(e)
            return False
