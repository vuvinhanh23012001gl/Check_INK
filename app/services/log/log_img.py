# from pathlib import Path
# import sys
# sys.path.append(str(Path(__file__).resolve().parents[3]))

import cv2
from pathlib import Path
from app.utils import Folder

class Log_Img:
    extension = "jpg"
    def __init__(self,obj_folder:Folder ,path_img: str, open_log_img: bool = True):
        self.obj_folder = obj_folder
        self.open_log = open_log_img
        self.path_img = self.obj_folder.create_folder_from_path(Path(path_img))

    def save(self, img, file_name: str):
  
        if not self.open_log:
            return None

        if self.path_img is None:
            return None   # hoặc raise RuntimeError

        if img is None:
            return None
        if not file_name or not isinstance(file_name, str):
          
            return None

        file_path = self.path_img / f"{file_name.strip()}.{Log_Img.extension}"
        success = cv2.imwrite(str(file_path), img)
        return file_path if success else None