import json
import sys
from pathlib import Path

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from app.judger import BaseJudgerAI, JudgmentResult, Judment

CONFIG_PATH = PROJECT_ROOT / "app" / "storage" / "config_judgment_law.json"
IMAGE_PATH = PROJECT_ROOT / "app" / "storage" / "img_points" / "1" / "0" / "4.jpg"


def create_recording_inspector(name: str):
    """Tạo detector giả có tên đúng với key trong cấu hình.

    Input: Tên inspector cần đăng ký.
    Output: Một lớp ``BaseJudgerAI`` dùng để ghi nhận task được chạy.
    Errors: Không phát sinh.
    """
    def define(self, image, *args, **kwargs):
        self.image = image
        self.define_args = args
        self.define_kwargs = kwargs
        return {"called": True, "args": args}

    def compare(self, standard_data, runtime_data, **kwargs):
        self.standard_data = standard_data
        self.compare_kwargs = kwargs
        return {"standard": standard_data, "runtime": runtime_data}

    def judge(self, comparison_data):
        return JudgmentResult(
            ok=True,
            status="OK",
            standard_data=comparison_data["standard"],
            runtime_data=comparison_data["runtime"],
            comparison_data=comparison_data,
            message="Detector giả chạy thành công",
        )

    return type(
        f"{name}RecordingInspector",
        (BaseJudgerAI,),
        {
            "INSPECTOR_NAME": name,
            "define": define,
            "compare": compare,
            "judge": judge,
        },
    )


def load_item_config() -> dict:
    """Đọc cấu hình judgment của product 1, frame 0, item 4.

    Input: Không có.
    Output: Object cấu hình inspector của item 4.
    Errors: ``FileNotFoundError`` hoặc ``KeyError`` nếu dữ liệu không tồn tại.
    """
    with CONFIG_PATH.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)
    return data["1"]["0"]["4"]


def main() -> None:
    """Kiểm tra Judment điều phối đúng config item 1/0/4 trên một ảnh.

    Input: ``config_judgment_law.json`` và ảnh ``img_points/1/0/4.jpg``.
    Output: In PASS khi mọi inspector cấu hình được tạo task và chạy đủ.
    Errors: ``AssertionError`` nếu thiếu inspector, sai số task hoặc không nhận ảnh.
    """
    image = cv2.imread(str(IMAGE_PATH))
    if image is None:
        raise AssertionError(f"Không đọc được ảnh test: {IMAGE_PATH}")

    config = load_item_config()
    registry = {
        name: create_recording_inspector(name)()
        for name in config
    }
    summary = Judment(registry).run_summary(image, config)

    assert summary["overall"] is True
    assert summary["status"] == "OK"
    assert set(summary["inspectors"]) == set(config)
    assert len(summary["errors"]) == 0
    assert summary["image"] == {
        "height": image.shape[0],
        "width": image.shape[1],
        "channels": image.shape[2],
    }
    print("Judment config item 1/0/4 logic test: PASS")
    print(f"Inspectors: {list(config)}")


if __name__ == "__main__":
    main()
