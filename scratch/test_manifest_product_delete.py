import json
import shutil
import sys
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.engines.train.patchcore_train_model.patchcore_train_record_repository import (
    PatchCoreTrainRecordRepository,
)

def test_belonging_logic():
    rec_p2 = {
        "run_id": "model_foreign_crop_20260929_084504_668747",
        "model_root": "app/input/model/patch_core/2/0/0/model_foreign_crop_20260929_084504_668747",
        "model_file": "app/input/model/patch_core/2/0/0/model_foreign_crop_20260929_084504_668747/the_first/patchcore.index",
        "runtime_images_root": "app/input/model/patch_core/2/0/0/model_foreign_crop_20260929_084504_668747/runtime",
    }
    rec_p20 = {
        "run_id": "model_foreign_crop_p20",
        "model_root": "app/input/model/patch_core/20/0/0/model_foreign_crop_xxx",
        "model_file": "app/input/model/patch_core/20/0/0/model_foreign_crop_xxx/the_first/patchcore.index",
        "runtime_images_root": "app/input/model/patch_core/20/0/0/model_foreign_crop_xxx/runtime",
    }
    rec_p1 = {
        "run_id": "model_foreign_crop_p1",
        "model_root": "app/input/model/patch_core/1/0/0/model_foreign_crop_yyy",
    }

    # Test product 2
    assert PatchCoreTrainRecordRepository.is_record_belonging_to_product(rec_p2, 2) is True
    assert PatchCoreTrainRecordRepository.is_record_belonging_to_product(rec_p2, "2") is True
    assert PatchCoreTrainRecordRepository.is_record_belonging_to_product(rec_p2, 20) is False
    assert PatchCoreTrainRecordRepository.is_record_belonging_to_product(rec_p2, 1) is False

    # Test product 20 (tránh nhầm với 2)
    assert PatchCoreTrainRecordRepository.is_record_belonging_to_product(rec_p20, 2) is False
    assert PatchCoreTrainRecordRepository.is_record_belonging_to_product(rec_p20, 20) is True

    # Test product 1
    assert PatchCoreTrainRecordRepository.is_record_belonging_to_product(rec_p1, 1) is True
    assert PatchCoreTrainRecordRepository.is_record_belonging_to_product(rec_p1, 2) is False
    print("PASS: test_belonging_logic")

def test_delete_manifest_by_product():
    with tempfile.TemporaryDirectory() as temp_dir:
        manifest_file = Path(temp_dir) / "test_manifest.json"
        sample_records = [
            {
                "run_id": "rec_prod_1",
                "model_root": "app/input/model/patch_core/1/0/0/model_1",
            },
            {
                "run_id": "rec_prod_2_a",
                "model_root": "app/input/model/patch_core/2/0/0/model_2a",
            },
            {
                "run_id": "rec_prod_2_b",
                "model_root": "app/input/model/patch_core/2/1/0/model_2b",
            },
            {
                "run_id": "rec_prod_20",
                "model_root": "app/input/model/patch_core/20/0/0/model_20",
            },
        ]
        manifest_file.write_text(json.dumps(sample_records, indent=2), encoding="utf-8")

        repo = PatchCoreTrainRecordRepository(manifest_path=manifest_file)
        assert repo.has_records_for_product(2) is True
        assert repo.has_records_for_product(99) is False

        # Xóa product 2
        deleted = repo.delete_records_by_product_id(2)
        assert deleted == 2, f"Expected 2 deleted, got {deleted}"

        # Kiểm tra nội dung sau khi xóa
        remaining = repo.load_manifest()
        remaining_ids = [r["run_id"] for r in remaining]
        assert remaining_ids == ["rec_prod_1", "rec_prod_20"], f"Remaining: {remaining_ids}"
        assert repo.has_records_for_product(2) is False
        assert repo.has_records_for_product(1) is True
        assert repo.has_records_for_product(20) is True
        print("PASS: test_delete_manifest_by_product")

def test_product_service_manifest_cleanup():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        foreign_manifest = temp_path / "foreign_manifest.json"
        end_manifest = temp_path / "end_manifest.json"

        records_foreign = [
            {"run_id": "f_1", "model_root": "app/input/model/patch_core/1/0/0/m1"},
            {"run_id": "f_2", "model_root": "app/input/model/patch_core/2/0/0/m2"},
        ]
        records_end = [
            {"run_id": "e_2", "model_root": "app/input/model/patch_core/2/0/0/m2"},
            {"run_id": "e_3", "model_root": "app/input/model/patch_core/3/0/0/m3"},
        ]
        foreign_manifest.write_text(json.dumps(records_foreign, indent=2), encoding="utf-8")
        end_manifest.write_text(json.dumps(records_end, indent=2), encoding="utf-8")

        from app.services.product_service import ProductService
        # Test helper method
        assert ProductService._has_patchcore_records(foreign_manifest, "2") is True
        assert ProductService._has_patchcore_records(foreign_manifest, "3") is False

        # Test delete helper
        del_count = ProductService._delete_patchcore_manifest_records(foreign_manifest, "2")
        assert del_count == 1
        rem_foreign = json.loads(foreign_manifest.read_text(encoding="utf-8"))
        assert len(rem_foreign) == 1
        assert rem_foreign[0]["run_id"] == "f_1"

        del_end = ProductService._delete_patchcore_manifest_records(end_manifest, "2")
        assert del_end == 1
        rem_end = json.loads(end_manifest.read_text(encoding="utf-8"))
        assert len(rem_end) == 1
        assert rem_end[0]["run_id"] == "e_3"

        print("PASS: test_product_service_manifest_cleanup")

if __name__ == "__main__":
    test_belonging_logic()
    test_delete_manifest_by_product()
    test_product_service_manifest_cleanup()
    print("ALL TESTS PASSED!")
