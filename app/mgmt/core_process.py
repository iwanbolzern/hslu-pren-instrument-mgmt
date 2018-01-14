from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from typing import List

from app.com.ic_interface import ICInterface
from app.com.ui_interface import UIInterface
from mgmt.steps_base import Step, Context, CancleStep, StepResult, SyncStep
from mgmt.steps_init import WaitForInitStep, InitStep
from mgmt.steps_run import WaitForStartStep, DriveXToLoadPickup, DriveZToLoadPickup, EnableMagnetStep, \
    DriveZToTravelPosition
from target_recognition.target_recognition import TargetRecognition
from utils import log


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
        self.context.target_recognition = TargetRecognition()

    def _init_steps(self):
        wait_for_init_step = WaitForInitStep(self.context)
        init_step = InitStep(self.context)
        wait_for_start_step = WaitForStartStep(self.context)

        cancle_wait_for_start_step = CancleStep(self.context, [wait_for_start_step])
        cancle_wait_for_init_step = CancleStep(self.context, [wait_for_init_step])
        # steps for run
        drive_x_to_load_pickup_step = DriveXToLoadPickup(self.context)
        drive_z_to_load_pickup_step = DriveZToLoadPickup(self.context)
        enable_magnet_step = EnableMagnetStep(self.context)
        sync_pickup_steps = SyncStep(self.context, 3)
        drive_z_to_travel_position = DriveZToTravelPosition(self.context)


        # connect steps
        # init loop
        wait_for_init_step.set_next_steps([cancle_wait_for_start_step])
        cancle_wait_for_start_step.set_next_steps([init_step])
        init_step.set_next_steps([wait_for_start_step, wait_for_init_step])

        #start loop
        wait_for_start_step.set_next_steps([cancle_wait_for_init_step])
        cancle_wait_for_init_step.set_next_steps([drive_x_to_load_pickup_step,
                                                  drive_z_to_load_pickup_step,
                                                  enable_magnet_step])
        drive_x_to_load_pickup_step.set_next_steps([sync_pickup_steps])
        drive_z_to_load_pickup_step.set_next_steps([sync_pickup_steps])
        enable_magnet_step.set_next_steps([sync_pickup_steps])
        sync_pickup_steps.set_next_steps([drive_z_to_travel_position])


        # set start steps
        self._set_start_steps([wait_for_start_step, wait_for_init_step])

    def start_process(self):
        for step in self.start_steps:
            future = self.step_thread_pool.submit(step.run)
            future.add_done_callback(lambda x: self._step_done_callback(step, x.result()))

    def _step_done_callback(self, step, result):
        if not step.is_canceled:
            # do not start next steps if result is sync (SyncStep)
            if result == StepResult.SYNC:
                return
            elif not result:
                for step in step.next_steps:
                    future = self.step_thread_pool.submit(step.run)
                    future.add_done_callback(lambda x: self._step_done_callback(step, x.result()))

    def _set_start_steps(self, start_steps):
        self.start_steps = start_steps

