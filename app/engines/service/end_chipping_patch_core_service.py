"""Cấu hình PatchCore cho workflow kiểm tra đầu ống mẻ."""

from app.config import PATH_FILE_END_CHIPPING_PATCHCORE_TRAIN_MANIFEST
from app.engines.service.patchcore_inspection_service import PatchCoreInspectionService
from app.engines.train.patchcore_train_model.patchcore_train_record_repository import (
    PatchCoreTrainRecordRepository,
)


class EndChippingPatchCoreService(PatchCoreInspectionService):
    """Cấu hình PatchCore cho kiểm tra đầu ống mẻ."""

    def __init__(self, point_service):
        """Khởi tạo service End Chipping với manifest riêng.

        Args:
            point_service: Service truy xuất ảnh theo product/frame/item.

        Returns:
            None.

        Raises:
            OSError: Nếu không thể tạo thư mục chứa manifest.
        """
        super().__init__(
            point_service=point_service,
            roi_name="end_chipping",
            purpose="train patchcore end chipping",
            record_repository=PatchCoreTrainRecordRepository(
                manifest_path=PATH_FILE_END_CHIPPING_PATCHCORE_TRAIN_MANIFEST,
            ),
        )
