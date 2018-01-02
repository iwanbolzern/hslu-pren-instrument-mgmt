from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import List

from com.ic_interface import ICInterface
from com.ui_interface import UIInterface


class Context:
    def __init__(self):
        self.ic_interface = None
        self.ui_interface = None

class Step:

    def __init__(self, context: Context):
        self.context = context
        self.next_steps = None
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

class WaitForInitStep(Step):

    def __init__(self, context: Context):
        super(WaitForInitStep, self).__init__(context)

class WaitForStartStep(Step):

    def __init__(self, context: Context):
        super(WaitForStartStep, self).__init__(context)

class CoreProcess:

    def __init__(self):
        self.process = []
        self.start_steps = None
        self.step_thread_pool = ThreadPoolExecutor()
        self.context = None

        self._create_context()
        self._init_steps()

    def _create_context(self):
        self.context = Context()
        self.context.ui_interface = UIInterface()
        self.context.ic_interface = ICInterface()

    def _init_steps(self):
        wait_for_init_step = WaitForInitStep(self.context)
        wait_for_start_step = WaitForStartStep(self.context)

        cancle_wait_for_start_step = CancleStep(self.context, [wait_for_start_step])
        cancle_wait_for_init_step = CancleStep(self.context, [wait_for_init_step])

        # connect steps
        wait_for_init_step.set_next_steps([cancle_wait_for_start_step])
        wait_for_start_step.set_next_steps([cancle_wait_for_init_step])

        # set start steps
        self._set_start_steps([wait_for_start_step, wait_for_init_step])

    def start_process(self):
        for step in self.start_steps:
            future = self.step_thread_pool.submit(step.run)
            future.add_done_callback(lambda: self._step_done_callback(step))

    def _step_done_callback(self, step):
        if not step.is_canceled:
            for step in step.next_steps:
                future = self.step_thread_pool.submit(step.run)
                future.add_done_callback(lambda: self._step_done_callback(step))

    def _set_start_steps(self, start_steps):
        self.start_steps = start_steps

