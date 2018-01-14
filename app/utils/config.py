import configparser, logging
from enum import Enum

import pickle

from utils.singleton import Singleton
import argparse
from pathlib import Path


class Environment(Enum):
    pi = 1
    win = 2

    @classmethod
    def fromstring(cls, str):
        return getattr(cls, str.lower(), None)


class Config(metaclass=Singleton):

    FILE_PATH = r'../mgmt-conf.pkl'

    def __init__(self):
        self.conf_dict: dict = {}
        self.load_config()

        # path length (not x distance)
        self.x_distance_to_load_pickup = self.conf_dict['XDistanceToLoadPickup']
        self.x_speed_to_load_pickup = self.conf_dict['SpeedToLoadPickup']
        self.x_position_to_start_load_pickup = self.conf_dict['XToStartLoadPickup']
        self.z_distance_to_load_pickup = self.conf_dict['ZDistanceToLoadPickup']
        self.x_position_to_enable_magnet_load_pickup = self.conf_dict['XPosToEnableMagnetLoadPickup']
        self.z_position_to_enable_magnet_load_pickup = self.conf_dict['ZPosToEnableMagnetLoadPickup']
        self.z_travel_position = self.conf_dict['ZTravelPosition']
        self.z_position_to_start_travel = self.conf_dict['ZPositionToStartTravel']
        self.travel_speed = self.conf_dict['TravelSpeed']

        self.max_adjust_offset = self.conf_dict['MaxAdjustOffset']
        self.adjust_speed = self.conf_dict['AdjustSpeed']
        self.adjust_offset_to_start_tele = self.conf_dict['AdjustDistanceToStartTele']

        # do not use log.info(..) you will end in hell
        print("Started with config: {}".format(Config.FILE_PATH))

    def save_config(self):
        with open(Config.FILE_PATH, 'wb') as f:
            pickle.dump(self.conf_dict, f, pickle.HIGHEST_PROTOCOL)

    def load_config(self):
        with open(Config.FILE_PATH, 'rb') as f:
            self.conf_dict = pickle.load(f)




