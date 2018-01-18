from abc import abstractmethod
from enum import Enum
from threading import Event
from typing import List

from com.ic_interface import ICInterface
from com.ui_interface import UIInterface
from mgmt import mgmt_utils
from target_recognition import TargetRecognition


class Context:
    def __init__(self):
        # handles
        self.ic_interface: ICInterface = None
        self.ui_interface: UIInterface = None
        self.target_recognition: TargetRecognition = None

        # infos
        self.x_position: int = None
        self.z_position: int = None

        self._x_offset: int = None
        self._z_position_on_target = None

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
        self.load_present = False

    @abstractmethod
    def run(self):
        pass

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
        if self.steps_done < self.step_count_to_wait_for:
            return StepResult.SYNC
        self.steps_done = 0

class CancleStep(Step):

    def __init__(self, context: Context, steps_to_cancle: List[Step]):
        super(CancleStep, self).__init__(context)
        self.steps_to_cancel = steps_to_cancle

    def run(self):
        for step in self.steps_to_cancel:
            step.cancel()