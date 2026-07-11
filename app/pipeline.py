from app.stages import StagePreprocess,StageTransform,StageExport
from app.container import ServiceContainer
from app.container import ServiceContainer,EnumMode
import threading
import time

class Pipeline:
    def __init__(self,services: ServiceContainer):

        self.services = services
        self.stage_ingest = StagePreprocess(self.services)
        self.stage_transform = StageTransform(self.services)
        self.stage_export   =  StageExport(self.services)

        self.running = False
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


    def _run_pipeline(self):
        while True:
            if self.running:
                mode = self.services.get_mode() 
                if (mode == EnumMode.MODE_PREPOCESS): 
                    print("--Vào chế độ chuẩn bị chạy --") 
                    self.stage_ingest.run()

                elif (mode == EnumMode.MODE_TRANSFORM):
                    print("----Vào chế độ chạy -----")
                    self.stage_transform.run()

                elif (mode == EnumMode.MODE_EXPORT):
                    print("----Vào chế độ hoàn thiện-----")
                    
                time.sleep(1)


            

