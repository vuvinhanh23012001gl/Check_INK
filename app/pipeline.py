from app.stages import StageIngest
from app.container import ServiceContainer
import threading
import time
from enum import Enum
class Pipeline:
    def __init__(self,services: ServiceContainer):
        self.services = services
        self.stage_ingest = StageIngest(services)
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
               self.stage_ingest.run()

            
