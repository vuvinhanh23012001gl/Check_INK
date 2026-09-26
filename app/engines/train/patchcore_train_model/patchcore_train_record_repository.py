import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from app.config.path_config import (
    PATH_FILE_END_CHIPPING_PATCHCORE_TRAIN_MANIFEST,
    WORKSPACE_DIR,
)


class PatchCoreTrainRecordRepository:
    """Quản lý lịch sử train mô hình PatchCore theo từng phiên.

    Mỗi phiên train được lưu trực tiếp thành một phần tử trong
    ``runs_manifest.json`` để UI có thể liệt kê nhanh.
    """

    def __init__(
        self,
        root_dir: str | Path | None = None,
        manifest_path: str | Path | None = None,
    ):
        """Khởi tạo service với manifest trung tâm.

        Args:
            root_dir: Folder tùy chọn dùng cho test; manifest sẽ nằm trong
                ``root_dir/runs_manifest.json``. Khi bỏ trống, service dùng
                file trung tâm đã cấu hình trong ``path_config.py``.
            manifest_path: File manifest tùy chọn; không kết hợp với root_dir.
        """
        if manifest_path is not None:
            self.manifest_path = Path(manifest_path).expanduser().resolve()
        elif root_dir is None:
            self.manifest_path = Path(
                PATH_FILE_END_CHIPPING_PATCHCORE_TRAIN_MANIFEST
            ).expanduser().resolve()
        else:
            root_path = Path(root_dir).expanduser().resolve()
            root_path.mkdir(parents=True, exist_ok=True)
            self.manifest_path = root_path / "runs_manifest.json"
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

    def _normalize_runtime_value(self, value: Any) -> Any:
        """Chuyển giá trị runtime sang kiểu có thể serialize bằng JSON.

        Args:
            value: Giá trị cần chuẩn hóa, có thể là Path, collection hoặc dict.

        Returns:
            Any: Giá trị JSON-safe tương ứng.

        Raises:
            Không chủ động phát sinh lỗi; kiểu không đặc biệt được giữ nguyên.
        """
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, (list, tuple, set)):
            return [self._normalize_runtime_value(item) for item in value]
        if isinstance(value, dict):
            return {str(key): self._normalize_runtime_value(item) for key, item in value.items()}
        return value

    @staticmethod
    def _manifest_path_value(value: str | Path | None) -> str:
        """Chuẩn hóa path trong manifest thành đường dẫn tương đối workspace."""
        if value is None or value == "":
            return ""
        path = Path(value).expanduser().resolve()
        workspace_root = WORKSPACE_DIR
        try:
            return path.relative_to(workspace_root).as_posix()
        except ValueError:
            return str(path)

    def _compact_metadata(self, item: dict) -> dict:
        """Loại bỏ các khóa legacy hoặc trùng lặp khỏi một record."""
        compacted = dict(item)
        for key in (
            "data_root",
            "model_dir",
            "model_files",
            "summary_image",
            "notes",
            "config_snapshot",
        ):
            compacted.pop(key, None)
        for key in ("model_root", "model_file", "runtime_images_root"):
            if key in compacted:
                compacted[key] = self._manifest_path_value(compacted[key])
        train_config = compacted.get("train_config")
        if isinstance(train_config, dict):
            train_config = dict(train_config)
            train_config.pop("crop_roi", None)
            compacted["train_config"] = train_config
        return compacted

    def load_manifest(self) -> list[dict]:
        """Đọc danh sách record từ file manifest trung tâm.

        Returns:
            list[dict]: Các record hợp lệ sau khi compact metadata.

        Raises:
            Không phát sinh lỗi ra ngoài; JSON hỏng hoặc lỗi I/O trả về list rỗng.
        """
        if not self.manifest_path.exists():
            return []
        try:
            data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [self._compact_metadata(item) for item in data if isinstance(item, dict)]
            return []
        except (json.JSONDecodeError, OSError):
            return []

    def save_manifest(self, items: list[dict]):
        """Ghi danh sách record vào file manifest.

        Args:
            items: Danh sách metadata cần compact và lưu.

        Returns:
            None.

        Raises:
            OSError: Nếu không thể tạo hoặc ghi file manifest.
        """
        compacted_items = [self._compact_metadata(item) for item in items]
        self.manifest_path.write_text(
            json.dumps(compacted_items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _has_same_roi(record: dict, roi_list: list[str]) -> bool:
        """Kiểm tra record có cùng ROI với phiên train hiện tại không."""
        current_rois = {
            str(roi).strip().lower()
            for roi in roi_list
        }
        record_rois = {
            str(roi).strip().lower()
            for roi in record.get("roi_list", [])
        }
        return bool(current_rois) and current_rois == record_rois

    def config_to_dict(self, config):
        """Chuyển object config sang dict JSON-safe.

        Args:
            config: Object config dataclass hoặc object có thuộc tính.

        Returns:
            dict: Dữ liệu đủ để lưu snapshot.
        """
        if config is None:
            return {}

        if hasattr(config, "__dict__"):
            data = config.__dict__.copy()
            return self._normalize_runtime_value(data)

        return self._normalize_runtime_value(config)

    def save_record(
        self,
        config,
        purpose: str,
        roi_list: list[str] | None = None,
        crop_roi: dict | None = None,
        model_root: str | Path | None = None,
        model_file: str | Path | None = None,
        inference_result: str | Path | None = None,
        runtime_images_root: str | Path | None = None,
        run_id: str | None = None,
        status: str = "completed",
    ) -> dict:
        """Lưu metadata của phiên train vào manifest.

        Args:
            config: Cấu hình train.
            purpose: Mục đích train.
            roi_list: Danh sách ROI được train.
            crop_roi: Tọa độ vùng crop.
            model_root: Folder chứa ảnh và model của session.
            model_file: Đường dẫn file model.
            inference_result: Ảnh inference sau khi train.
            runtime_images_root: Folder ảnh runtime của session.
            run_id: Mã session; tự tạo nếu bỏ trống.
            status: Trạng thái phiên train.

        Returns:
            dict: Metadata của phiên train.
        """
        now = datetime.now(timezone.utc)
        run_id = run_id or f"patchcore_{now.strftime('%Y%m%d_%H%M%S_%f')}"
        config_data = self.config_to_dict(config)
        model_file_value = str(model_file) if model_file is not None else ""
        metadata = {
            "run_id": run_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "purpose": purpose,
            "status": status,
            "model_root": self._manifest_path_value(model_root),
            "model_file": self._manifest_path_value(model_file_value),
            "inference_result": self._manifest_path_value(inference_result),
            "runtime_images_root": self._manifest_path_value(runtime_images_root),
            "roi_list": list(roi_list or []),
            "crop_roi": self._normalize_runtime_value(crop_roi or {}),
            "train_config": {
                key: value for key, value in config_data.items() if key != "crop_roi"
            },
        }

        manifest = [
            record
            for record in self.load_manifest()
            if not self._has_same_roi(record, roi_list or [])
        ]
        manifest.insert(0, metadata)
        self.save_manifest(manifest)
        return metadata

    def get_latest_run(self) -> dict | None:
        """Lấy record mới nhất trong manifest.

        Returns:
            dict | None: Record đầu tiên hoặc None nếu manifest rỗng.

        Raises:
            Không phát sinh lỗi ra ngoài; lỗi đọc manifest được xử lý bởi
                ``load_manifest``.
        """
        manifest = self.load_manifest()
        if not manifest:
            return None
        return manifest[0]

    def delete_records_by_model_root(self, model_root: str | Path) -> int:
        """Xóa các record trỏ đúng tới một thư mục session PatchCore.

        Args:
            model_root: Thư mục session model cần loại khỏi manifest.

        Returns:
            int: Số record đã xóa khỏi danh sách manifest.

        Raises:
            OSError: Nếu không thể ghi lại manifest.
        """
        target_root = Path(model_root).expanduser().resolve()
        manifest = self.load_manifest()
        retained = []
        deleted_count = 0
        for record in manifest:
            record_root_value = record.get("model_root")
            if record_root_value:
                record_root = Path(record_root_value).expanduser()
                if not record_root.is_absolute():
                    record_root = WORKSPACE_DIR / record_root
                if record_root.resolve() == target_root:
                    deleted_count += 1
                    continue
            retained.append(record)
        if deleted_count:
            self.save_manifest(retained)
        return deleted_count


PatchCoreTrainRecordManager = PatchCoreTrainRecordRepository
