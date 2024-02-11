from os import environ

from yaml import BaseLoader, load

from config.dynamic_string import DynamicString
from utils.app_logger import logging


class YamlParser:
    @staticmethod
    def parse(file_name: str) -> dict:
        """
        Parse yaml document from file name.

        Parameters:
        file_name (str): The path of the yaml file

        Returns:
        dict: The loaded configuration

        """
        try:
            config = {}

            with open(file_name, "r") as f:
                # Read the config data into a string and parse the dynamic placeholders
                config_data = DynamicString.parse(f.read(), dict(environ))
                if config_data:
                    config = load(config_data,
                                  Loader=BaseLoader)  # added BaseLoader to prevent int cast of nft address

            return config

        except FileNotFoundError as e:
            logging.exception(e)
            return {}
