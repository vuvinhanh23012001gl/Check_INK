from app.container import ServiceContainer,EnumMode
import time

TIME_OUT_WAIT_ARM_RESEND = 4


class StagePreprocess:
    """ Lớp này là lớp chuẩn bị chạy """
    def __init__(self,services:ServiceContainer):

        self.services = services
        self.protocol_connection_OK = False


    def run(self):
        if not self.check_protocol_connect_com():
             print("Luồng pipeline đang chạy đợi kêt nối ESP32")
             time.sleep(0.5) # Sleep tranh 100% CPU
             return
        

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
                                    self.services.set_mode(EnumMode.MODE_TRANSFORM)
                                    return True
                    time.sleep(0.5)   
    


      
            


                
                
             
             
        

            
            
       














