import configparser, logging
import json
from enum import Enum

import pickle

from mgmt_utils.singleton import Singleton
import argparse
from pathlib import Path


class Environment(Enum):
    pi = 1
    win = 2

    @classmethod
    def fromstring(cls, str):
        return getattr(cls, str.lower(), None)


class Config(metaclass=Singleton):

    FILE_PATH = r'../mgmt-conf.json'

    def __init__(self):

        # path length (not x distance)
        self.x_distance_to_load_pickup = None
        self.x_speed_to_load_pickup = None
        self.x_position_to_start_load_pickup = None
        self.z_distance_to_load_pickup = None
        self.x_position_to_enable_magnet_load_pickup = None
        self.z_position_to_enable_magnet_load_pickup = None
        self.z_travel_position = None
        self.z_position_to_start_travel = None
        self.travel_speed = None

        self.max_adjust_offset = None
        self.adjust_speed = None
        self.adjust_offset_to_start_tele = None

        self.z_end_position = None
        self.z_position_to_drive_to_end = None

        self.load_config()

        # do not use log.info(..) you will end in hell
        print("Started with config: {}".format(Config.FILE_PATH))

    def save_config(self):
        with open(Config.FILE_PATH, 'w') as f:
            json.dump(self.__dict__, f, indent=2)

    def load_config(self):
        with open(Config.FILE_PATH, 'rb') as f:
            self.__dict__ = json.load(f)




