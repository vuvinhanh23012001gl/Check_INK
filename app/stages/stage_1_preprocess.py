from app.container import ServiceContainer
import time

class StagePreprocess:
    """ Lớp này là lớp chuẩn bị chạy """
    def __init__(self,services:ServiceContainer):

        self.services = services
        self.protocol_connection_OK = False


    def run(self):
        print("IAIControl xử lý kết nối COM và đưa máy về gốc bằng nút xanh.")
        time.sleep(0.5)
        

    def check_protocol_connect_com(self):
    
        """Kiểm tra COM đã sẵn sàng mà không điều khiển ARM về gốc.
        Input: không có; đọc trạng thái kết nối từ ``ManagerSerial``.
        Output: ``True`` nếu COM và các luồng RX/TX đang hoạt động, ngược lại
            ``False``.
        Errors: không phát sinh; lỗi kết nối được ``ManagerSerial`` xử lý.
        """

        status = self.services.obj_manager_serial.is_running()
        if status and not self.protocol_connection_OK:
            print("✅ COM và luồng Serial đã sẵn sàng.")
            self.protocol_connection_OK = True
            self.services.obj_com_service.set_shake_hands_complete(True)
        elif not status:
            self.protocol_connection_OK = False
        return status
    


      
            


                
                
             
             
        

            
            
       














