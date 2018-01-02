from abc import abstractmethod
from typing import List

from com.ic_interface import ICInterface
from com.ui_interface import UIInterface


class Context:
    def __init__(self):
        self.ic_interface: ICInterface = None
        self.ui_interface: UIInterface = None


class Step:

    def __init__(self, context: Context):
        self.context = context
        self.next_steps = []
        self.is_canceled = False

    @abstractmethod
    def run(self):
        pass

    def cancel(self):
        self.is_canceled = True

    def set_next_steps(self, next_steps):
        self.next_steps = next_steps

class CancleStep(Step):

    def __init__(self, context: Context, steps_to_cancle: List[Step]):
        super(CancleStep, self).__init__(context)
        self.steps_to_cancel = steps_to_cancle

    def run(self):
        for step in self.steps_to_cancel:
            step.cancel()