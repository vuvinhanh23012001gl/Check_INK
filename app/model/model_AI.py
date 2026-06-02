from abc import ABC,abstractmethod

class BaseAI(ABC):
    @abstractmethod
    def load_model(self):
        # Load
        pass
    def preprocess(self):
        # tiền xử lý
        pass
    def predict(self):
        # du doan
        pass
    def unload(self):
        # giai phong mo hinh tren ram
        pass
    def warmup(self):
        # chạy trước mô hình 1 lần
        pass

     