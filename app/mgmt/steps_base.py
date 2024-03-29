from abc import abstractmethod
from enum import Enum
from threading import Event, RLock
from typing import List, Callable

from com.ic_interface import ICInterface
from com.ui_interface import UIInterface
from mgmt.pos_callculation import PosCalculation
from target_recognition_pi import TargetRecognition
from mgmt_utils import log


class Context:
    def __init__(self):
        # handles
        self.ic_interface = ICInterface()
        self.ui_interface = UIInterface()
        self.target_recognition = TargetRecognition()
        self.position_calculation = PosCalculation()

        # infos
        self.load_present = False
        self.x_position_rel = 0
        self.z_position_rel = 0
        self.x_position_abs = 0
        self.z_position_abs = 0

        self.__abs_x_offset = None
        self.__z_position_on_target = None

        # register position callbacks
        self.position_callbacks = []
        self.ic_interface.register_position_callback(self.__position_update)

    def reset_position(self):
        self.load_present = False
        self.x_position_rel = 0
        self.z_position_rel = 0
        self.x_position_abs = 0
        self.z_position_abs = 0

        self.__abs_x_offset = None
        self.__z_position_on_target = None

    def __position_update(self, x_offset, z_offset):
        self.x_position_rel += x_offset
        self.z_position_rel += z_offset
        self.x_position_abs = self.position_calculation.calc_x_abs(self.x_position_rel)
        self.z_position_abs = self.position_calculation.calc_z_abs(self.x_position_rel, self.z_position_rel)
        #print('x_position: {}, z_position: {}'.format(self.x_position_abs, self.z_position_abs))
        for callback in self.position_callbacks:
            callback(self.x_position_abs, self.z_position_abs)

    def register_position_callback(self, callback: Callable[[int, int], None]):
        self.position_callbacks.append(callback)

    def unregister_position_callback(self, callback: Callable[[int, int], None]):
        self.position_callbacks.remove(callback)

    @property
    def z_position_on_target(self):
        return self.__z_position_on_target

    @property
    def rel_x_offset(self):
        return self.position_calculation.calc_x_rel(self.x_position_abs, self.__abs_x_offset)

    @property
    def abs_x_offset(self):
        return self.__abs_x_offset

    @abs_x_offset.setter
    def abs_x_offset(self, value):
        self.__abs_x_offset = value
        self.__z_position_on_target = self.position_calculation.calc_z_abs(self.x_position_rel + self.rel_x_offset,
                                                                  self.z_position_rel)


class StepResult(Enum):
    SUCCESS = 0
    SYNC = 1
    END = 2


class Step:

    def __init__(self, context: Context):
        self.context = context
        self.next_steps = []
        self.is_canceled = False

    @abstractmethod
    def run(self):
        pass

    def start(self):
        self.is_canceled = False
        return self.run()

    def cancel(self):
        self.is_canceled = True

    def set_next_steps(self, next_steps):
        self.next_steps = next_steps

class SyncStep(Step):

    def __init__(self, context: Context, step_count_to_wait_for: int):
        super(SyncStep, self).__init__(context)
        self.step_count_to_wait_for = step_count_to_wait_for
        self.steps_done = 0
        self.lock = RLock()

    def run(self):
        self.lock.acquire(True)
        self.steps_done += 1
        log.debug('SyncStep run called: steps_done ' + str(self.steps_done))
        if self.steps_done < self.step_count_to_wait_for:
            self.lock.release()
            return StepResult.SYNC
        self.steps_done = 0
        self.lock.release()
        log.debug('SyncStep done')

class CancleStep(Step):

    def __init__(self, context: Context, steps_to_cancle: List[Step]):
        super(CancleStep, self).__init__(context)
        self.steps_to_cancel = steps_to_cancle

    def run(self):
        log.debug('CancelStep run called: step_to_cancel_count ' + str(len(self.steps_to_cancel)))
        for step in self.steps_to_cancel:
            step.cancel()
