from app.container import ServiceContainer,EnumMode
from app.utils import Logic
from datetime import datetime
import time

TIME_OUT_WAIT_ARM_RESEND = 4

class StageTransform:
    def __init__(self,services:ServiceContainer):
        self.services =  services

    def run(self):   
        product = self.services.obj_choose_product.get_choose_product().data
        result_run_product = self.services.obj_point_service.get_all_xyz_by_product_id(product).data
        print(result_run_product)
        result_path = self.services.obj_point_service.get_retrain_paths_by_product_frame(product,0).data
        print("path:",result_path)
        for frame_id, points in result_run_product.items():
            i = 0
            for point in points:
                path = result_path[i]
                print("duong dan",path)
                i+=1
                point_id = point["point_id"]
                x = point["x"]
                y = point["y"]
                z = point["z"]
                cmd = f"cmd:{x},{y},{z},{80}"
                self.services.obj_manager_serial.send_data(cmd)
                status_send_arm = Logic.wait_for_specific_data(self.services.obj_manager_serial,cmd,TIME_OUT_WAIT_ARM_RESEND)
                if status_send_arm:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    name  = f"image_{timestamp}.jpg"
                    self.services.obj_camera.capture_image_trigger(path,name,1)
 
                elif not status_send_arm:
                    self.services.set_mode(EnumMode.MODE_DEAFAULT)
                    time.sleep(2)


