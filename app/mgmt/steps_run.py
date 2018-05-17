import time
from threading import Event

from com.ic_interface import Direction, MagnetDirection, DirectionTele
from mgmt import pos_callculation
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
        log.debug('UpdatePositionStep done')

    def __position_update_received(self, x_position, z_position):
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
        log.debug('DriveXToLoadPickup run called')
        self.event = Event()
        self.context.ic_interface.drive_distance_async(Config().x_distance_to_load_pickup,
                                                       Config().x_speed_to_load_pickup,
                                                       Direction.Forward,
                                                       lambda: self.event.set())
        self.event.wait()
        log.debug('DriveXToLoadPickup done')


class DriveZToLoadPickup(Step):

    def __init__(self, context: Context):
        super(DriveZToLoadPickup, self).__init__(context)
        self.event = None

    def run(self):
        log.debug('DriveZToLoadPickup run called')
        #wait to start of move tele
        self.event = Event()
        self.context.register_position_callback(self.__position_update_received)
        self.event.wait()

        log.debug('DriveZToLoadPickup start move tele')
        #drive tele
        self.event = Event()
        self.context.ic_interface.move_tele_async(Config().z_distance_to_load_pickup,
                                                  DirectionTele.Extend,
                                                  lambda: self.event.set())
        self.event.wait()
        log.debug('DriveZToLoadPickup done')

    def __position_update_received(self, x_position, z_position):
        if x_position >= Config().x_position_to_start_load_pickup:
            self.context.unregister_position_callback(self.__position_update_received)
            self.event.set()


class EnforceMagnetStep(Step):

    def __init__(self, context: Context):
        super(EnforceMagnetStep, self).__init__(context)
        self.event = None

    def run(self):
        log.debug('EnforceMagnetStep run called')
        # wait until magnet is near enough
        self.event = Event()
        self.context.register_position_callback(self.__position_update_received)
        self.event.wait()

        log.debug('EnforceMagnetStep start enforce magnet')
        #enable magnet
        self.context.ic_interface.enable_magnet(MagnetDirection.Enforce)
        log.debug('EnforceMagnetStep done')

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
        log.debug('DriveZToTravelPosition run called')
        #drive tele
        self.event = Event()
        self.context.ic_interface.move_tele_async(Config().z_travel_position,
                                                  DirectionTele.Retract,
                                                  lambda: self.event.set())
        self.event.wait()
        log.debug('DriveZToTravelPosition done')


class DisableMagnet(Step):

    def __init__(self, context: Context):
        super(DisableMagnet, self).__init__(context)

    def run(self):
        log.debug('DisableMagnet run called')
        self.context.ic_interface.disable_magnet()
        log.debug('DisableMagnet done')


class DriveToUnloadPlainInterrupt(Step):

    def __init__(self, context: Context):
        super(DriveToUnloadPlainInterrupt, self).__init__(context)
        self.event = None

    def run(self):
        log.debug('DriveToUnloadPlainInterrupt run called')
        #wait until tele is high enough
        self.event = Event()
        self.context.register_position_callback(self._position_update_received)
        self.event.wait()

        log.debug('DriveToUnloadPlainInterrupt start drive')
        #drive jog
        self.context.ic_interface.drive_jog(Config().travel_speed, Direction.Forward)

        # register image recognition callback and wait
        self.event = Event()
        self.context.target_recognition.register_callback(self._unload_plain_interrupt)
        self.context.target_recognition.start()
        self.event.wait()

        log.debug('DriveToUnloadPlainInterrupt done')

    def _position_update_received(self, x_position, z_position):
        if z_position >= Config().z_position_to_start_travel:
            self.context.unregister_position_callback(self._position_update_received)
            self.event.set()

    def _unload_plain_interrupt(self, x_centroid, y_centroid):
        log.debug('_unload_plain_interrupt called')
        self.context.abs_x_offset = self.context.position_calculation\
            .calc_abs_x_offset_from_centroid(self.context.x_position_abs, x_centroid)
        self.context.target_recognition.unregister_callback(self._unload_plain_interrupt)
        self.event.set()
        log.debug('_unload_plain_interrupt event set')


