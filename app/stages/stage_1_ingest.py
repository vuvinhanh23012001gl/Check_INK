import time
from app.container import ServiceContainer,EnumMode
from app.utils import Logic
from datetime import datetime
TIME_OUT_WAIT_ARM_RESEND = 4

def data_format(arr_check):

    """Kiểm tra dữ liệu có đúng định dạng không và chuyển đổi về định dạng chuẩn.
    Ví dụ: 'cmd:1,2,3' -> 'cmd:001,002,003,ok'"""
    
    if not arr_check:
        print("❌ Dữ liệu bị lỗi hoặc trống, không có dữ liệu để so sánh.")
        return False
    if arr_check.startswith("cmd:"):
        raw_data = arr_check[4:].split(",")
        raw_data = [x.strip() for x in raw_data if x.strip() != ""]

        if not raw_data:
            print("❌ Không có dữ liệu tọa độ sau 'cmd:'")
            return False

        arr_covert_text = ["cmd:"]
        for i in raw_data:
            try:
                padded = f"{int(i):03}"
            except ValueError:
                print(f"⚠️ Không thể chuyển '{i}' thành số nguyên.")
                return False
            arr_covert_text.append(padded)

        arr_covert_text.append("ok")
        s = ",".join(arr_covert_text[1:])
        s = "cmd:"+s
        return s
    else:
        print("❌ Không phải dữ liệu tọa độ (không bắt đầu bằng 'cmd:')")
        return False
    


class StageIngest:
    # Lop nay ke noi COM Va chuan bi du lieu
   
    def __init__(self,services:ServiceContainer):

        self.services = services
        self.protocol_connection_OK = False
  
       
    def check_protocol_connect_com(self):
        if not self.protocol_connection_OK:
                self.services.obj_manager_serial.clear_rx_queue()  
                self.services.obj_manager_serial.clear_tx_queue()
                self.services.obj_manager_serial.send_data("move_to_org:")
                while True:
                    if self.services.obj_manager_serial.get_rx_queue_size() > 0:
                            data = self.services.obj_manager_serial.get_data_from_queue()
                            print("Data nhận được từ Queue ARM:", data)
                            if "has_returned_org:" in data:
                                    print("........IAI về gốc thành công nha .....")
                                    self.services.obj_manager_serial.clear_rx_queue()  
                                    self.services.obj_manager_serial.clear_tx_queue()
                                    self.protocol_connection_OK = True
                                    self.services.obj_com_service.set_shake_hands_complete(True)
                                    return True
                    time.sleep(0.5)   
    
    

    def run(self):
        if not self.check_protocol_connect_com():
             time.sleep(0.5) # Sleep tranh 100% CPU
             return
        if (self.services.get_mode() == EnumMode.MODE_RUN_ONE_FRAME):
            print("----Vào chế độ chạy Frame---")
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
                    status_send_arm = self.wait_for_specific_data(self.services.obj_manager_serial,cmd)
                    if status_send_arm:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                        name  = f"image_{timestamp}.jpg"
                        self.services.obj_camera.capture_image_trigger(path,name,1)

                    elif not status_send_arm:
                        self.services.set_mode(EnumMode.MODE_DEAFAULT)
                        print("Nhan saiiiiiiiiiiiiii tin hieu mong doi")
                        time.sleep(2)

            
            self.services.set_mode(EnumMode.MODE_DEAFAULT)
        
                        
                        
        
                    
                    
             
            # print("Vào mode Run server")
            # time.sleep(0.5)

        if self.services.get_mode() == EnumMode.MODE_DEAFAULT:
            # print("Vào chế độ mặc định")
            time.sleep(0.1)
      
            

    def wait_for_specific_data(self,obj_manager_serial, expected_message, timeout=TIME_OUT_WAIT_ARM_RESEND):
        """Hàm này chờ tín hiệu cụ thể từ obj_manager_serial.Chờ thời gian timeout giây.Sau thời gian chờ k được gửi về False.Nếu nhận đúng tín hiệu trả về True"""
        print(f"⏳ Đang chờ tín hiệu:{expected_message} trong {timeout} giây...")
        obj_manager_serial.clear_rx_queue()
        obj_manager_serial.clear_tx_queue()
        start_time = time.time()
        expected = data_format(expected_message)  # chỉ xử lý 1 lần
        while time.time() - start_time < timeout:
            data = obj_manager_serial.get_data_from_queue()
            if data:
                print(f"📥 PC Nhận được: {data}")
                print("📥 Sau chuyển đổi :", expected)
                if data.strip() == expected:
                    now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    print(now_str,"✅ Nhận đúng tín hiệu mong đợi.")
                    return True
                else:
                    print("⚠️ Tín hiệu nhận sai nội dung.")
            time.sleep(0.001)  # 🔑 tránh CPU 100% + làm chương trình mượt hơn
        print(f"❌ Timeout: Không nhận được tín hiệu trong {timeout} giây.")
        return False
                
                
             
             
        

            
            
       














