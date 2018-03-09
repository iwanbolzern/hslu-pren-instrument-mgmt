from threading import Event

import math

from com.ic_interface import Direction, MagnetDirection
from mgmt import mgmt_utils
from mgmt.steps_base import Step, Context
from mgmt_utils import log
from mgmt_utils.config import Config


class WaitForStartStep(Step):

    def __init__(self, context: Context):
        super(WaitForStartStep, self).__init__(context)
        self.event = None

    def run(self):
        log.debug('WaitForStartStep started')
        self.event = Event()
        self.context.ui_interface.register_start_once(self.set_event)
        log.info('Waiting for start callback')
        self.event.wait()
        if not self.is_canceled:
            log.info('Start callback received')

    def set_event(self):
        self.event.set()

    def cancel(self):
        super(WaitForStartStep, self).cancel()
        self.context.ui_interface.unregister_start(self.set_event)
        self.event.set()


class UpdatePositionStep(Step):

    def __init__(self, context: Context):
        super(UpdatePositionStep, self).__init__(context)
        self.event = None

    def run(self):
        log.debug('UpdatePositionStep started')
        self.context.register_position_callback(self.__position_update_received)

        #prevent step from end
        self.event = Event()
        self.event.wait()

    def __position_update_received(self, x_position, z_position):
        self.context.x_position = x_position
        self.context.z_position = z_position
        if self.context.load_present:
            self.context.ui_interface.send_position_update(x_position, z_position)

    def cancel(self):
        super(UpdatePositionStep, self).cancel()
        self.context.unregister_position_callback(self.__position_update_received)
        self.event.set()


class DriveXToLoadPickup(Step):

    def __init__(self, context: Context):
        super(DriveXToLoadPickup, self).__init__(context)
        self.event = None

    def run(self):
        self.event = Event()
        self.context.ic_interface.drive_distance_async(Config().x_distance_to_load_pickup,
                                                       Config().x_speed_to_load_pickup,
                                                       Direction.Forward,
                                                       lambda: self.event.set())
        self.event.wait()


class DriveZToLoadPickup(Step):

    def __init__(self, context: Context):
        super(DriveZToLoadPickup, self).__init__(context)
        self.event = None

    def run(self):
        #wait to start of move tele
        self.event = Event()
        self.context.register_position_callback(self.__position_update_received)
        self.event.wait()

        #drive tele
        self.event = Event()
        self.context.ic_interface.move_tele_async(Config().z_distance_to_load_pickup,
                                                  Direction.Forward,
                                                  lambda: self.event.set())
        self.event.wait()

    def __position_update_received(self, x_position, z_position):
        if x_position >= Config().x_position_to_start_load_pickup:
            self.context.unregister_position_callback(self.__position_update_received)
            self.event.set()


class EnforceMagnetStep(Step):

    def __init__(self, context: Context):
        super(EnforceMagnetStep, self).__init__(context)
        self.event = None

    def run(self):
        # wait until magnet is near enough
        self.event = Event()
        self.context.register_position_callback(self.__position_update_received)
        self.event.wait()

        #enable magnet
        self.context.ic_interface.enable_magnet(MagnetDirection.Enforce)

    def __position_update_received(self, x_position, z_position):
        if x_position >= Config().x_position_to_enable_magnet_load_pickup and \
                z_position >= Config().z_position_to_enable_magnet_load_pickup:
            self.context.unregister_position_callback(self.__position_update_received)
            self.event.set()


class DriveZToTravelPosition(Step):

    def __init__(self, context: Context):
        super(DriveZToTravelPosition, self).__init__(context)
        self.event = None

    def run(self):
        #drive tele
        self.event = Event()
        self.context.ic_interface.move_tele_async(Config().z_travel_position,
                                                  Direction.Backward,
                                                  lambda: self.event.set())
        self.event.wait()