class AdjustXPosition(Step):

    def __init__(self, context: Context):
        super(AdjustXPosition, self).__init__(context)
        self.event = None

    def run(self):
        log.debug('AdjustXPosition run called')
        # register image recognition callback
        self.context.target_recognition.register_callback(self._unload_plain_interrupt)

        #while abs(self.context.abs_x_offset) > Config().max_adjust_offset:
        log.debug('AdjustXPosition offset procedure started with offset adjustment of '
                  'abs_x_offset: {} and rel_x_offset: {}'.format(self.context.abs_x_offset,
                                                                 self.context.rel_x_offset))
        self.event = Event()
        direction = Direction.Forward if self.context.rel_x_offset > 0 else Direction.Backward
        self.context.ic_interface.drive_distance_async(abs(self.context.rel_x_offset),
                                                       Config().adjust_speed, direction,
                                                       lambda: self.event.set())
        self.event.wait()

        self.context.target_recognition.unregister_callback(self._unload_plain_interrupt)
        self.context.target_recognition.stop()

        log.debug('AdjustXPosition done')

    def _unload_plain_interrupt(self, x_centroid, y_centroid):
        self.context.abs_x_offset = self.context.position_calculation.calc_abs_x_offset_from_centroid(x_centroid)


class DriveZToUnloadPosition(Step):

    def __init__(self, context: Context):
        super(DriveZToUnloadPosition, self).__init__(context)
        self.event = None

    def run(self):
        log.debug('DriveZToUnloadPosition run called')
        # register image recognition callback and wait until plain is near enough
        self.event = Event()
        self.context.target_recognition.register_callback(self._unload_plain_interrupt)
        self.event.wait()

        log.debug('DriveZToUnloadPosition move tele started: z_position_on_target {}'
                  .format(self.context.z_position_on_target))
        #drive tele
        self.event = Event()
        self.context.ic_interface.move_tele_async(self.context.z_position_on_target,
                                                  DirectionTele.Extend,
                                                  lambda: self.event.set())
        self.event.wait()
        log.debug('DriveZToUnloadPosition done')

    def _unload_plain_interrupt(self, x_centroid, y_centroid):
        self.context.abs_x_offset = self.context.position_calculation.calc_abs_x_offset_from_centroid(x_centroid)
        if abs(self.context.abs_x_offset) < Config().adjust_offset_to_start_tele:
            self.context.target_recognition.unregister_callback(self._unload_plain_interrupt)
            self.event.set()


class ReleaseMagnet(Step):

    def __init__(self, context: Context):
        super(ReleaseMagnet, self).__init__(context)
        self.event = None

    def run(self):
        log.debug('ReleaseMagnet run called')
        self.context.ic_interface.enable_magnet(MagnetDirection.Release)
        log.debug('ReleaseMagnet done')


class DriveZToEndPosition(Step):

    def __init__(self, context: Context):
        super(DriveZToEndPosition, self).__init__(context)
        self.event = None

    def run(self):
        log.debug('DriveZToEndPosition run called')
        # drive tele
        self.event = Event()
        self.context.ic_interface.move_tele_async(self.context.z_position_rel,
                                                  DirectionTele.Retract,
                                                  lambda: self.event.set())
        self.event.wait()
        log.debug('DriveZToEndPosition done')


class DriveToEnd(Step):
    def __init__(self, context: Context):
        super(DriveToEnd, self).__init__(context)
        self.event = None

    def run(self):
        log.debug('DriveToEnd run called')
        # wait until tele is high enough
        self.event = Event()
        self.context.register_position_callback(self._position_update_received)
        self.event.wait()

        log.debug('DriveToEnd start drive')
        # drive to end
        self.event = Event()
        remaining_distance = pos_callculation.calc_x_rel(self.context.x_position_abs,
                                                         Config().x_end_position_abs - self.context.x_position_abs)
        self.context.ic_interface.drive_to_end_async(remaining_distance,
                                                     Config().drive_to_end_speed,
                                                     Direction.Forward,
                                                     lambda: self.event.set())
        self.event.wait()
        log.debug('DriveToEnd done')

    def _position_update_received(self, x_position, z_position):
        if z_position >= Config().z_position_to_drive_to_end:
            self.context.unregister_position_callback(self._position_update_received)
            self.event.set()