import json
import os
import shutil
import time
from pathlib import Path
from typing import Optional, Tuple, Any
import numpy as np


class WeldReferenceService:
    """Quản lý lưu trữ và truy xuất dữ liệu tham chiếu đường hàn (Polygon & Skeleton)."""

    STORAGE_DIR = Path("app/storage/weld_reference")
    RECORD_CATALOG_FILE = Path("app/storage/weld_reference_record.json")

    def __init__(self):
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.RECORD_CATALOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not self.RECORD_CATALOG_FILE.exists():
            self._write_catalog({"records": {}})

    def _read_catalog(self) -> dict:
        try:
            with open(self.RECORD_CATALOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"records": {}}

    def _write_catalog(self, catalog: dict) -> bool:
        try:
            with open(self.RECORD_CATALOG_FILE, "w", encoding="utf-8") as f:
                json.dump(catalog, f, ensure_ascii=False, indent=4)
            return True
        except Exception as error:
            print(f"⚠️ [WeldReferenceService] Lỗi ghi catalog: {error}")
            return False

    @staticmethod
    def generate_record_id(product_id: int | str, frame_id: int | str, item_id: int | str) -> str:
        """Sinh mã ID duy nhất định danh bản ghi đường hàn theo Product/Frame/Item."""
        return f"weld_ref_p{product_id}_f{frame_id}_i{item_id}"

    def save_reference(
        self,
        record_id: str,
        product_id: int | str,
        frame_id: int | str,
        item_id: int | str,
        polygon: list,
        skeleton: list,
        width: int,
        height: int,
    ) -> bool:
        """Lưu polygon, skeleton và metadata của đường hàn vào thư mục ổ cứng."""
        try:
            record_dir = self.STORAGE_DIR / record_id
            record_dir.mkdir(parents=True, exist_ok=True)

            # Chuẩn hóa polygon sang list thuần
            poly_data = []
            for p in polygon:
                if isinstance(p, np.ndarray):
                    poly_data.append(p.tolist())
                elif isinstance(p, list):
                    poly_data.append(p)

            # Chuẩn hóa skeleton
            skel_data = []
            for pt in skeleton:
                if isinstance(pt, (np.ndarray, list, tuple)):
                    skel_data.append([int(pt[0]), int(pt[1])])

            with open(record_dir / "polygon.json", "w", encoding="utf-8") as f:
                json.dump(poly_data, f, ensure_ascii=False)

            with open(record_dir / "skeleton.json", "w", encoding="utf-8") as f:
                json.dump(skel_data, f, ensure_ascii=False)

            metadata = {
                "id": record_id,
                "product_id": int(product_id),
                "frame_id": int(frame_id),
                "item_id": int(item_id),
                "image_width": int(width),
                "image_height": int(height),
                "point_count_skeleton": len(skel_data),
                "polygon_contours": len(poly_data),
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            with open(record_dir / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=4)

            # Cập nhật catalog
            catalog = self._read_catalog()
            catalog.setdefault("records", {})[record_id] = {
                "id": record_id,
                "product_id": int(product_id),
                "frame_id": int(frame_id),
                "item_id": int(item_id),
                "dir": str(record_dir).replace("\\", "/"),
                "updated_at": metadata["updated_at"],
            }
            self._write_catalog(catalog)
            return True
        except Exception as error:
            print(f"❌ [WeldReferenceService] Lỗi lưu bản ghi {record_id}: {error}")
            return False

    def get_reference(self, record_id: str) -> Optional[dict]:
        """Đọc toàn bộ dữ liệu polygon, skeleton và metadata theo record_id."""
        try:
            record_dir = self.STORAGE_DIR / record_id
            if not record_dir.exists():
                return None

            polygon_file = record_dir / "polygon.json"
            skeleton_file = record_dir / "skeleton.json"
            metadata_file = record_dir / "metadata.json"

            polygon = []
            skeleton = []
            metadata = {}

            if polygon_file.exists():
                with open(polygon_file, "r", encoding="utf-8") as f:
                    polygon = json.load(f)

            if skeleton_file.exists():
                with open(skeleton_file, "r", encoding="utf-8") as f:
                    skeleton = json.load(f)

            if metadata_file.exists():
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

            return {
                "id": record_id,
                "polygon": polygon,
                "skeleton": skeleton,
                "metadata": metadata,
            }
        except Exception as error:
            print(f"⚠️ [WeldReferenceService] Lỗi đọc bản ghi {record_id}: {error}")
            return None

    def delete_reference(self, record_id: str) -> bool:
        """Xóa thư mục polygon/skeleton/metadata và mục catalog theo record ID.

        Args:
            record_id: ID weld reference cần xóa.
        Returns:
            bool: True nếu đã xóa hoặc bản ghi vốn không còn tồn tại.
        Errors:
            Trả về False nếu ID không an toàn, catalog lỗi hoặc thao tác file thất bại.
        """
        if not isinstance(record_id, str) or not record_id or Path(record_id).name != record_id:
            return False

        try:
            with open(self.RECORD_CATALOG_FILE, "r", encoding="utf-8") as f:
                catalog = json.load(f)
        except FileNotFoundError:
            catalog = {"records": {}}
        except (OSError, json.JSONDecodeError) as error:
            print(f"⚠️ [WeldReferenceService] Không đọc được catalog khi xóa: {error}")
            return False

        records = catalog.get("records") if isinstance(catalog, dict) else None
        if not isinstance(records, dict):
            return False

        record_dir = self.STORAGE_DIR / record_id
        if not record_dir.exists() and record_id not in records:
            return True

        try:
            if record_dir.exists():
                if not record_dir.is_dir():
                    return False
                shutil.rmtree(record_dir)
            records.pop(record_id, None)
            return self._write_catalog(catalog)
        except OSError as error:
            print(f"⚠️ [WeldReferenceService] Lỗi xóa bản ghi {record_id}: {error}")
            return False

    def delete_references_by_product(self, product_id: int | str) -> tuple[int, list[str]]:
        """Xóa toàn bộ weld reference thuộc về một sản phẩm.

        Input: ``product_id`` là ID sản phẩm ở dạng int hoặc str.
        Output: tuple ``(deleted_count, failed_ids)`` với:
            - ``deleted_count``: số record xóa thành công.
            - ``failed_ids``: danh sách record_id xóa thất bại.
        Errors: Không ném lỗi; lỗi đọc catalog/xóa file được quy đổi vào
            ``failed_ids`` và trả về số lượng xóa thành công.
        """
        product_key = str(product_id)
        catalog = self._read_catalog()
        records = catalog.get("records") if isinstance(catalog, dict) else {}
        if not isinstance(records, dict):
            records = {}

        candidate_ids: set[str] = set()
        for record_id, payload in records.items():
            if not isinstance(payload, dict):
                continue
            if str(payload.get("product_id")) == product_key:
                candidate_ids.add(str(record_id))

        # Dọn thêm các thư mục orphan không còn trong catalog.
        for ref_dir in self.STORAGE_DIR.glob(f"weld_ref_p{product_key}_f*_i*"):
            if ref_dir.is_dir():
                candidate_ids.add(ref_dir.name)

        deleted_count = 0
        failed_ids: list[str] = []
        for record_id in sorted(candidate_ids):
            if self.delete_reference(record_id):
                deleted_count += 1
            else:
                failed_ids.append(record_id)

        return deleted_count, failed_ids

    def get_polygon_contour(self, record_id: str) -> Optional[np.ndarray]:
        """Lấy polygon lớn nhất dạng np.ndarray (int32) để phục vụ cv2.pointPolygonTest."""
        data = self.get_reference(record_id)
        if not data or not data.get("polygon"):
            return None
        polygons = data["polygon"]
        if not polygons:
            return None
        # Lấy polygon có số điểm lớn nhất (contour chính của đường hàn)
        main_poly = max(polygons, key=lambda pts: len(pts) if isinstance(pts, list) else 0)
        if not main_poly:
            return None
        return np.array(main_poly, dtype=np.int32)


weld_reference_service = WeldReferenceService()
