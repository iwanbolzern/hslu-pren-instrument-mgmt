

# create config file
from mgmt_utils.config import Config

config = Config()

config.x_distance_to_load_pickup = 60
config.x_speed_to_load_pickup = 100
config.x_position_to_start_load_pickup = 20
config.z_distance_to_load_pickup = 20
config.x_position_to_enable_magnet_load_pickup = 50
config.z_position_to_enable_magnet_load_pickup = 50
config.z_travel_position = 30
config.z_position_to_start_travel = 20
config.travel_speed = 100

config.max_adjust_offset = 2
config.adjust_speed = 100
config.adjust_offset_to_start_tele = 50

config.z_end_position = 0
config.z_position_to_drive_to_end = 40

config.save_config()