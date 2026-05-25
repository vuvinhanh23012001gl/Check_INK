from app.manager.serial import ManagerSerial
class ComService:
    def __init__(self, manager_serial:ManagerSerial):

        self.manager = manager_serial

    def send(self,x,y,z):
        """
        Gửi 1 lệnh đơn giản qua serial
        Format: <CMD:PAYLOAD>
        """
        try:
            data_send = f"cmd:{int(x)},{(int(y))},{int(z)},80"
            self.manager.send_data(data_send)
        except:
            print("ép kiểu nhận về bị sai kiểm tra lại")
       
  