import json
from pathlib import Path
from app.config import PATH_FILE_DATA_CONFIG_JUDMENT_LAW

class JudmentLawProductRepository:
    def __init__(self):
        self.path = Path(PATH_FILE_DATA_CONFIG_JUDMENT_LAW)
        self._ensure_file_exists()
        self.data = self._load()

    def _ensure_file_exists(self) -> None:
        if self.path.exists():
            return

        self.path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({}, f)

    def _load(self) -> dict:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def exists(self, product_id: str, frame_id: str, item_id: str) -> bool:
        return item_id in self.data.get(product_id, {}).get(frame_id, {})

    def get(self, product_id: str, frame_id: str, item_id: str) -> dict | None:
        return self.data.get(product_id, {}).get(frame_id, {}).get(item_id)

    def upsert(self, product_id: str, frame_id: str, item_id: str, item_data: dict) -> None:
        self.data.setdefault(product_id, {})
        self.data[product_id].setdefault(frame_id, {})
        self.data[product_id][frame_id][item_id] = item_data
        self.save()

    def delete(self, product_id: str, frame_id: str, item_id: str) -> bool:
        try:
            del self.data[product_id][frame_id][item_id]
            self.save()
            return True
        except KeyError:
            return False

    def get_product(self, product_id: str) -> dict:
        return self.data.get(product_id, {})

    def get_frame(self, product_id: str, frame_id: str) -> dict:
        return self.data.get(product_id, {}).get(frame_id, {})

    def get_product_ids(self) -> list[str]:
        return list(self.data.keys())

    def get_frame_ids(self, product_id: str) -> list[str]:
        return list(self.data.get(product_id, {}).keys())

    def get_item_ids(self, product_id: str, frame_id: str) -> list[str]:
        return list(self.data.get(product_id, {}).get(frame_id, {}).keys())

    def clear(self) -> None:
        self.data.clear()
        self.save()

    # =========================
    # NEW: import full dict
    # =========================
    def load_from_dict(self, raw: dict, merge: bool = False) -> None:
        """
        Input: dict cây JSON
        merge=False -> ghi đè toàn bộ
        merge=True  -> merge vào dữ liệu cũ
        """
        if not merge:
            self.data = raw
        else:
            self._deep_update(self.data, raw)

        self.save()

    def _deep_update(self, target: dict, source: dict) -> dict:
        for k, v in source.items():
            if isinstance(v, dict) and isinstance(target.get(k), dict):
                self._deep_update(target[k], v)
            else:
                target[k] = v
        return target