import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.judment_law_product_service import JudmentLawProductSevice
from app.services.weld_reference_service import WeldReferenceService


class InMemoryJudgmentRepository:
    def __init__(self, item_data):
        self.item_data = item_data
        self.save_count = 0

    def get(self, product_id, frame_id, item_id):
        return self.item_data

    def save(self):
        self.save_count += 1


class TestDeleteAirBubblesWeldReference(unittest.TestCase):
    def test_delete_reference_removes_files_and_preserves_rectangles(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            reference_service = object.__new__(WeldReferenceService)
            reference_service.STORAGE_DIR = root / "weld_reference"
            reference_service.RECORD_CATALOG_FILE = root / "weld_reference_record.json"
            record_id = "weld_ref_p1_f0_i2"
            record_dir = reference_service.STORAGE_DIR / record_id
            record_dir.mkdir(parents=True)
            for file_name in ("polygon.json", "skeleton.json", "metadata.json"):
                (record_dir / file_name).write_text("{}", encoding="utf-8")
            reference_service.RECORD_CATALOG_FILE.write_text(
                json.dumps({"records": {record_id: {"id": record_id}}}),
                encoding="utf-8",
            )
            item_data = {
                "AirBubblesItemInspector": {
                    "0": {"id": 0, "name": "bubble", "xStart": 1},
                    "weld_reference_id": record_id,
                }
            }
            repository = InMemoryJudgmentRepository(item_data)
            service = JudmentLawProductSevice(repository)

            with patch(
                "app.services.judment_law_product_service.weld_reference_service",
                reference_service,
            ):
                result = service.delete_weld_reference(1, 0, 2)

            self.assertTrue(result.ok)
            self.assertTrue(result.data["deleted"])
            self.assertFalse(record_dir.exists())
            self.assertEqual(
                item_data["AirBubblesItemInspector"]["0"],
                {"id": 0, "name": "bubble", "xStart": 1},
            )
            self.assertNotIn(
                "weld_reference_id", item_data["AirBubblesItemInspector"]
            )
            self.assertNotIn(
                record_id,
                json.loads(reference_service.RECORD_CATALOG_FILE.read_text(
                    encoding="utf-8"
                ))["records"],
            )

    def test_delete_without_saved_reference_is_a_noop(self):
        repository = InMemoryJudgmentRepository(
            {"AirBubblesItemInspector": {"0": {"id": 0}}}
        )
        service = JudmentLawProductSevice(repository)

        result = service.delete_weld_reference(1, 0, 2)

        self.assertTrue(result.ok)
        self.assertFalse(result.data["deleted"])
        self.assertFalse(result.data["changed"])
        self.assertEqual(repository.save_count, 0)


if __name__ == "__main__":
    unittest.main()