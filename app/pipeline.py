from app.stages import StagePreprocess, StageTransform, StageExport
from app.container import ServiceContainer, EnumMode
from app.config import ModeState
from app.core.context import RuntimePipelineState
import threading
import time

class Pipeline:
    def __init__(self,services: ServiceContainer):

        self.services = services
        self.stage_ingest = StagePreprocess(self.services)
        self.stage_transform = StageTransform(self.services)
        self.stage_export   =  StageExport(self.services)

        self.running = False
        self.awaiting_reset = True
        self._last_connections = None
        self._previous_reset = None
        self.thread = threading.Thread(
            target=self._run_pipeline,
            daemon=True,
            name="RunPipeline"
        )
        self.open_task_pipeline()
        self.thread.start()

    def open_task_pipeline(self):
        self.running = True

    def stop_task_pipeline(self):
        self.running = False
        self.services.runtime_state.request_stop()

    def _publish_log(self, message: str) -> None:
        """Gửi log pipeline vào ô ``log_judment`` qua queue hiện có."""
        self.services.queue_log_send_client.put({
            "type": "log_Home",
            "message": message,
        })

    def _read_runtime_status(self) -> None:
        """Đọc trạng thái phần cứng và trạng thái IAI, không điều khiển phần cứng."""
        com_connected = self.services.obj_manager_serial.is_running()
        camera_connected = self.services.obj_camera.get_is_connect()
        self.services.runtime_state.set_connections(com_connected, camera_connected)
        connections = (com_connected, camera_connected)
        if self._last_connections is not None and connections != self._last_connections:
            if not com_connected:
                self._publish_log("❌ Mất kết nối COM, đang chờ kết nối lại.")
            if not camera_connected:
                self._publish_log("❌ Mất kết nối camera, đang chờ kết nối lại.")
            if com_connected and camera_connected:
                self._publish_log("✅ COM và camera đã kết nối lại.")
        self._last_connections = connections
        iai_status = self.services.obj_iai_control.get_status()
        if iai_status == ModeState.STOP:
            self.services.runtime_state.set_pipeline_state(RuntimePipelineState.ERROR)
        elif self.services.runtime_state.is_judgment_running():
            self.services.runtime_state.set_pipeline_state(RuntimePipelineState.RUNNING)
        elif self.services.obj_iai_control.get_pause_because_sensor_safety():
            self.services.runtime_state.set_pipeline_state(RuntimePipelineState.WARNING)
        elif self.services.obj_iai_control.get_is_origin():
            self.services.runtime_state.set_pipeline_state(RuntimePipelineState.READY)
        else:
            self.services.runtime_state.set_pipeline_state(RuntimePipelineState.WAIT_START)

    def _start_cycle_after_reset(self) -> None:
        """Chuyển sang Stage 1 sau tín hiệu Reset của IAI."""
        if self.services.get_mode() != EnumMode.MODE_IDLE:
            return
        com_connected, camera_connected = self.services.runtime_state.get_connections()
        if not com_connected or not camera_connected:
            return
        reset_pressed = bool(self.services.obj_iai_control.get_btn_inp_reset())
        reset_rising = reset_pressed and self._previous_reset is False
        self._previous_reset = reset_pressed
        if self.awaiting_reset:
            if not reset_rising:
                return
            self.awaiting_reset = False
            self.services.runtime_state.clear_stop()
        if self.services.obj_iai_control.get_status() in {
            ModeState.WAIT_AUTO,
            ModeState.AUTO,
        }:
            self.services.set_mode(EnumMode.MODE_PREPOCESS)


    def _run_pipeline(self):
        while self.running and not self.services.runtime_state.is_stop_requested():
            self._read_runtime_status()
            if self.running:
                mode = self.services.get_mode() 
                if mode == EnumMode.MODE_IDLE:
                    self._start_cycle_after_reset()
                    time.sleep(1)
                elif (mode == EnumMode.MODE_PREPOCESS): 
                    print("--Vào chế độ chuẩn bị chạy --") 
                    try:
                        self.stage_ingest.run()
                    except Exception as error:
                        self._publish_log(f"❌ Stage 1 lỗi: {error}")
                        self.awaiting_reset = True
                        self.services.set_mode(EnumMode.MODE_IDLE)

                elif (mode == EnumMode.MODE_TRANSFORM):
                    print("----Vào chế độ chạy -----")
                    try:
                        self.stage_transform.run()
                    except Exception as error:
                        self._publish_log(f"❌ Stage 2 lỗi: {error}")
                        self.awaiting_reset = True
                        self.services.set_mode(EnumMode.MODE_IDLE)
                    try:
                        self.stage_export.run()
                        self.awaiting_reset = True
                    except Exception as error:
                        self._publish_log(f"❌ Stage 3 lỗi: {error}")
                        self.awaiting_reset = True
                        self.services.set_mode(EnumMode.MODE_IDLE)
                elif (mode == EnumMode.MODE_EXPORT):
                    print("----Vào chế độ hoàn thiện-----")
                    
                time.sleep(1)


            

