import numpy as np
from app.config import ClassNameModelSurfaceConfig
from app.engines.AI_model_process import FrameModelYoloObject
from app.core import Result, ErrorCode
class SurfaceFrameYoloService:
    def __init__(self, frame_model: FrameModelYoloObject):
        """Khởi tạo StructureFrameYoloService.
        Args:
            frame_model (FrameModelYoloObject): Đối tượng thực hiện nhận diện YOLO.
        """
        self.frame_model = frame_model


    def get_objects_by_label(
            self,
            image: np.ndarray,
            x1: int,
            y1: int,
            x2: int,
            y2: int,
            label: str,
            width_canvas: int
        ) -> Result:
            """Lấy danh sách đối tượng theo label trong vùng kiểm tra sau khi quy đổi tọa độ từ Canvas sang Ảnh thực tế."""
            
            # 1. Lấy kích thước thực tế của ảnh gốc (OpenCV load lên)
            h_img, w_img = image.shape[:2]
            
            # 2. Tính tỷ lệ scale (Tránh chia cho 0 nếu width_canvas truyền vào không hợp lệ)
            if width_canvas <= 0:
                return Result.Fail(ErrorCode.INVALID_INPUT)
                
            scale = w_img / width_canvas
            
            # 3. Quy đổi tọa độ từ Canvas sang tọa độ thực trên ảnh gốc
            real_x1 = int(x1 * scale)
            real_y1 = int(y1 * scale)
            real_x2 = int(x2 * scale)
            real_y2 = int(y2 * scale)
            
            # 4. Giới hạn (Clip) các tọa độ thực tế nằm trong biên của ảnh gốc để tránh lỗi Out of Bounds
            real_x1 = max(0, min(real_x1, w_img - 1))
            real_y1 = max(0, min(real_y1, h_img - 1))
            real_x2 = max(0, min(real_x2, w_img - 1))
            real_y2 = max(0, min(real_y2, h_img - 1))
    
            # 5. Truyền tọa độ đã quy đổi chuẩn xác vào hàm search của mô hình AI
            status, _, img, objects = self.frame_model.search(
                image, 
                real_x1, 
                real_y1, 
                real_x2, 
                real_y2, 
                label,
            )
            # Tool_OpenCv2.show_img(img)
            print("status",status)
            if not status:
                return Result.Fail(ErrorCode.LABEL_NOT_FOUND)
            return Result.Ok(objects)

    def judge_regions(
        self,
        image: np.ndarray,
        regions: list[dict],
        width_canvas: int,
    ) -> Result:
        """Phán định bọt khí trong nhiều vùng kiểm tra trên ảnh.

        Args:
            image: Ảnh master cần kiểm tra.
            regions: Danh sách vùng có xStart, yStart, xEnd, yEnd.
            width_canvas: Chiều rộng canvas phía client.

        Returns:
            Result.Ok chứa trạng thái, danh sách object và kết quả từng vùng.
            Result.Fail nếu ảnh, vùng hoặc kích thước canvas không hợp lệ.

        Raises:
            Không phát sinh exception cho input thông thường; lỗi kiểm tra được
            trả về dưới dạng Result.Fail.
        """
        if image is None or image.size == 0:
            return Result.Fail(ErrorCode.IMAGE_NOT_FOUND)
        if not isinstance(regions, list) or not regions:
            return Result.Fail(ErrorCode.INVALID_INPUT)
        if width_canvas <= 0:
            return Result.Fail(ErrorCode.INVALID_INPUT)

        all_objects = []
        region_results = []
        for index, region in enumerate(regions, start=1):
            try:
                x_start = int(region["xStart"])
                y_start = int(region["yStart"])
                x_end = int(region["xEnd"])
                y_end = int(region["yEnd"])
            except (KeyError, TypeError, ValueError):
                return Result.Fail(ErrorCode.INVALID_INPUT)

            x_start, x_end = sorted((x_start, x_end))
            y_start, y_end = sorted((y_start, y_end))
            if x_start == x_end or y_start == y_end:
                return Result.Fail(ErrorCode.INVALID_INPUT)

            image_objects, _ = self.frame_model.get_objects(
                image,
                int(x_start * image.shape[1] / width_canvas),
                int(y_start * image.shape[1] / width_canvas),
                int(x_end * image.shape[1] / width_canvas),
                int(y_end * image.shape[1] / width_canvas),
            )
            bubble_objects, _ = self.frame_model.filter_objects_by_class_name(
                image_objects,
                ClassNameModelSurfaceConfig.AIR_BUBBLE.value,
            )
            for detected_object in bubble_objects:
                detected_object["region_id"] = region.get("id", index - 1)
            all_objects.extend(bubble_objects)
            region_results.append(
                {
                    "region_id": region.get("id", index - 1),
                    "region_name": region.get("name", f"Bọt khí {index}"),
                    "bubble_count": len(bubble_objects),
                    "ok": not bubble_objects,
                }
            )
        is_ok = not all_objects
        return Result.Ok(
            {
                "is_ok": is_ok,
                "status": "OK" if is_ok else "NG",
                "objects": all_objects,
                "regions": region_results,
                "width": image.shape[1],
                "height": image.shape[0],
            }
        )