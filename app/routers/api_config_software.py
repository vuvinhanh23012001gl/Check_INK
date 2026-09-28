from fastapi import APIRouter, Depends
from pathlib import Path
from app.config.path_config import (
    PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_BORDER,
    PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_INER,
    PATH_FILE_MODEL_YOLO_STRUCTURE,
    PATH_FILE_MODEL_YOLO_SURFACE,
    PATH_FILE_UNET_DETECT_FILM_BORDER_LINE,
    PATH_FILE_UNET_DETECT_WELD_LINE,
    PATH_FOLDER_IMG_COORDINATE_OUTPUT,
    PATH_FOLDER_OUTPUT_JUDGMENT,
)
from app.core.dependencies import get_services

router = APIRouter(
    prefix="/software",
    tags=["Software"]
)

@router.get("/version")
def software_version():
    return {"version": "1.0.0"}


@router.get("/information")
def software_information(services=Depends(get_services)):
    """Trả về metadata phần mềm và các đường dẫn model/output cho giao diện.

    Input: service container của ứng dụng do FastAPI inject.
    Output: metadata và danh sách model, thư mục output theo ba nhóm.
    Errors: lỗi cấu hình service có thể được FastAPI trả về dưới dạng HTTP 500.
    """
    def display_path(path):
        """Chuẩn hóa đường dẫn cấu hình thành đường dẫn tuyệt đối.

        Input: đường dẫn file hoặc thư mục trong cấu hình.
        Output: đường dẫn tuyệt đối theo hệ điều hành hiện tại.
        Errors: OSError nếu hệ thống không thể phân giải đường dẫn.
        """
        return str(Path(path).resolve())

    return {
        "software": services.obj_infor_software.to_dict(),
        "models": [
            {"label": "Mô hình nhận diện đường hàn", "path": display_path(PATH_FILE_UNET_DETECT_WELD_LINE)},
            {"label": "Mô hình nhận diện viền Film", "path": display_path(PATH_FILE_UNET_DETECT_FILM_BORDER_LINE)},
            {"label": "Mô hình YOLO nhận diện cấu trúc", "path": display_path(PATH_FILE_MODEL_YOLO_STRUCTURE)},
            {"label": "Mô hình YOLO nhận diện bề mặt", "path": display_path(PATH_FILE_MODEL_YOLO_SURFACE)},
            {"label": "Mô hình YOLO phân đoạn màng thấm bên trong", "path": display_path(PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_INER)},
            {"label": "Mô hình YOLO phân đoạn viền màng thấm", "path": display_path(PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_BORDER)},
            {
                "label": "Mô hình PatchCore",
                "message": "Hãy vào ‘Điều chỉnh master’ -> ‘Kiểm tra mẻ ống’ hoặc ‘Kiểm tra dị vật’ để thay đổi mô hình",
            },
        ],
        "outputs": [
            {"label": "Thư mục output phán định", "path": display_path(PATH_FOLDER_OUTPUT_JUDGMENT)},
            {"label": "Thư mục output PatchCore", "path": display_path(PATH_FOLDER_IMG_COORDINATE_OUTPUT)},
        ],
    }