class DriveToUnloadPlainInterrupt(Step):

    def __init__(self, context: Context):
        super(DriveToUnloadPlainInterrupt, self).__init__(context)
        self.event = None

    def run(self):
        #wait until tele is high enough
        self.event = Event()
        self.context.register_position_callback(self._position_update_received)
        self.event.wait()

        #drive jog
        self.context.ic_interface.drive_jog(Config().travel_speed, Direction.Forward)

        # register image recognition callback and wait
        self.event = Event()
        self.context.target_recognition.register_callback(self._unload_plain_interrupt)
        self.context.target_recognition.start()
        self.event.wait()

    def _position_update_received(self, x_position, z_position):
        if z_position >= Config().z_position_to_start_travel:
            self.context.unregister_position_callback(self._position_update_received)
            self.event.set()

    def _unload_plain_interrupt(self, x_centroid, y_centroid):
        self.context.x_offset = mgmt_utils.get_x_offset(x_centroid)
        self.context.target_recognition.unregister_callback(self._unload_plain_interrupt)
        self.context.target_recognition.stop()
        self.event.set()


class AdjustXPosition(Step):

    def __init__(self, context: Context):
        super(AdjustXPosition, self).__init__(context)
        self.event = None

    def run(self):
        # register image recognition callback
        self.context.target_recognition.register_callback(self._unload_plain_interrupt)
        self.context.target_recognition.start()

        while math.abs(self.context.x_offset) > Config().max_adjust_offset:
            self.event = Event()
            direction = Direction.Forward if self.context.x_offset > 0 else Direction.Backward
            self.context.ic_interface.drive_distance_async(math.abs(self.context.x_offset),
                                                           Config().adjust_speed, direction,
                                                           lambda: self.event.set())
            self.event.wait()

    def _unload_plain_interrupt(self, x_centroid, y_centroid):
        self.context.x_offset = mgmt_utils.get_x_offset(x_centroid)

class DriveZToUnloadPosition(Step):

    def __init__(self, context: Context):
        super(DriveZToUnloadPosition, self).__init__(context)
        self.event = None

    def run(self):
        # register image recognition callback and wait until plain is near enough
        self.event = Event()
        self.context.target_recognition.register_callback(self._unload_plain_interrupt)
        self.context.target_recognition.start()
        self.event.wait()

        #drive tele
        self.event = Event()
        self.context.ic_interface.move_tele_async(self.context.z_position_on_target,
                                                  Direction.Forward,
                                                  lambda: self.event.set())
        self.event.wait()

    def _unload_plain_interrupt(self, x_centroid, y_centroid):
        self.context.x_offset = mgmt_utils.get_x_offset(x_centroid)
        if math.abs(self.context.x_offset) < self.adjust_offset_to_start_tele:
            self.context.target_recognition.unregister_callback(self._unload_plain_interrupt)
            self.event.set()

class ReleaseMagnet(Step):

    def __init__(self, context: Context):
        super(ReleaseMagnet, self).__init__(context)
        self.event = None

    def run(self):
        self.context.ic_interface.enable_magnet(MagnetDirection.Release)


class DriveZToEndPosition(Step):

    def __init__(self, context: Context):
        super(DriveZToEndPosition, self).__init__(context)
        self.event = None

    def run(self):
        # drive tele
        self.event = Event()
        self.context.ic_interface.move_tele_async(self.context.z_position_on_target -
                                                  mgmt_utils.z_end_position,
                                                  Direction.Backward,
                                                  lambda: self.event.set())
        self.event.wait()


class DriveToEnd(Step):
    def __init__(self, context: Context):
        super(DriveToEnd, self).__init__(context)
        self.event = None

    def run(self):
        # wait until tele is high enough
        self.event = Event()
        self.context.register_position_callback(self._position_update_received)
        self.event.wait()

        # drive to end
        self.event = Event()
        self.context.ic_interface.drive_to_end_async(100,
                                                     mgmt_utils.drive_to_end_speed,
                                                     Direction.Forward,
                                                     lambda: self.event.set())
        self.event.wait()
        self.context.ui_interface.send_log()

    def _position_update_received(self, x_position, z_position):
        if z_position >= Config().z_position_to_drive_to_end:
            self.context.unregister_position_callback(self._position_update_received)
            self.event.set()