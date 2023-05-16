#!/usr/bin/env python3
from configparser import ConfigParser

import os
from client import Client
from time import sleep


def initialize_config():
    """
    Parse env variables or config file to find program config params

    Function that search and parse program configuration parameters in the
    program environment variables first and the in a config file.
    If at least one of the config parameters is not found a KeyError exception
    is thrown. If a parameter could not be parsed, a ValueError is thrown.

    If parsing succeeded, the function returns a ConfigParser object
    with config parameters
    """

    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")

    config_params = {}
    config_params["ip"] = os.getenv('SERVER_ADDRESS', config["SERVER"]["IP"])
    config_params["port"] = int(os.getenv('SERVER_ADDRESS', config["SERVER"]["PORT"]))

    return config_params


def main():
    params = initialize_config()

    ip = params["ip"]
    port = params["port"]

    client = Client(ip, port)
    client.run()


if __name__ == "__main__":
    sleep(3)
    main()