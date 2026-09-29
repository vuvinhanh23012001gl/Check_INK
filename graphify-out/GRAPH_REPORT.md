# Graph Report - app  (2026-09-29)

## Corpus Check
- 277 files · ~861,213 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 40 file(s) not represented in the graph (top: .pt 15, .css 11, .pth 6)

## Summary
- 3331 nodes · 7405 edges · 179 communities (133 shown, 46 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 430 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9ea5852a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ServiceContainer
- PatchCoreImageDataset
- common_value_tool.js
- measure_weld_width_tool.js
- AGENTS.md — Quy chuẩn phát triển dự án Python Detect Width Line
- Camera
- capture_frame.js
- test_logic_slit_detector.py
- .Ok
- TrainlerPatchCore
- WeldMeamunetUnetService
- create_obj_cross_item
- border_film_tool.js
- summary_tool.js
- ._process_point
- ComService
- home.js
- JudmentLawProductRepository
- Judment
- foreign_object_tool.js
- PatchCoreInspectionService
- IAIControl
- Worker
- CalibSearchCoordinator
- WeldSeamAirBubbles
- Calibration
- patchcore_inspection_service.py
- cnd_lybrary.js
- dimetional_calibration.js
- ItemsInspector
- test_logic_armsensor.py
- test_run_judment_config_item_1_0_4.py
- add_new_product.js
- SerialConnect
- slit_tool.js
- end_chipping_tool.js
- RuntimeState
- EndChippingInspector
- ModelUnet
- ModelPatchCore
- PatchCoreTrainRecordRepository
- ndarray
- Config_SoftWare
- TestForeignObjectDetectorLogic
- model/__init__.py
- ScratchThePipeDetector
- .get_objects
- .predict
- .extract_membrane_polygons
- ManagerSerial
- update_com_config
- .__init__
- shutdown_system
- items_inspector.js
- MeasurementItemsInspector
- test_logic_measurement_welding_detector.py
- CanvasManager
- test_logic_semi_permeable_membrane.py
- Folder
- BorderFilmInspector
- SlitItemInspector
- container.py
- Infor_Software
- BorderDetector
- camera_config_panel.js
- controler.js
- DimesionalCalibrationCanvas
- IAIService
- ProductRepository
- PermeableMembraneInspector
- ScratchedPipeItemInspector
- ._load_product_data
- .save_training_input
- Pipeline
- HandlerCalibration
- handler_calibration.py
- 5. API va giao dien
- ArmCoverItemInspector
- ArmSensorItemInspector
- HoleItemInspector
- test_logic_armcoverdetector.py
- config/__init__.py
- test_logic_border_detector.py
- 4. Kien truc module
- Logic
- Log_Txt
- HandlerWorkDetect
- RectangleDrawer
- config_com.js
- CameraConfig
- SerialConfig
- config_software.js
- .fuc_update_input_queue_request_arm
- ProductService
- FrameHandlers
- AirBubblesItemInspector
- test_logic_hole.py
- Product
- ModelHandler
- .evaluate
- .wait_for_specific_data
- .send_command_stm32
- .get_segments
- .detect_anomaly_objects
- BaseConfig
- MeasurementWeldingDetector
- .crop_image
- numpy
- .error
- Tong hop du an Python Detect Width Line
- test_serial_manager.py
- PatchCoreTrainConfig
- SemiPermeableMembrane
- .run_from_folder
- ai_config.py
- SocketModel
- ProductCountRepository
- test_product_service.py
- EndChippingDetector
- VideoManager
- .worker_judget
- cv2
- Quy chế sử dụng Graphify và đọc/sửa mã nguồn trọng tâm
- .__init__
- api_product.py
- validate/__init__.py
- Point
- test_crop.py
- .send_log_html
- get_hardware_status
- .predict
- ComRepository
- .run_model_with_object_detection
- .judge_regions
- test_choose_products.py
- get_instruct_staff_ee
- test_judment_config_item_1_0_4.py
- test_logic_scratch_the_pipe.py
- .stop
- get_instruct_worker
- Senior Python & Computer Vision Web Engineer
- Workflow: graphify
- app_services_product_product
- logic/__init__.py
- runtime/__init__.py
- run.py
- .apply_config
- JudmentLawProductSevice
- Manager_Log
- JudgmentResult
- IAIConfig
- HandleClickBtnRun
- 18. Cap nhat ngay 2026-08-28
- Change_Disk
- .start_thread_handl_request_stm32
- .from_feature_file
- .compare
- calculater_calibration
- api_captureproduct.py
- .read_json_from_file
- shapely
- ProductAggregator
- .sync_config_from_camera
- ._delete_patchcore_manifest_records
- .__init__
- header_function
- get_instruct_fix_erro
- .datastream_callback
- FakeTrainer
- .convert_objects_to_original_image
- .__init__
- .__init__
- patchcore_train_record_service.py

## God Nodes (most connected - your core abstractions)
1. `ServiceContainer` - 96 edges
2. `JudgmentResult` - 61 edges
3. `IAIControl` - 58 edges
4. `create_obj_cross_item()` - 57 edges
5. `Result` - 48 edges
6. `FrameModelYoloObject` - 47 edges
7. `PatchCoreTrainRecordRepository` - 47 edges
8. `ItemsInspector` - 45 edges
9. `get_obj_product()` - 45 edges
10. `ModelPatchCore` - 44 edges

## Surprising Connections (you probably didn't know these)
- `3.2. Tập trung hóa khởi tạo dịch vụ` --references--> `ServiceContainer`  [INFERRED]
  .agents/rules/project_standards.md → app/container.py
- `13. Ket luan` --references--> `ServiceContainer`  [INFERRED]
  SOURCE_CODE_SUMMARY.md → app/container.py
- `4.10. `app/core/` va `app/validate/`` --references--> `ServiceContainer`  [INFERRED]
  SOURCE_CODE_SUMMARY.md → app/container.py
- `Law regulation / judgment` --references--> `Result`  [INFERRED]
  SOURCE_CODE_SUMMARY.md → app/core/result.py
- `16.2. Semi-permeable membrane` --references--> `JudgmentResult`  [INFERRED]
  SOURCE_CODE_SUMMARY.md → app/judger/base_ai.py

## Import Cycles
- None detected.

## Communities (179 total, 46 thin omitted)

### Community 0 - "ServiceContainer"
Cohesion: 0.09
Nodes (49): Dừng toàn bộ dịch vụ, giải phóng cổng COM, đóng Camera, ngắt luồng và giải…, Gửi log pipeline tới ô log phán định trên giao diện. Input: ``message`` là nội…, ServiceContainer, auto_create_line(), create_end_chipping_model(), create_foreign_object_model(), delete_end_chipping_model(), delete_end_chipping_runtime_image() (+41 more)

### Community 1 - "PatchCoreImageDataset"
Cohesion: 0.10
Nodes (16): CroppedImageFolder, PatchCoreImageDataset, Path, Trả về số lượng ảnh train hợp lệ. Returns: int: Số file ảnh được dataset thu…, Đọc, crop tùy chọn và transform một ảnh train. Args: index: Vị trí ảnh trong…, Khởi tạo dataset ImageFolder có crop ảnh. Args: root: Thư mục dữ liệu theo cấu…, Đọc, crop và transform một ảnh theo chỉ số dataset. Args: index: Vị trí ảnh…, Dataset đọc ảnh trực tiếp trong folder PatchCore. Args: root: Folder chứa ảnh… (+8 more)

### Community 2 - "common_value_tool.js"
Cohesion: 0.07
Nodes (53): canvasManager, HEIGH_IMG_SHAPE, scroll_container, video_product, videoManager, WIDTH_IMG_SHAPE, clearButton, closeButton (+45 more)

### Community 3 - "measure_weld_width_tool.js"
Cohesion: 0.08
Nodes (22): Measurement, obj_measure_weld_width_canvas, panner_measure_weld_width, bntJudment, boxContentMeasureWeldWidth, btnAutoRule, btnClearFrameMeasureWeldWidth, btnExitMeasureWeldWidth (+14 more)

### Community 4 - "AGENTS.md — Quy chuẩn phát triển dự án Python Detect Width Line"
Cohesion: 0.09
Nodes (22): 1.1. Thứ tự ưu tiên, 1. Mục đích và phạm vi áp dụng, 2.1. Không tự suy đoán yêu cầu, 2.2. Các trường hợp bắt buộc hỏi lại, 2.3. Cách đặt câu hỏi, 2.4. Trong thời gian chờ xác nhận, 2.5. Xác nhận trước khi triển khai, 2. Nguyên tắc làm rõ yêu cầu (Requirement Clarification) (+14 more)

### Community 5 - "Camera"
Cohesion: 0.15
Nodes (5): Camera, Lấy cấu hình camera hiện tại. Input: không có. Output: dictionary JSON-…, Trả về True nếu chụp & lưu ảnh thành công, Hiển thị ảnh sau khi chụp bằng OpenCV. :param img: Khung hình (numpy array) cần…, Bật trigger -> chụp 1 ảnh -> lưu ảnh -> tắt trigger Return: (status, image,…

### Community 6 - "capture_frame.js"
Cohesion: 0.08
Nodes (32): anonymous, btn_add_frame, btn_add_point, btn_erase_frame, btn_run_frame, btn_run_product, btn_stream_video, coordinate_after_taking_photo (+24 more)

### Community 7 - "test_logic_slit_detector.py"
Cohesion: 0.21
Nodes (16): create_detector(), create_runtime(), main(), Kiểm tra Judment dùng đúng tọa độ SlitWeldInspector để đo polygon., Kiểm tra line không cắt polygon luôn là NG., Kiểm tra widthMin lớn hơn hoặc bằng widthMax bị từ chối., Chạy toàn bộ test logic SlitDetector bằng Python thường., Tạo SlitDetector với polygon chữ nhật giả. Input: Không có. Output: Detector và… (+8 more)

### Community 8 - ".Ok"
Cohesion: 0.04
Nodes (43): Result, ndarray, Trích xuất đa giác đường biên từ ảnh bằng ModelUnet và trả về đối tượng Result.…, Chạy inference model PatchCore mẻ đầu ống của một Point và vẽ viền vàng cam như…, ndarray, Lấy danh sách đối tượng theo label trong vùng kiểm tra sau khi quy đổi tọa độ…, Chức năng: Tạo mới hoàn toàn cấu hình Calibration cho một Frame từ một đối…, Chức năng: Xóa bỏ thông số cấu hình Calibration của Frame và dọn dẹp node cha… (+35 more)

### Community 9 - "TrainlerPatchCore"
Cohesion: 0.08
Nodes (23): Khởi tạo facade với PointService và worker train. Args: point_service: Service…, PatchCoreTrainRequest, Any, Path, Queue, Worker chạy train PatchCore trên thread riêng., Đưa một ảnh vào queue train. Args: image: PIL.Image, NumPy array hoặc bytes…, Lấy kết quả train hoặc lỗi từ result_queue. Args: timeout: Thời gian tối đa chờ… (+15 more)

### Community 10 - "WeldMeamunetUnetService"
Cohesion: 0.05
Nodes (26): Vẽ danh sách các đoạn thẳng đo đạc (đã hoặc chưa kéo dài) lên bề mặt ảnh. Args:…, Vẽ các điểm lấy mẫu từ biên đa giác (polygon) lên bề mặt ảnh dưới dạng hình…, Kéo dài tuyến tính các đoạn thẳng hiện tại về cả hai đầu dựa theo hướng vector…, Tìm giao điểm giữa hai đoạn thẳng p1p2 và q1q2 bằng giải thuật nhân chéo…, Sinh các đoạn thẳng đo chiều rộng bằng cách bắn tia pháp tuyến từ biên hướng về…, Dự đoán mask phân đoạn từ ảnh đầu vào và trích xuất ra danh sách các đa giác…, Lấy mẫu các điểm phân bố cách đều nhau theo một khoảng nhất định dọc trên các…, Vẽ danh sách các điểm bất kỳ (ví dụ: điểm trung tâm skeleton) lên bề mặt ảnh.… (+18 more)

### Community 11 - "create_obj_cross_item"
Cohesion: 0.10
Nodes (46): event_transition_items(), getInspector(), openRectangleEditor(), removeStoredRectangle(), selectStoredRectangle(), updateHighlight(), btn_exit_arm_cover, btn_judment_arm_sensor (+38 more)

### Community 12 - "border_film_tool.js"
Cohesion: 0.11
Nodes (13): FilmBorder, Line, btn_erase_border_film, btn_exit_border_film, btn_judment_border_film, createMeasureBorderFilmTable(), func_callback_click_on_line_drawn(), func_callback_click_on_line_have_aready() (+5 more)

### Community 13 - "summary_tool.js"
Cohesion: 0.07
Nodes (33): openOptionPanel(), getNameEventActivate(), set_obj_product(), btn_border_film, btn_check_air_bubbles, btn_check_arm_cover, btn_check_arm_sensor, btn_check_end_chipping (+25 more)

### Community 14 - "._process_point"
Cohesion: 0.10
Nodes (15): Any, Path, Dừng stage nếu người dùng yêu cầu stop hoặc IAI đang ở lỗi., Xử lý một point và trả về payload JSON hóa được. Input: Dữ liệu sản phẩm đã…, Đưa sự kiện phán định vào queue gửi Socket.IO., Loại ảnh NumPy nội bộ, giữ overlay và đường dẫn ảnh đã lưu., Chuyển payload judgment về kiểu có thể truyền qua Socket.IO., Tạo thư mục lưu dữ liệu của một item trong một session. (+7 more)

### Community 15 - "ComService"
Cohesion: 0.24
Nodes (4): ComService, Hàm này chờ tín hiệu cụ thể từ manager_serial.Chờ thời gian timeout giây.Sau…, Gửi dữ liệu và chờ ARM xác nhận. Returns: True : nhận đúng phản hồi False :…, Kiểm tra dữ liệu có đúng định dạng không và chuyển đổi về định dạng chuẩn. Ví…

### Community 16 - "home.js"
Cohesion: 0.07
Nodes (41): get_com_connection(), set_camera_connection(), set_com_connection(), SocketData, btn_left, btn_reset_count_total, btn_right, circle_status_connect_camera (+33 more)

### Community 17 - "JudmentLawProductRepository"
Cohesion: 0.07
Nodes (19): JudmentLawProductRepository, Khởi tạo repository, tạo file nếu chưa có và nạp dữ liệu., Lấy dữ liệu Product. Args: product_id: ID sản phẩm. Returns: dict: Dữ liệu…, Lấy dữ liệu Frame. Args: product_id: ID sản phẩm. frame_id: ID Frame. Returns:…, Lấy danh sách Product ID. Returns: list[str]: Danh sách Product ID., Lấy danh sách Frame ID. Args: product_id: ID sản phẩm. Returns: list[str]: Danh…, Lấy danh sách Item ID. Args: product_id: ID sản phẩm. frame_id: ID Frame.…, Nạp dữ liệu từ dict. Args: raw: Dữ liệu nguồn. merge: True để gộp, False để ghi… (+11 more)

### Community 18 - "Judment"
Cohesion: 0.10
Nodes (23): InspectorTask, Judment, Any, ndarray, Path, Cấu hình một inspector trong một lần kiểm tra ảnh. Input: inspector: Instance…, Chuyển object config thành danh sách task có thể thực thi. Input: config:…, Alias dễ đọc hơn cho ``run``. Input: Giống ``run``. Output: Dictionary kết quả… (+15 more)

### Community 19 - "foreign_object_tool.js"
Cohesion: 0.10
Nodes (35): boxContentForeignObject, obj_region_foreign_object_canvas, panner_region_foreign_object, write_log_append(), activateForeignObjectPanel(), btnCreateModel, btnDeleteModel, btnDetectObject (+27 more)

### Community 20 - "PatchCoreInspectionService"
Cohesion: 0.09
Nodes (18): PatchCoreInspectionService, Image, ndarray, Path, Lưu ảnh crop vào thư mục runtime/good của session hiện tại để phục vụ train lại…, Resolve đúng session từ record mới nhất của Point., Tạo yêu cầu train PatchCore từ ảnh Point. Args: product_id: Mã sản phẩm.…, Chạy inference model PatchCore mới nhất của một Point. Args: product_id: Mã sản… (+10 more)

### Community 21 - "IAIControl"
Cohesion: 0.10
Nodes (7): IAIControl, Gửi lệnh Ready vào RX moniter để sẵn sàng chạy, Hàm này để xử lý logic mflow với biến input thread-safe, Hàm này xử lý khi đợi Auto, Hàm này xừ lý khi người dùng vào chế độ Auto, Hàm này xử lý đèn khi lần đầu chạy, Hàm này nhấp nháy led vì chạm cảm biến an toàn

### Community 22 - "Worker"
Cohesion: 0.16
Nodes (5): Khởi tạo tọa độ viên và cấu hình các dịch vụ liên quan. Args:…, Any, Queue, QueueManager, Worker

### Community 23 - "CalibSearchCoordinator"
Cohesion: 0.09
Nodes (17): CalibSearchCoordinator, Any, setter, Thread-safe setter cập nhật số lượng ảnh đã xử lý hoàn thành. Args: value…, Khởi chạy thuật toán tìm kiếm calib trong một luồng riêng biệt (Non-blocking)., Vòng lặp chính xử lý thuật toán Calibration: Kiểm tra kết nối, điều khiển ARM…, Lớp phối hợp tính toán hệ số calibration cho frame ID trước khi sử dụng. Bắt…, Tạo luồng mới nhưng luồng này sẽ chịu sự kiểm soát số lượng của Semaphore. (+9 more)

### Community 24 - "WeldSeamAirBubbles"
Cohesion: 0.10
Nodes (24): ndarray, Chuyển box dạng (x, y, width, height) sang (x1, y1, x2, y2). Input: box gồm bốn…, Chuẩn hóa danh sách vùng về dạng ``(x, y, width, height)``. Input: Danh sách…, Quét bọt khí độc lập trên từng vùng cấm đã cấu hình. Args: img (np.ndarray):…, So sánh luật cấm bọt khí với kết quả quét runtime. Input: ``standard_data``…, Phán định bọt khí: có bọt khí là NG, không có là OK. Input: dict kết quả từ…, WeldSeamAirBubbles, create_detector() (+16 more)

### Community 25 - "Calibration"
Cohesion: 0.09
Nodes (5): Calibration, setter, Cập nhật các tham số cấu hình bằng cách truyền tham số đặt tên trực tiếp., Cập nhật các tham số kết quả đo (Result) bằng cách truyền tham số đặt tên trực…, Chuyển đổi dữ liệu thô (dict) từ Repository sang Object định dạng trong RAM

### Community 26 - "patchcore_inspection_service.py"
Cohesion: 0.15
Nodes (15): ErrorCode, Enum, BorderFilmUnetService, ForeignObjectPatchCoreService, PatchCore service cho workflow kiểm tra dị vật., Tạo model PatchCore Dị vật với manifest riêng và session foreign., Logic dùng chung để train và chạy inference PatchCore theo từng loại kiểm tra., PermeableMembraneService (+7 more)

### Community 27 - "cnd_lybrary.js"
Cohesion: 0.15
Nodes (21): a(), i(), At(), c(), e(), Et(), f(), ft() (+13 more)

### Community 28 - "dimetional_calibration.js"
Cohesion: 0.06
Nodes (45): btn_calcular_calibration, calibration_loading, calibration_loading_bar, calibration_loading_percent, calibration_loading_status, cancel_calibration_button, config_calibration, coordinate_items_now (+37 more)

### Community 29 - "ItemsInspector"
Cohesion: 0.06
Nodes (3): Frame, Product, ItemsInspector

### Community 30 - "test_logic_armsensor.py"
Cohesion: 0.23
Nodes (14): create_detector(), main(), Kiểm tra compare từ chối chuẩn hoặc runtime sai cấu trúc., Chạy các kiểm tra logic ArmSensorDetector và báo kết quả console. Input: Không…, Tạo ArmSensorDetector với kết quả search giả. Input: ``search_result`` là…, Kiểm tra evaluate trả OK khi runtime có Sensor Arm., Kiểm tra evaluate trả NG khi cấu hình yêu cầu Sensor Arm nhưng không phát hiện., Kiểm tra evaluate trả OK khi vùng được cấu hình không có Sensor Arm. (+6 more)

### Community 31 - "test_run_judment_config_item_1_0_4.py"
Cohesion: 0.08
Nodes (30): Cấu hình cho mô hình YOLO Segment., YoloSegmentConfig, FrameModelYoloSegment, ModelYoloSegment, Warmup mô hình. Args: None Returns: None, Giải phóng mô hình. Args: None Returns: None, YOLO Segment sử dụng Ultralytics., Khởi tạo mô hình. Args: config: Cấu hình mô hình. Returns: None (+22 more)

### Community 32 - "add_new_product.js"
Cohesion: 0.14
Nodes (15): add_product, btn_cancel_delete, btn_confirm_delete, close_add_product, createDataShowTable(), form_add_new_product, imageInput, overlay_accpet_delete_product (+7 more)

### Community 33 - "SerialConnect"
Cohesion: 0.11
Nodes (9): Đóng handle COM hiện tại và xóa trạng thái kết nối. Input: không có. Output:…, Ghi một lệnh xuống COM đang mở. Input: ``data`` là chuỗi lệnh không kèm newline…, Kiểm tra cổng serial có đang bị sử dụng hay không. Args: port_name (str): Tên…, Mở cổng COM và chỉ thành công khi handle thực sự đang mở. Input: không có; sử…, SerialConnect, test_check_port_busy(), test_check_port_exists(), test_list_ports() (+1 more)

### Community 34 - "slit_tool.js"
Cohesion: 0.09
Nodes (14): LineDrawer, ModelSlit, boxContentMeasureSlitWidth, obj_measure_slit_width_canvas, panner_measure_slit_width, btn_clear_slit, btn_exit_slit, btn_judment_slit (+6 more)

### Community 35 - "end_chipping_tool.js"
Cohesion: 0.10
Nodes (29): boxContentEndChipping, obj_region_end_chipping_canvas, panner_region_end_chipping, activateEndChippingPanel(), btn_create_model_end_chipping, btn_delete_model_end_chipping, btn_exit_end_chipping, btn_judment_end_chipping (+21 more)

### Community 36 - "RuntimeState"
Cohesion: 0.08
Nodes (13): Lưu trạng thái dùng chung giữa pipeline và các service. Input: không có.…, Cập nhật trạng thái tổng thể của pipeline., Đọc trạng thái tổng thể hiện tại của pipeline., Cập nhật trạng thái kết nối COM và camera., Trả về ``(com_connected, camera_connected)``., Cập nhật cờ sản phẩm đang được phán định., Đọc cờ sản phẩm đang được phán định., Lưu kết quả sản phẩm cuối cùng cho stage export hoặc client. (+5 more)

### Community 38 - "ModelUnet"
Cohesion: 0.05
Nodes (44): UnetConfig, ModelUnet, Vẽ đa giác xấp xỉ lên ảnh gốc. Args: image (np.ndarray): Ảnh gốc (BGR) cần vẽ…, Lớp thực hiện khởi tạo, dự đoán và xử lý hậu kỳ cho mô hình Unet++. Kế thừa từ…, Thực hiện feed-forward ảnh qua mô hình để lấy mặt nạ phân đoạn (binary mask).…, Giải phóng mô hình khỏi bộ nhớ RAM và VRAM (GPU). Chuyển trọng số về CPU, xóa…, Chạy thử nghiệm mô hình (Warmup) với một ảnh đen (dummy image). Mục đích giúp…, Khởi tạo cấu hình, kiểm tra file trọng số và tải mô hình lên thiết bị phần… (+36 more)

### Community 39 - "ModelPatchCore"
Cohesion: 0.05
Nodes (52): PatchCoreAnomalyConfig, FramePatchCoreObjectDetector, Khởi tạo detector. Input: patch_core_frame: instance ``FrameModelPatchCore`` đã…, Chạy PatchCore để tìm vùng bất thường, rồi infer bằng YOLO Object trên từng…, FrameModelPatchCore, Khởi tạo frame processor. Input: ``model`` là instance ``ModelPatchCore`` đã…, Chạy PatchCore trên một ROI và quy đổi kết quả về ảnh gốc. ``ModelPatchCore``…, ModelPatchCore (+44 more)

### Community 40 - "PatchCoreTrainRecordRepository"
Cohesion: 0.10
Nodes (21): PatchCoreTrainRecordRepository, Any, Path, Ghi danh sách record vào file manifest. Args: items: Danh sách metadata cần…, Quản lý lịch sử train mô hình PatchCore theo từng phiên. Mỗi phiên train được…, Kiểm tra record có cùng ROI với phiên train hiện tại không., Chuyển object config sang dict JSON-safe. Args: config: Object config dataclass…, Lưu metadata của phiên train vào manifest. Args: config: Cấu hình train.… (+13 more)

### Community 41 - "ndarray"
Cohesion: 0.11
Nodes (14): ndarray, Thực hiện tính toán độ bất thường tổng thể và sinh bản đồ nhiệt (Heatmap…, Dự đoán anomaly score, tạo heatmap overlay và trích xuất bounding boxes theo…, Chạy thử nghiệm mô hình (Warmup) với một ảnh đen (dummy image) giúp khởi tạo…, Dự đoán và trích xuất trực tiếp ảnh gốc được vẽ đè các khung bao quanh vùng bất…, Tính toán phân ngưỡng động bản đồ bất thường, lọc nhiễu hạt và trích xuất danh…, Gộp các box bất thường giao nhau hoặc nằm trong cùng một vùng. Args: boxes:…, Kiểm tra hai box có giao nhau với diện tích dương hay không. (+6 more)

### Community 42 - "Config_SoftWare"
Cohesion: 0.09
Nodes (3): Config_SoftWare, Quản lý cấu hình phần mềm & đường dẫn log, Thay đổi đường dẫn log theo tên sản phẩm. - name_product phải là chuỗi và độ…

### Community 43 - "TestForeignObjectDetectorLogic"
Cohesion: 0.11
Nodes (10): Nhánh 3: Score > threshold và YOLO CÓ phát hiện dị vật -> Kết quả LỖI (NG)., Kiểm tra khả năng tương thích với nhiều kiểu dữ liệu standard_data., Kiểm tra toàn bộ chu trình chuẩn evaluate(): define -> compare -> judge., Kiểm thử đơn vị logic phán định độc lập của ForeignObjectDetector., Thiết lập môi trường mock trước mỗi bài kiểm tra., Kiểm tra khởi tạo detector với model không đúng chuẩn hợp đồng., Kiểm tra define truyền chính xác tham số threshold xuống engine model., Nhánh 1: Score bất thường runtime <= threshold cài đặt -> Kết quả ĐẠT (OK). (+2 more)

### Community 44 - "model/__init__.py"
Cohesion: 0.07
Nodes (21): CalibrationConfig, Line, CalibrationReponsitory, Chức năng: Đọc toàn bộ dữ liệu cấu hình từ file JSON. Input: None Output: dict…, Chức năng: Ghi đè cấu trúc dữ liệu dictionary hiện tại xuống file cấu hình…, Khởi tạo Repository quản lý file dữ liệu cấu hình các điểm (Points). Nếu file…, PointRepository, CalibrationService (+13 more)

### Community 45 - "ScratchThePipeDetector"
Cohesion: 0.20
Nodes (6): ndarray, Định nghĩa, đánh giá trạng thái và trả về ảnh trực quan của Scratch The Pipe.…, Kiểm tra vùng ảnh không được xuất hiện Scratch. Input: ``standard_data`` phải…, Phán định Scratch: có object là NG, không có object là OK. Input: dict kết quả…, ScratchThePipeDetector, 18.6. Scratch va Air Bubble

### Community 46 - ".get_objects"
Cohesion: 0.18
Nodes (10): ndarray, Vẽ khung chữ nhật lên ảnh., Nhận diện và kiểm tra đối tượng của một class trong vùng ảnh chỉ định. Args:…, Kiểm tra xem vùng chỉ định có SẠCH/TRỐNG (không chứa vật thể mục tiêu) hay…, Lấy danh sách các đối tượng detect được trên ảnh gốc (bằng cách infer trên vùng…, Kiểm tra xem vùng chỉ định có HOÀN TOÀN TRỐNG (không chứa bất kỳ vật thể nào)…, Vẽ bounding box và nhãn của danh sách đối tượng lên một bản sao của ảnh. Args:…, Hiển thị ảnh kết quả detection bằng cửa sổ OpenCV. Args: image: Ảnh gốc hoặc… (+2 more)

### Community 47 - ".predict"
Cohesion: 0.16
Nodes (9): Any, ndarray, Vẽ polygon của các segment lên ảnh. Args: image: Ảnh đầu vào. segments: Danh…, Thực hiện suy luận và vẽ kết quả lên ảnh. Args: image: Ảnh đầu vào. show_label:…, Hiển thị ảnh. Args: image: Ảnh cần hiển thị. window_name: Tên cửa sổ. Returns:…, Tiền xử lý ảnh. Args: image: Ảnh đầu vào. Returns: Any: Ảnh sau tiền xử lý., Thực hiện suy luận. Args: image: Ảnh đầu vào. Returns: Results: Kết quả suy…, Lấy danh sách kết quả segment. Args: image: Ảnh đầu vào. Returns: list[dict]:… (+1 more)

### Community 48 - ".extract_membrane_polygons"
Cohesion: 0.33
Nodes (4): ndarray, Trích xuất đa giác của màng bán thấm. Args: img: Ảnh gốc. x1, y1, x2, y2: Tọa…, Trích xuất polygon đầu tiên thuộc class xuất hiện đầu tiên trong danh sách…, Chuyển tọa độ từ Canvas sang ảnh gốc. Args: x_start, y_start, x_end, y_end: tọa…

### Community 49 - "ManagerSerial"
Cohesion: 0.13
Nodes (5): ManagerSerial, Queue, Tạo queue riêng cho một consumer nhận bản tin Serial. Input: không có. Output:…, Dừng luồng kiểm tra COM, RX/TX và đóng cổng serial., 14.3. COM configuration

### Community 50 - "update_com_config"
Cohesion: 0.25
Nodes (8): ComConnectionUpdate, open_panel_com(), BaseModel, post, Payload cấu hình cổng COM từ giao diện web., Tương thích endpoint cũ, trả dữ liệu để mở panel COM., Cập nhật cổng COM, lưu JSON và mở kết nối mới., update_com_config()

### Community 51 - ".__init__"
Cohesion: 0.07
Nodes (16): ArmCoverDetector, ndarray, Định nghĩa và đánh giá trạng thái của linh kiện Cover Arm trong vùng chỉ định.…, So sánh yêu cầu tồn tại Cover Arm với output của ``define``. Input:…, Phán định Cover Arm và trả về đầy đủ dữ liệu OK/NG. Input: dict kết quả từ…, ArmSensorDetector, ndarray, Định nghĩa, đánh giá trạng thái và trả về ảnh trực quan của linh kiện Arm… (+8 more)

### Community 52 - "shutdown_system"
Cohesion: 0.29
Nodes (7): _delayed_exit(), post, Request, Chờ một khoảng thời gian ngắn để server trả về response cho client trước khi…, Dừng toàn bộ hệ thống, ngắt các luồng, đóng Camera, COM và giải phóng bộ nhớ.…, shutdown_system(), JSONResponse

### Community 55 - "test_logic_measurement_welding_detector.py"
Cohesion: 0.15
Nodes (20): create_detector(), create_runtime(), main(), Kiểm tra Measurement không kéo dài line ngoài tọa độ cấu hình. Input: Ba đoạn…, Kiểm tra tọa độ chuẩn được dùng làm line đo trên polygon runtime. Input: Cấu…, Chỉ chạy UNet một lần khi hai detector cùng model đo cùng ảnh. Input: Cấu hình…, Lưu crop từng ROI và full-frame thực nhận của inspector đo line. Input: Ảnh giả…, Xác nhận ảnh train được ghi trước khi model UNet nhận ảnh. Input: Một item… (+12 more)

### Community 57 - "test_logic_semi_permeable_membrane.py"
Cohesion: 0.22
Nodes (16): create_detector(), main(), Luật cố định phải từ chối standard_data khác True., Chạy test logic SemiPermeableMembrane và báo kết quả console. Input: Không có.…, Tạo detector với kết quả segmentation giả. Input: ``border_segments`` và…, Tạo một segment polygon tối thiểu cho test., Inner nằm hoàn toàn trong border phải trả về OK., Inner đè lên border phải trả về NG. (+8 more)

### Community 58 - "Folder"
Cohesion: 0.12
Nodes (9): Folder, Path, Tạo folder nếu chưa tồn tại và trả về đường dẫn tuyệt đối. :param folder_name:…, Tạo toàn bộ thư mục từ đường dẫn nếu chưa tồn tại :param path: đường dẫn đầy đủ…, Đảm bảo thư mục và file tồn tại; tự động tạo nếu chưa có và trả về đường dẫn…, Lấy đường dẫn thư mục cha và nối thêm tên mới dùng thư viện os., Tạo folder nếu chưa tồn tại và trả về đường dẫn tuyệt đối., Lấy đường dẫn thư mục cha của file GỌI hàm này và nối thêm tên mới. (+1 more)

### Community 61 - "container.py"
Cohesion: 0.11
Nodes (24): 3.1. Bảo toàn Pipeline 3 giai đoạn, EnumMode, Enum, AppContext, Enum, Các trạng thái tổng quát của pipeline runtime., RuntimePipelineState, Sắp xếp ID số trước ID chữ. (+16 more)

### Community 63 - "BorderDetector"
Cohesion: 0.13
Nodes (13): BorderDetector, Any, ndarray, Khởi tạo BorderDetector với một thực thể của ModelUnet. Args: unet_model…, Vẽ polygon, line kiểm tra và giao điểm lên ảnh output. Input: Ảnh BGR, polygon…, Hiển thị ảnh kết quả BorderDetector bằng cửa sổ OpenCV. Input: ``image`` là ảnh…, Nhận vào ảnh gốc, tự động chạy qua ModelUnet để lấy polygon, sau đó tìm giao…, Đo giao điểm của từng đoạn line hữu hạn với polygon đã có. Input: ảnh gốc, danh… (+5 more)

### Community 64 - "camera_config_panel.js"
Cohesion: 0.17
Nodes (13): balanceAuto, balanceInputs, cameraConfigButton, cameraConfigFields, cameraConfigLog, cameraConfigPanel, openCameraConfigPanel(), renderCameraConfig() (+5 more)

### Community 65 - "controler.js"
Cohesion: 0.12
Nodes (9): choose_product, close_choose_product, container, overlay_choose_product, btn_instruct_fix_erro, btn_instruct_staff_ee, btn_instruct_worker, btn_out_app (+1 more)

### Community 71 - "._load_product_data"
Cohesion: 0.20
Nodes (6): PreparedProduct, Lấy scale calibration đầu tiên hợp lệ, mặc định 1.0., Dữ liệu đã chuẩn hóa để Stage 2 xử lý tuần tự., Nạp points, judgment law, calibration và chuyển sang Stage 2. Input: dữ liệu…, Đọc một file JSON object. Input: ``path`` là đường dẫn file JSON. Output:…, Ghép bốn nguồn JSON thành danh sách frame/point có judgment config.

### Community 72 - ".save_training_input"
Cohesion: 0.18
Nodes (7): add_product(), post, ndarray, Path, Lưu ảnh thực sự đưa vào model theo folder riêng inspector. Input: Ảnh BGR đã…, Vẽ ROI có nhãn Unicode dễ đọc trực tiếp lên ảnh BGR. Input: Ảnh BGR, box (x1,…, UploadFile

### Community 73 - "Pipeline"
Cohesion: 0.26
Nodes (5): Pipeline, Chuyển sang Stage 1 sau tín hiệu Reset của IAI., Theo dõi cạnh nhấn Reset và khóa Reset trong lúc phán định., Gửi log pipeline vào ô ``log_judment`` qua queue hiện có., Đọc trạng thái phần cứng và trạng thái IAI, không điều khiển phần cứng.

### Community 74 - "HandlerCalibration"
Cohesion: 0.21
Nodes (4): HandlerCalibration, setter, Hàm này dùng để tạo luồng xử lý phán định sản phẩm trong đa luồng., Nếu file JSON tồn tại → đọc và trả về data. Nếu chưa tồn tại → tạo folder +…

### Community 75 - "handler_calibration.py"
Cohesion: 0.18
Nodes (6): Queue, FrameHandlersCalibration, points: list [(x,y), ...], Kiểm tra 2 đoạn thẳng p1-p2 và p3-p4 có cắt nhau không Nếu có trả về tọa độ…, Vẽ polygon lên ảnh Parameters: image (np.ndarray): Ảnh gốc (BGR) polygon…, statistics

### Community 76 - "5. API va giao dien"
Cohesion: 0.20
Nodes (10): 5. API va giao dien, Calibration, Camera, Capture product, COM va Socket.IO, Draw regulations, Home, Law regulation / judgment (+2 more)

### Community 80 - "test_logic_armcoverdetector.py"
Cohesion: 0.23
Nodes (14): create_detector(), main(), Tạo detector với model giả trả về kết quả định trước. Input: ``search_result``…, Kiểm tra compare từ chối cấu hình chuẩn không phải bool., Chạy toàn bộ test ArmCoverDetector và báo kết quả ra console., Kiểm tra evaluate trả OK khi cấu hình yêu cầu và model phát hiện Cover Arm., Kiểm tra evaluate trả NG khi cấu hình yêu cầu Cover Arm nhưng model không phát…, Kiểm tra evaluate trả OK khi cấu hình yêu cầu vùng không có Cover Arm. (+6 more)

### Community 81 - "config/__init__.py"
Cohesion: 0.09
Nodes (18): QueueConfig, Log_Img, Aggregate, Nếu gặp ':\\' trong đường dẫn thì loại bỏ và chèn target_drive vào. Ví dụ:…, Chuyển tiếng Việt sang không dấu, thay khoảng trắng bằng '_', chỉ giữ…, image_path: Đường dẫn đầy đủ tới file ảnh cần xoá, Tool_OpenCv2, csv (+10 more)

### Community 82 - "test_logic_border_detector.py"
Cohesion: 0.23
Nodes (14): create_detector(), main(), Dữ liệu chuẩn thiếu widthMin/widthMax phải báo ValueError., Chạy test logic BorderDetector và báo kết quả console. Input: Không có. Output:…, Tạo BorderDetector với polygon hình chữ nhật giả., Một ảnh có nhiều line chỉ gọi UNet một lần và lấy giao điểm chính xác., Line có khoảng cách trong min/max phải cho kết quả OK., Line đo vượt widthMax phải cho kết quả NG. (+6 more)

### Community 83 - "4. Kien truc module"
Cohesion: 0.25
Nodes (8): 4.10. `app/core/` va `app/validate/`, 4.1. `app/main.py`, 4.5. `app/engines/`, 4.6. `app/judger/`, 4.7. `app/services/`, 4.8. `app/repository/`, 4.9. `app/model/`, 4. Kien truc module

### Community 84 - "Logic"
Cohesion: 0.18
Nodes (5): Logic, ndarray, Hàm này dùng để kiểm tra xem tất cả phần tử trong danh sách có phải là số…, Kiểm tra dữ liệu có đúng định dạng không và chuyển đổi về định dạng chuẩn. Ví…, Hàm này chờ tín hiệu cụ thể từ obj_manager_serial.Chờ thời gian timeout…

### Community 86 - "HandlerWorkDetect"
Cohesion: 0.19
Nodes (6): HandlerWorkDetect, Queue, setter, Hàm này dùng để tạo luồng xử lý phán định sản phẩm trong đa luồng., ChooseProduct, ProductManager

### Community 88 - "config_com.js"
Cohesion: 0.16
Nodes (13): baudSelect, comButton, comClose, comEmptyState, comForm, comInfo, comOverlay, comPorts (+5 more)

### Community 89 - "CameraConfig"
Cohesion: 0.18
Nodes (10): CameraConfig, Any, Kiểm tra miền giá trị số cơ bản trước khi áp dụng camera. Input: không có.…, Chuyển cấu hình thành dictionary để trả về API hoặc ghi JSON. Input: không có.…, Cấu hình runtime ánh xạ trực tiếp vào camera feature file. Input: dictionary…, Cập nhật field vận hành, không cho operator sửa white balance. Input:…, 14.1. Camera configuration, 14.4. Product header va panel switching (+2 more)

### Community 90 - "SerialConfig"
Cohesion: 0.08
Nodes (17): ComConfig, Any, Tạo cấu hình web từ cấu hình serial đang được sử dụng. Input: instance…, Chuẩn hóa và xác thực giá trị nhận từ API. Input: tên cổng và baudrate bất kỳ…, Chuyển sang cấu hình mà lớp serial hiện tại sử dụng. Input: cấu hình COM đã hợp…, Kiểm tra cấu hình trước khi lưu hoặc mở cổng. Input: không có. Output: không…, Trả về dữ liệu cấu hình dùng cho API và log. Input: không có. Output:…, Cấu hình kết nối COM ở biên config của ứng dụng. Input: tên cổng COM và… (+9 more)

### Community 91 - "config_software.js"
Cohesion: 0.20
Nodes (9): btn_close_settings, btn_config_software, btn_exit_software_information, btn_software_information, overlay_config_software, renderInformationGroup(), showSoftwareInformation(), software_information_content (+1 more)

### Community 92 - ".fuc_update_input_queue_request_arm"
Cohesion: 0.18
Nodes (4): Cập nhật biến input với lock, thread-safe, Cập nhật trạng thái tất cả các biến từ chuỗi STM32, thread-safe data: chuỗi…, Cập nhật trạng thái nút và cảm biến từ RX queue của ManagerSerial., Đọc giá trị số của một bản tin input STM32. Input: chuỗi dạng ``btn_start:1``…

### Community 93 - "ProductService"
Cohesion: 0.12
Nodes (8): ProductService, Liệt kê dữ liệu product sẽ bị xóa trước khi người dùng xác nhận. Input:…, Xóa toàn bộ dữ liệu liên quan product và trả báo cáo từng nhóm. Input:…, Tạo danh sách file/thư mục có dữ liệu riêng của product., Trả về danh sách dict thông tin sản phẩm + đường dẫn ảnh web, Lấy n phần tính từ dưới lên. levels=1: lấy tên file levels=2: lấy…, Tạo ảnh màu đen channels = 1 : ảnh grayscale channels = 3 : ảnh BGR (OpenCV), Product

### Community 94 - "FrameHandlers"
Cohesion: 0.23
Nodes (5): FrameHandlers, points: list [(x,y), ...], Kiểm tra 2 đoạn thẳng p1-p2 và p3-p4 có cắt nhau không Nếu có trả về tọa độ…, p1, p2: (x, y) có thể là int hoặc float (subpixel) return: khoảng cách mm, Vẽ polygon lên ảnh Parameters: image (np.ndarray): Ảnh gốc (BGR) polygon…

### Community 96 - "test_logic_hole.py"
Cohesion: 0.23
Nodes (14): create_detector(), main(), Kiểm tra compare từ chối chuẩn hoặc runtime sai cấu trúc., Chạy các kiểm tra logic HoleDetector và báo kết quả console. Input: Không có.…, Tạo HoleDetector với kết quả search giả. Input: ``search_result`` là output giả…, Kiểm tra evaluate trả OK khi runtime có Hole., Kiểm tra evaluate trả NG khi yêu cầu Hole nhưng không phát hiện., Kiểm tra evaluate trả OK khi vùng được cấu hình không có Hole. (+6 more)

### Community 98 - "ModelHandler"
Cohesion: 0.21
Nodes (5): ModelHandler, Vẽ contours lên ảnh Parameters: image (np.ndarray): Ảnh gốc (BGR) contours…, Tìm contour ngoài cùng và lọc theo diện tích Parameters: mask (np.ndarray):…, Làm sạch mask bằng phép Morphology Opening (Erosion + Dilation) Parameters:…, Tìm contour ngoài cùng, lọc theo diện tích và xấp xỉ polygon Parameters: mask…

### Community 99 - ".evaluate"
Cohesion: 0.19
Nodes (7): Any, Chuyển kết quả phán định sang dictionary dùng cho API hoặc log., Kiểm tra mỗi judger con khai báo tên inspector riêng. Input: ``cls`` là lớp…, Thực hiện đầy đủ quy trình define, compare và judge. Input: standard_data: Dữ…, Xác định dữ liệu runtime từ input của bài toán., So sánh dữ liệu chuẩn với dữ liệu runtime., Phán định dữ liệu đã so sánh và trả về đầy đủ dữ liệu OK/NG.

### Community 100 - ".wait_for_specific_data"
Cohesion: 0.18
Nodes (5): Kiểm tra IAI đã hoàn tất về gốc trước khi cho phép di chuyển. Input:…, Gửi tọa độ đến ARM và chờ phản hồi trên queue lệnh riêng. Input: ``x``, ``y``,…, Gửi lệnh đưa ARM về gốc và chờ xác nhận. Input: ``timeout`` là thời gian chờ…, Chờ tín hiệu cụ thể từ queue_check_in_1. - expected_signal: tín hiệu mong đợi…, So khớp phản hồi ARM, kể cả dạng tọa độ có padding và hậu tố ``ok``. Input:…

### Community 101 - ".send_command_stm32"
Cohesion: 0.20
Nodes (5): show trạng thái hiện tại của của các Input Output, Luồng này đọc trạng thái từ các nút nhấn.Xủ lý Input và cập nhật trạng thái gửi…, Gửi lệnh qua ManagerSerial được truyền từ bên ngoài. Input: ``data`` là chuỗi…, Gửi lệnh xuống STM32 khi trạng thái output thay đổi, Hàm này xử lý khi người dùng nhấn nút nhấn về gốc

### Community 102 - ".get_segments"
Cohesion: 0.29
Nodes (4): ndarray, Lấy segment trên ảnh gốc. Args: image: Ảnh đầu vào. x1: Góc trái trên X. y1:…, Chuyển tọa độ segment về ảnh gốc. Args: segments: Danh sách segment. left: Tọa…, Hiển thị ảnh cùng các segment. Args: image: Ảnh gốc. segments: Danh sách…

### Community 103 - ".detect_anomaly_objects"
Cohesion: 0.50
Nodes (3): ndarray, Trả về score PatchCore, heatmap và danh sách đối tượng YOLO chỉ trên các vùng…, Tìm vùng bất thường bằng PatchCore và infer YOLO trên từng vùng đó. Input:…

### Community 105 - "MeasurementWeldingDetector"
Cohesion: 0.13
Nodes (14): MeasurementWeldingDetector, Any, ndarray, Chuyển key line trong JSON thành số nguyên., Đọc và kiểm tra năm level tăng dần của một line chuẩn., Xếp khoảng cách vào level theo ngưỡng trên bao gồm. Input: ``distance_mm`` là…, Đo giao điểm chỉ trong phạm vi từng đoạn line cấu hình. Input: ảnh runtime,…, So sánh chiều rộng runtime với level chuẩn của từng line. Input:… (+6 more)

### Community 106 - ".crop_image"
Cohesion: 0.24
Nodes (7): ndarray, Dịch box từ hệ tọa độ ROI về hệ tọa độ ảnh gốc. Input: ``boxes`` dạng ``(x, y,…, Kiểm tra ảnh và ROI trước khi crop. Input: Ảnh NumPy và bốn tọa độ ROI. Output:…, Phát hiện vùng bất thường trong ROI và trả box theo ảnh gốc. Input: image: Ảnh…, Tính anomaly score và heatmap overlay trong một ROI. Input: Ảnh NumPy và tọa độ…, Tính anomaly score, heatmap overlay và các bounding box của vùng bất thường…, Cắt ảnh theo hai điểm chéo. Args: image: Ảnh đầu vào. x1: Góc trái trên X. y1:…

### Community 107 - "numpy"
Cohesion: 0.08
Nodes (23): BaseAI, ABC, _crop_image(), main(), ndarray, Runtime test TrainlerPatchCore tren du lieu truc tiep trong workspace., Chay runtime test doc lap khong can pytest. Returns: None: In thong bao PASS…, Crop ảnh inference theo cùng tọa độ đã dùng khi train. Args: image: Ảnh BGR đọc… (+15 more)

### Community 109 - ".error"
Cohesion: 0.22
Nodes (12): apply_camera_config(), CameraConfigUpdate, _payload_values(), BaseModel, post, Khôi phục cấu hình từ file JSON và áp dụng lại vào camera., Payload cho các thông số camera operator được phép chỉnh., Lấy các giá trị khác None từ payload và báo lỗi nếu payload rỗng. Input:… (+4 more)

### Community 110 - "Tong hop du an Python Detect Width Line"
Cohesion: 0.13
Nodes (14): 11. Trang thai tong quat, 12. Thu tu nen doc khi tiep tuc phat trien, 13. Ket luan, 17. Tach output runtime khoi storage - 2026-08-28, 1. Muc dich du an, 2. Cach chay, 6. Luong nghiep vu chinh, 7. Tai nguyen model va du lieu (+6 more)

### Community 111 - "test_serial_manager.py"
Cohesion: 0.12
Nodes (4): ModeState, Enum, queue, time

### Community 112 - "PatchCoreTrainConfig"
Cohesion: 0.09
Nodes (23): PatchCoreTrainConfig, Tham số train PatchCore, không chứa đường dẫn dữ liệu của phiên train., main(), Path, test_patchcore_train_record_service_logic(), _create_roi_dataset(), main(), Path (+15 more)

### Community 113 - "SemiPermeableMembrane"
Cohesion: 0.12
Nodes (14): ndarray, Trích xuất polygon đầu tiên thuộc class xuất hiện đầu tiên trong danh sách…, Kiểm tra `polygon_inner` có nằm hoàn toàn trong `polygon_border` hay không.…, Vẽ các điểm giao (các điểm lỗi hình học) lên ảnh. Mỗi điểm được vẽ thành: - Một…, Vẽ hai polygon (border và inner) lên ảnh để trực quan hóa kết quả. Args: image…, Thực hiện suy luận segmentation cho hai lớp màng (border và inner), kiểm tra…, Hiển thị ảnh bằng OpenCV trong cửa sổ có thể resize. Chức năng: - Tạo window…, Kiểm tra luật inner phải nằm hoàn toàn trong border. Input: ``standard_data``… (+6 more)

### Community 114 - ".run_from_folder"
Cohesion: 0.12
Nodes (12): Image, ndarray, Path, Trích xuất đặc trưng patch-level cho batch ảnh. Args: batch (torch.Tensor):…, Lấy danh sách thư mục ROI từ `data_root` sắp xếp theo tên. Returns: list[Path]:…, Chuẩn hóa tọa độ crop từ config thành ``(left, top, right, bottom)``. Returns:…, Huấn luyện một ROI và lưu index FAISS + memory bank tương ứng. Args: roi_path…, Thay thế session của ROI, chép ảnh đầu vào rồi train. Args: images: Danh sách… (+4 more)

### Community 115 - "ai_config.py"
Cohesion: 0.14
Nodes (11): ClassNameModelSurfaceConfig, UnetCofigAutoDetectLineMaster, Khởi tạo service cấu hình và mô hình UNet để tự động phát hiện đường line.…, app_engines_unet_plus, main(), collections, enum, scipy_spatial (+3 more)

### Community 117 - "ProductCountRepository"
Cohesion: 0.10
Nodes (13): ProductCountRepository, Khởi tạo file json mặc định nếu file chưa tồn tại trên ổ cứng., Đọc số lượng sản phẩm OK, NG và Tổng từ file JSON. Returns: Dict[str, int]:…, Lưu dữ liệu số lượng sản phẩm vào file JSON. Args: counts (Dict[str, int]):…, Đặt lại toàn bộ số đếm OK, NG, Tổng về 0 và lưu vào file. Returns: Dict[str,…, Tăng số lượng sản phẩm theo kết quả phán định (OK hoặc NG) và cộng vào Tổng.…, Repository quản lý đọc và ghi file lưu trữ số lượng sản phẩm OK, NG và Tổng., ProductCountService (+5 more)

### Community 118 - "test_product_service.py"
Cohesion: 0.39
Nodes (7): print_result(), test_add_roi_image(), test_delete_product(), test_get_all_products(), test_get_arr_path_img_roi_product_by_id(), test_get_product(), test_update_product()

### Community 119 - "EndChippingDetector"
Cohesion: 0.13
Nodes (12): EndChippingDetector, Any, ndarray, Bộ phán định mẻ đầu ống (End Chipping Detector) sử dụng PatchCore. Sử dụng mô…, So sánh điểm số bất thường mẻ đầu ống runtime với cấu hình chuẩn. Quy tắc phán…, Khởi tạo detector phát hiện mẻ đầu ống. Args: end_chipping_model…, Thực hiện kết luận phán định cuối cùng trả về đối tượng JudgmentResult. Args:…, Trích xuất dữ liệu bất thường và phát hiện mẻ đầu ống runtime từ ảnh gốc và… (+4 more)

### Community 122 - "cv2"
Cohesion: 0.14
Nodes (24): Cấu hình cho mô hình YOLO Segment., YoloDetectObjectConfig, FrameModelYoloObject, ModelYoloObject, Release model from memory., main(), main(), main() (+16 more)

### Community 123 - "Quy chế sử dụng Graphify và đọc/sửa mã nguồn trọng tâm"
Cohesion: 0.08
Nodes (23): 1.1. Nguyên tắc bắt buộc, 1. Mục tiêu và nguyên tắc cốt lõi, 2.1. Kiểm tra trạng thái Graphify, 2.2. Truy vấn đồ thị để khoanh vùng tác động, 2.3. Cơ chế dự phòng khi Graphify không khả dụng, 2.4. Đọc mã nguồn có chọn lọc (Targeted Reading), 2.5. Xác minh trước khi sửa, 2. Quy trình trước khi sửa code (Pre-Edit Workflow) (+15 more)

### Community 124 - ".__init__"
Cohesion: 0.25
Nodes (5): Any, ndarray, So sánh điểm số bất thường runtime và dị vật phát hiện với cấu hình chuẩn. Quy…, Khởi tạo detector phát hiện dị vật. Args: foreign_object_model…, Trích xuất dữ liệu bất thường và phát hiện dị vật runtime từ ảnh gốc và ROI.…

### Community 125 - "api_product.py"
Cohesion: 0.39
Nodes (7): delete_preview(), erase_product(), get_product(), list_product(), get, Liệt kê dữ liệu product sẽ bị xóa trước khi xác nhận., select_product_new()

### Community 126 - "validate/__init__.py"
Cohesion: 0.12
Nodes (15): capture(), captureproduct_load(), erase_frame(), erase_item_img(), PointData, BaseModel, post, Xử lý tải dữ liệu ban đầu cho giao diện Lấy ảnh mẫu. Kiểm tra tình trạng sản… (+7 more)

### Community 127 - "Point"
Cohesion: 0.25
Nodes (3): Point, Path, setter

### Community 128 - "test_crop.py"
Cohesion: 0.38
Nodes (6): center_to_box(), crop_image(), main(), ndarray, Crop ảnh theo tọa độ góc trên bên trái. Args: image: Ảnh đầu vào. x: Tọa độ X.…, Chuyển tọa độ tâm thành hai góc. Args: x: Tọa độ tâm X. y: Tọa độ tâm Y. width:…

### Community 129 - ".send_log_html"
Cohesion: 0.33
Nodes (3): Hàm này xử lý khi nhả stop, Gửi log điều khiển; log queue UI được quản lý bên ngoài controller., Hàm này xử lý khi có người nhấn nút Start

### Community 130 - "get_hardware_status"
Cohesion: 0.25
Nodes (8): get_hardware_status(), get_product_count(), home(), get, Request, Hiển thị màn hình chính cùng tên sản phẩm đang được chọn. Input: request…, Lấy số lượng sản phẩm OK, NG và Tổng đã lưu trong file JSON., Lấy trạng thái kết nối phần cứng thực tế cho Camera và cổng COM.

### Community 131 - ".predict"
Cohesion: 0.38
Nodes (4): ndarray, Preprocess input image. Args: image: Input image. Returns: Preprocessed image., Run object detection. Args: image: Input image. Returns: YOLO prediction result., Lấy danh sách kết quả detect và kiểm tra chạm biên trục X, Y. Args: image: Ảnh…

### Community 133 - ".run_model_with_object_detection"
Cohesion: 0.33
Nodes (3): Chuyển box ``(x, y, width, height)`` thành object response., Crop và mã hóa PNG từng vùng PatchCore bất thường., Chạy PatchCore và nhận diện YOLO trên từng vùng bất thường. Args: product_id:…

### Community 134 - ".judge_regions"
Cohesion: 0.33
Nodes (4): ndarray, Lấy danh sách đối tượng theo label trong vùng kiểm tra sau khi quy đổi tọa độ…, Phán định bọt khí trong nhiều vùng kiểm tra trên ảnh. Args: image: Ảnh master…, 20.3. API chay model va Air Bubble

### Community 135 - "test_choose_products.py"
Cohesion: 0.22
Nodes (6): ChooseProductRepository, ChooseProductService, print_result(), test_get_choose_product(), test_reset_choose_product(), test_set_choose_product_valid()

### Community 136 - "get_instruct_staff_ee"
Cohesion: 0.50
Nodes (4): get_instruct_staff_ee(), FileResponse, get, Trả về file PDF tài liệu hướng dẫn sử dụng phần mềm dành cho kỹ sư EE để xem…

### Community 137 - "test_judment_config_item_1_0_4.py"
Cohesion: 0.19
Nodes (11): create_recording_inspector(), judge(), load_item_config(), main(), Kiểm tra Judment điều phối đúng config item 1/0/4 trên một ảnh. Input:…, Tạo detector giả có tên đúng với key trong cấu hình. Input: Tên inspector cần…, Đọc cấu hình judgment của product 1, frame 0, item 4. Input: Không có. Output:…, Kiểm tra ảnh runtime có khung ROI xanh và nhãn lỗ thủng rõ ràng. Input: Ảnh đen… (+3 more)

### Community 138 - "test_logic_scratch_the_pipe.py"
Cohesion: 0.26
Nodes (12): create_detector(), main(), Tạo ScratchThePipeDetector với model phủ định giả. Input: ``runtime_result`` là…, Khi phát hiện Scratch, vùng không sạch và kết quả phải là NG., Khi không phát hiện Scratch, vùng sạch và kết quả phải là OK., Kiểm tra compare từ chối chuẩn và runtime sai cấu trúc., Kiểm tra judge báo lỗi khi thiếu dữ liệu so sánh bắt buộc., Chạy test logic ScratchThePipeDetector và báo kết quả console. Input: Không có.… (+4 more)

### Community 139 - ".stop"
Cohesion: 0.25
Nodes (5): Hàm này dùng để dừng luồng này dùng để khi giải phóng phần mềm, Hàm này dùng để dừng luồng này dùng để khi giải phóng phần mềm, Dừng luồng đọc dữ liệu đầu vào từ các nút nhấn vật lý của STM32., Dừng luồng chính xử lý logic và gửi dữ liệu Output tới STM32., Dừng toàn bộ các luồng hoạt động của bộ điều khiển STM32/IAI.

### Community 141 - "get_instruct_worker"
Cohesion: 0.50
Nodes (4): get_instruct_worker(), FileResponse, get, Trả về file PDF tài liệu hướng dẫn sử dụng phần mềm cho người thao tác để xem…

### Community 142 - "Senior Python & Computer Vision Web Engineer"
Cohesion: 0.50
Nodes (3): 1. Năng lực cốt lõi, 2. Nguyên tắc giao tiếp & Thực thi, Senior Python & Computer Vision Web Engineer

### Community 143 - "Workflow: graphify"
Cohesion: 0.40
Nodes (4): 1. Khởi tạo toàn diện (Full Build), 2. Tra cứu & Phân tích tác động (Impact Analysis), 3. Cập nhật gia tăng sau khi code (Incremental Update), Workflow: graphify

### Community 152 - ".apply_config"
Cohesion: 0.18
Nodes (6): Ghi giá trị float vào node camera. Input: tên node và giá trị số. Output: không…, Áp dụng cấu hình hiện tại vào các node camera. Input: không có, sử dụng…, Áp dụng tạm thời field vận hành mà chưa lưu file. Input: dictionary field vận…, Cập nhật, lưu file và áp dụng cấu hình vận hành. Input: dictionary field vận…, Nạp lại features.cfg để khôi phục camera sau thao tác thất bại. Input: không…, Ghi trực tiếp nodemap hiện tại vào file features.cfg. Input: không có; sử dụng…

### Community 153 - "JudmentLawProductSevice"
Cohesion: 0.21
Nodes (6): JudmentLawProductSevice, Tên tương thích cũ của ``convert_canvas_coordinates``. Input, output và lỗi:…, Xác định inspector chứa nhiều line/rectangle con. Input: Dict cấu hình của một…, Lấy chi tiết dữ liệu của một Item cụ thể từ Product và Frame. Args: product_id:…, Kiểm tra payload judgment là một phần hợp lệ của cây point/frame. Args: data:…, Chuyển tọa độ mọi inspector từ canvas sang pixel ảnh master. Input: ``data`` là…

### Community 154 - "Manager_Log"
Cohesion: 0.24
Nodes (4): Log_CSV, Manager_Log, Queue, Dừng luồng ghi log an toàn.

### Community 155 - "JudgmentResult"
Cohesion: 0.13
Nodes (22): ClassNameForeignObjectConfig, ClassNameObjectStructureDetectConfig, BaseJudgerAI, JudgmentResult, ABC, Hợp đồng chung cho các lớp AI phán định trong structure. Mỗi lớp con bắt buộc…, Lấy tên inspector cấu hình của judger. Input: Không có. Output: Tên key…, Dữ liệu đầy đủ của một lần phán định AI. (+14 more)

### Community 156 - "IAIConfig"
Cohesion: 0.24
Nodes (3): IAIConfig, Khởi tạo bộ điều khiển IAI dùng ManagerSerial bên ngoài. Input:…, main()

### Community 157 - "HandleClickBtnRun"
Cohesion: 0.53
Nodes (9): CheckData(), container_driver(), HandleClickBtnDecrease_X(), HandleClickBtnDecrease_Y(), HandleClickBtnDecrease_Z(), HandleClickBtnIncrease_X(), HandleClickBtnIncrease_Y(), HandleClickBtnIncrease_Z() (+1 more)

### Community 158 - "18. Cap nhat ngay 2026-08-28"
Cohesion: 0.25
Nodes (6): 18.1. Tach output runtime, 18.3. BorderDetector va phan dinh theo mm, 18.4. Luu master va quy doi toa do, 18.7. Cau truc test moi, 18.8. Kiem tra da thuc hien, 18. Cap nhat ngay 2026-08-28

### Community 159 - "Change_Disk"
Cohesion: 0.29
Nodes (3): Change_Disk, Hàm trả về list rỗng nếu không, Kiểm tra ổ này có đang được chọn trả về 0 nếu tồn tại nhưng chưa được chọn trả…

### Community 162 - ".compare"
Cohesion: 0.33
Nodes (4): Any, Chuyển key line trong JSON thành số nguyên., Đọc và kiểm tra khoảng widthMin/widthMax của line chuẩn., So sánh độ rộng khe runtime với khoảng chuẩn từng line. Input:…

### Community 163 - "calculater_calibration"
Cohesion: 0.22
Nodes (10): calculater_calibration(), CalibrationDeleteData, DataIn, delete_calibration(), PointData, BaseModel, post, Xóa kết quả calibration đã lưu của một frame. (+2 more)

### Community 164 - "api_captureproduct.py"
Cohesion: 0.05
Nodes (56): TypeDataSendClient, TypeSend, create_container(), get_services(), get_services_ws(), Request, WebSocket, create_app() (+48 more)

### Community 168 - ".sync_config_from_camera"
Cohesion: 0.33
Nodes (3): Đọc giá trị float từ node camera. Input: tên node cần đọc. Output: giá trị…, Đọc symbolic value của node enumeration camera. Input: tên node enumeration.…, Đồng bộ cấu hình runtime từ nodemap đã nạp từ features.cfg. Input: nodemap…

### Community 169 - "._delete_patchcore_manifest_records"
Cohesion: 0.40
Nodes (4): Path, Kiểm tra có bản ghi train thuộc product_id trong file manifest không., Xóa các bản ghi train của product_id trong file manifest PatchCore., test_product_service_manifest_cleanup()

### Community 171 - "header_function"
Cohesion: 0.50
Nodes (4): exit(), header_function(), get, Xử lý tải dữ liệu ban đầu cho giao diện Hiệu chuẩn kích thước. Kiểm tra tình…

### Community 172 - "get_instruct_fix_erro"
Cohesion: 0.50
Nodes (4): get_instruct_fix_erro(), FileResponse, get, Trả về file PDF tài liệu hướng dẫn đối ứng và xử lý lỗi hệ thống để xem trực…

## Knowledge Gaps
- **249 isolated node(s):** `AppContext`, `add_product`, `overlay_new_product`, `overlay_accpet_delete_product`, `close_add_product` (+244 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1370 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **46 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `18.5. Chuan hoa judger va inspector name` connect `.__init__` to `ScratchedPipeItemInspector`, `18. Cap nhat ngay 2026-08-28`, `BorderFilmInspector`, `ScratchThePipeDetector`, `HoleItemInspector`, `SemiPermeableMembrane`, `WeldSeamAirBubbles`, `JudgmentResult`, `AirBubblesItemInspector`, `BorderDetector`?**
  _High betweenness centrality (0.196) - this node is a cross-community bridge._
- **Why does `20.1. Judment va registry detector` connect `Judment` to `EndChippingInspector`, `ScratchedPipeItemInspector`, `MeasurementWeldingDetector`, `JudgmentResult`, `HoleItemInspector`, `BorderFilmInspector`, `18. Cap nhat ngay 2026-08-28`, `AirBubblesItemInspector`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `ServiceContainer` connect `ServiceContainer` to `get_hardware_status`, `ComRepository`, `AGENTS.md — Quy chuẩn phát triển dự án Python Detect Width Line`, `IAIControl`, `CalibSearchCoordinator`, `calculater_calibration`, `api_captureproduct.py`, `RuntimeState`, `header_function`, `update_com_config`, `.__init__`, `container.py`, `.save_training_input`, `Pipeline`, `4. Kien truc module`, `SerialConfig`, `Tong hop du an Python Detect Width Line`, `api_product.py`, `validate/__init__.py`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 71 inferred relationships involving `ServiceContainer` (e.g. with `3.2. Tập trung hóa khởi tạo dịch vụ` and `RuntimeState`) actually correct?**
  _`ServiceContainer` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `JudgmentResult` (e.g. with `ArmCoverDetector` and `ArmSensorDetector`) actually correct?**
  _`JudgmentResult` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AppContext`, `add_product`, `overlay_new_product` to the rest of the system?**
  _249 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ServiceContainer` be split into smaller, more focused modules?**
  _Cohesion score 0.08831168831168831 - nodes in this community are weakly interconnected._