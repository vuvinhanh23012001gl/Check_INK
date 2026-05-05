import cv2
import os
import numpy as np
import base64
class Tool_OpenCv2:
    def __init__(self):
        pass    

    def save_image(self,image, save_path):
        """
        image: Dữ liệu ảnh (numpy array)
        save_path: Đường dẫn đầy đủ bao gồm tên file (vd: 'data/img/sanpham1.jpg')
        """
        try:
            # Lấy thư mục cha từ đường dẫn để kiểm tra tồn tại
            directory = os.path.dirname(save_path)
            
            # Nếu thư mục chưa tồn tại thì tạo mới
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Đã tạo thư mục: {directory}")

            # Tiến hành lưu ảnh
            # cv2.imwrite trả về True nếu thành công, False nếu thất bại
            result = cv2.imwrite(save_path, image)
            
            if result:
                print(f"Lưu ảnh thành công tại: {save_path}")
                return True
            else:
                print("Lưu ảnh thất bại. Kiểm tra lại định dạng file.")
                return False
                
        except Exception as e:
            print(f"Có lỗi xảy ra: {e}")
            return False
    def delete_image(self, image_path):
        """
        image_path: Đường dẫn đầy đủ tới file ảnh cần xoá
        """
        try:
            # Kiểm tra file có tồn tại không
            if not os.path.exists(image_path):
                print(f"❌ Không tìm thấy file ảnh: {image_path}")
                return False

            # Kiểm tra đúng là file (không phải thư mục)
            if not os.path.isfile(image_path):
                print(f"❌ Đường dẫn không phải file: {image_path}")
                return False

            os.remove(image_path)
            print(f"🗑️ Đã xoá ảnh: {image_path}")
            return True

        except Exception as e:
            print(f"❌ Có lỗi xảy ra khi xoá ảnh: {e}")
            return False
    def create_black_image(self, width, height, channels=3):
        """
        Tạo ảnh màu đen
        channels = 1 : ảnh grayscale
        channels = 3 : ảnh BGR (OpenCV)
        """
        if channels == 1:
            return np.zeros((height, width), dtype=np.uint8)
        elif channels == 3:
            return np.zeros((height, width, 3), dtype=np.uint8)
        else:
            raise ValueError("channels chỉ hỗ trợ 1 hoặc 3")
        
    def show_img(self,img, win_name="Image", wait=0):
        cv2.imshow(win_name, img)
        cv2.waitKey(wait)
        cv2.destroyAllWindows()
    def convert_frame_to_base64(self,frame):
        """
        Convert OpenCV frame sang base64 để gửi cho client
        """
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            return None
        
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        return frame_base64