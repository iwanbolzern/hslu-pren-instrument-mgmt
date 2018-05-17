from asyncio import Future
from concurrent.futures import ThreadPoolExecutor

import functools

from mgmt.steps_base import Step, Context, CancleStep, StepResult, SyncStep
from mgmt.steps_init import WaitForInitStep, InitStep, BackToOriginStep
from mgmt.steps_run import WaitForStartStep, DriveXToLoadPickup, DriveZToLoadPickup, EnforceMagnetStep, \
    DriveZToTravelPosition, DisableMagnet, UpdatePositionStep, DriveToUnloadPlainInterrupt, AdjustXPosition, DriveZToUnloadPosition, \
    ReleaseMagnet, DriveZToEndPosition, DriveToEnd


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

    def _init_steps(self):
        wait_for_init_step = WaitForInitStep(self.context)
        init_step = InitStep(self.context)
        back_to_origin_step = BackToOriginStep(self.context)
        wait_for_start_step = WaitForStartStep(self.context)

        cancel_wait_for_start_step = CancleStep(self.context, [wait_for_start_step])
        cancel_wait_for_init_step = CancleStep(self.context, [wait_for_init_step])
        cancel_back_to_origin_step = CancleStep(self.context, [back_to_origin_step])
        # steps for run
        update_position_step = UpdatePositionStep(self.context)
        cancel_update_position_step = CancleStep(self.context, [update_position_step])
        drive_x_to_load_pickup_step = DriveXToLoadPickup(self.context)
        drive_z_to_load_pickup_step = DriveZToLoadPickup(self.context)
        enforce_magnet_step = EnforceMagnetStep(self.context)
        sync_pickup_steps = SyncStep(self.context, 3)
        drive_z_to_travel_position = DriveZToTravelPosition(self.context)
        disable_magnet_step = DisableMagnet(self.context)
        drive_to_unload_plain_interrupt = DriveToUnloadPlainInterrupt(self.context)
        travel_sync_step = SyncStep(self.context, 2)
        adjust_x_position = AdjustXPosition(self.context)
        drive_z_to_unload_position = DriveZToUnloadPosition(self.context)
        unload_sync_step = SyncStep(self.context, 2)
        release_magnet = ReleaseMagnet(self.context)
        drive_z_to_end_position = DriveZToEndPosition(self.context)
        drive_to_end = DriveToEnd(self.context)
        end_sync_step = SyncStep(self.context, 3)

        # connect steps
        # init loop
        wait_for_init_step.set_next_steps([cancel_wait_for_start_step])
        cancel_wait_for_start_step.set_next_steps([init_step])
        init_step.set_next_steps([wait_for_start_step, wait_for_init_step, back_to_origin_step])

        # back to origin loop
        back_to_origin_step.set_next_steps([back_to_origin_step])

        #start loop
        wait_for_start_step.set_next_steps([cancel_wait_for_init_step])
        cancel_wait_for_init_step.set_next_steps([update_position_step,
                                                  drive_x_to_load_pickup_step,
                                                  drive_z_to_load_pickup_step,
                                                  enforce_magnet_step])
        update_position_step.set_next_steps([end_sync_step])
        drive_x_to_load_pickup_step.set_next_steps([sync_pickup_steps])
        drive_z_to_load_pickup_step.set_next_steps([sync_pickup_steps])
        enforce_magnet_step.set_next_steps([sync_pickup_steps])
        sync_pickup_steps.set_next_steps([drive_z_to_travel_position,
                                          drive_to_unload_plain_interrupt])
        drive_z_to_travel_position.set_next_steps([disable_magnet_step])
        disable_magnet_step.set_next_steps([travel_sync_step])
        drive_to_unload_plain_interrupt.set_next_steps([travel_sync_step])
        travel_sync_step.set_next_steps([adjust_x_position])
        adjust_x_position.set_next_steps([drive_z_to_unload_position])
        drive_z_to_unload_position.set_next_steps([release_magnet])
        unload_sync_step.set_next_steps([release_magnet])
        release_magnet.set_next_steps([drive_z_to_end_position,
                                       drive_to_end])
        drive_z_to_end_position.set_next_steps([end_sync_step])
        drive_to_end.set_next_steps([cancel_update_position_step])
        cancel_update_position_step.set_next_steps([end_sync_step])
        end_sync_step.set_next_steps([wait_for_start_step,
                                      wait_for_init_step,
                                      back_to_origin_step])

        # set start steps
        self._set_start_steps([wait_for_start_step, wait_for_init_step, back_to_origin_step])

    def start_process(self):
        for step in self.start_steps:
            future = self.step_thread_pool.submit(step.start)
            future.add_done_callback(functools.partial(self._step_done_callback, step))

    def _step_done_callback(self, step: Step, done_future: Future):
        if not step.is_canceled:
            result = done_future.result()
            # do not start next steps if result is sync (SyncStep)
            if result == StepResult.SYNC:
                return
            elif not result:
                for next_step in step.next_steps:
                    future = self.step_thread_pool.submit(next_step.start)
                    future.add_done_callback(functools.partial(self._step_done_callback, next_step))

    def _set_start_steps(self, start_steps):
        self.start_steps = start_steps

