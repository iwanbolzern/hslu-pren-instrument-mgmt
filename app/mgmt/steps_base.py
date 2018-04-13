from abc import abstractmethod
from enum import Enum
from threading import Event
from typing import List, Callable

from com.ic_interface import ICInterface
from com.ui_interface import UIInterface
from mgmt import mgmt_utils
from target_recognition import TargetRecognition
from mgmt_utils import log


class Context:
    def __init__(self):
        # handles
        self.ic_interface = ICInterface()
        self.ui_interface = UIInterface()
        self.target_recognition = TargetRecognition()

        # infos
        self.load_present = True
        self.x_position = 0
        self.z_position = 0

        self._x_offset = None
        self._z_position_on_target = None

        # register position callbacks
        self.position_callbacks = []
        self.ic_interface.register_position_callback(self.__position_update)

    def __position_update(self, x_offset, z_offset):
        self.x_position += x_offset
        self.z_position += z_offset

        for callback in self.position_callbacks:
            callback(self.x_position, self.z_position)

    def register_position_callback(self, callback: Callable[[int, int], None]):
        self.position_callbacks.append(callback)

    def unregister_position_callback(self, callback: Callable[[int, int], None]):
        self.position_callbacks.remove(callback)

    @property
    def z_position_on_target(self):
        return self._z_position_on_target

    @property
    def x_offset(self):
        return self._x_offset

    @x_offset.setter
    def x_offset(self, value):
        self._x_offset = value
        self._z_position_on_target = mgmt_utils.get_z_distance(value)



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
        self.run()

    def cancel(self):
        self.is_canceled = True

    def set_next_steps(self, next_steps):
        self.next_steps = next_steps

class SyncStep(Step):

    def __init__(self, context: Context, step_count_to_wait_for: int):
        super(SyncStep, self).__init__(context)
        self.step_count_to_wait_for = step_count_to_wait_for
        self.steps_done = 0
        self.wait_event = Event()

    def run(self):
        self.steps_done += 1
        log.debug('SyncStep run called: steps_done ' + self.steps_done)
        if self.steps_done < self.step_count_to_wait_for:
            return StepResult.SYNC
        self.steps_done = 0
        log.debug('SyncStep done')

class CancleStep(Step):

    def __init__(self, context: Context, steps_to_cancle: List[Step]):
        super(CancleStep, self).__init__(context)
        self.steps_to_cancel = steps_to_cancle

    def run(self):
        log.debug('CancelStep run called: step_to_cancel_count ' + len(self.steps_to_cancel))
        for step in self.steps_to_cancel:
            step.cancel()
