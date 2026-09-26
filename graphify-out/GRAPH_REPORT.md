# Graph Report - app  (2026-09-26)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2952 nodes · 6532 edges · 152 communities (110 shown, 42 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 260 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0a98cfc5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- .Ok
- .__init__
- common_value_tool.js
- pathlib
- config/__init__.py
- Camera
- capture_frame.js
- api_product.py
- ServiceContainer
- numpy
- WeldMeamunetUnetService
- create_obj_cross_item
- ModelPatchCore
- summary_tool.js
- FrameModelPatchCore
- ModelYoloSegment
- home.js
- JudmentLawProductRepository
- Judment
- foreign_object_tool.js
- container.py
- IAIControl
- slit_tool.js
- IAIService
- WeldSeamAirBubbles
- Calibration
- StageTransform
- cnd_lybrary.js
- dimetional_calibration.js
- ItemsInspector
- PatchCoreTrainConfig
- CalibSearchCoordinator
- SlitDetector
- SerialConnect
- ProductService
- end_chipping_tool.js
- RuntimeState
- model/__init__.py
- repository/__init__.py
- border_film_tool.js
- .save_record
- TrainlerPatchCore
- Config_SoftWare
- measure_weld_width_tool.js
- weld_seamunet_unet_service.py
- ArmSensorDetector
- .error
- SemiPermeableMembrane
- .extract_membrane_polygons
- ManagerSerial
- CalibrationService
- folder.py
- api_captureproduct.py
- items_inspector.js
- MeasurementItemsInspector
- api_config_camera.py
- CanvasManager
- ModelHandler
- Folder
- BorderFilmInspector
- SlitItemInspector
- api_dimesional_calibration.py
- Infor_Software
- .get_objects
- StagePreprocess
- add_new_product.js
- DimesionalCalibrationCanvas
- EndChippingInspector
- ProductRepository
- PermeableMembraneInspector
- ScratchedPipeItemInspector
- test_logic_measurement_welding_detector.py
- TrainWorkerPatchCore
- .process_lines_from_polygon
- HandlerCalibration
- FrameHandlersCalibration
- Product
- ArmCoverItemInspector
- ArmSensorItemInspector
- HoleItemInspector
- test_logic_armcoverdetector.py
- test_logic_border_detector.py
- test_logic_hole.py
- services/__init__.py
- Point
- test_choose_products.py
- HandlerWorkDetect
- RectangleDrawer
- config_com.js
- Pipeline
- api_com.py
- .compare
- .fuc_update_input_queue_request_arm
- FrameHandlers
- JudmentLawProductSevice
- AirBubblesItemInspector
- Logic
- ComConfig
- .crop_image
- ComService
- .wait_for_specific_data
- .send_command_stm32
- Log_Txt
- Measurement
- SerialConfig
- CroppedImageFolder
- createCalibrationTable
- test_train_worker_patchcore.py
- .configure_connection
- train_worker.py
- PatchCoreImageDataset
- handler_work_detect.py
- config_software.py
- create_items_img
- Frame
- test_product_service.py
- create_recording_inspector
- Aggregate
- ._get_record_session_root
- BaseAI
- Product
- .get_segments
- .predict
- .read_json_from_file
- ComRepository
- handler_calibration.py
- test_crop.py
- .send_log_html
- SocketModel
- test_run_train_worker_patchcore.py
- .detect_anomaly_objects
- add_product
- VideoManager
- config_software.js
- move_to_selected_point
- .define
- .define
- .stop_thread_handler_stm32
- .convert_objects_to_original_image
- .handler_mode_auto
- .handler_wait_auto
- app_services_product_product
- logic/__init__.py
- runtime/__init__.py
- run.py

## God Nodes (most connected - your core abstractions)
1. `ServiceContainer` - 84 edges
2. `IAIControl` - 57 edges
3. `create_obj_cross_item()` - 56 edges
4. `JudgmentResult` - 49 edges
5. `FrameModelYoloObject` - 47 edges
6. `Result` - 45 edges
7. `get_obj_product()` - 45 edges
8. `ItemsInspector` - 42 edges
9. `Camera` - 40 edges
10. `ModelYoloObject` - 39 edges

## Surprising Connections (you probably didn't know these)
- `BorderDetector` --uses--> `JudgmentResult`  [INFERRED]
  app/judger/border_detector.py → app/judger/base_ai.py
- `MeasurementWeldingDetector` --uses--> `JudgmentResult`  [INFERRED]
  app/judger/measurement_welding_detector.py → app/judger/base_ai.py
- `Manager_Log` --uses--> `Log_Txt`  [INFERRED]
  app/services/log/log_manager.py → app/services/log/log_txt.py
- `ComConfig` --uses--> `SerialConfig`  [INFERRED]
  app/config/com_config.py → app/model/serial.py
- `TrainlerPatchCore` --uses--> `CroppedImageFolder`  [INFERRED]
  app/engines/train/patchcore_train_model/trainler.py → app/engines/train/patchcore_train_model/patchcore_datasets.py

## Import Cycles
- None detected.

## Communities (152 total, 42 thin omitted)

### Community 0 - ".Ok"
Cohesion: 0.04
Nodes (37): Result, ndarray, Trích xuất đa giác đường biên từ ảnh bằng ModelUnet và trả về đối tượng Result.…, Tạo yêu cầu train PatchCore từ ảnh Point. Args: product_id: Mã sản phẩm.…, ndarray, ndarray, Lấy danh sách đối tượng theo label trong vùng kiểm tra sau khi quy đổi tọa độ…, Phán định bọt khí trong nhiều vùng kiểm tra trên ảnh. Args: image: Ảnh master… (+29 more)

### Community 1 - ".__init__"
Cohesion: 0.04
Nodes (55): UnetConfig, ModelUnet, Vẽ đa giác xấp xỉ lên ảnh gốc. Args: image (np.ndarray): Ảnh gốc (BGR) cần vẽ…, Lớp thực hiện khởi tạo, dự đoán và xử lý hậu kỳ cho mô hình Unet++. Kế thừa từ…, Thực hiện feed-forward ảnh qua mô hình để lấy mặt nạ phân đoạn (binary mask).…, Giải phóng mô hình khỏi bộ nhớ RAM và VRAM (GPU). Chuyển trọng số về CPU, xóa…, Khởi tạo cấu hình, kiểm tra file trọng số và tải mô hình lên thiết bị phần…, Chạy thử nghiệm mô hình (Warmup) với một ảnh đen (dummy image). Mục đích giúp… (+47 more)

### Community 2 - "common_value_tool.js"
Cohesion: 0.06
Nodes (64): choose_product, close_choose_product, container, overlay_choose_product, canvasManager, HEIGH_IMG_SHAPE, scroll_container, video_product (+56 more)

### Community 3 - "pathlib"
Cohesion: 0.05
Nodes (51): PatchCoreAnomalyConfig, EndChippingPatchCoreService, Cấu hình PatchCore cho workflow kiểm tra đầu ống mẻ., Cấu hình PatchCore cho kiểm tra đầu ống mẻ., Khởi tạo service End Chipping với manifest riêng. Args: point_service: Service…, PatchCore service cho workflow kiểm tra dị vật., PatchCoreInspectionService, Image (+43 more)

### Community 4 - "config/__init__.py"
Cohesion: 0.09
Nodes (29): YoloDetectObjectConfig, FrameModelYoloObject, ModelYoloObject, Release model from memory., StructureFrameYoloService, Khởi tạo StructureFrameYoloService. Args: frame_model (FrameModelYoloObject):…, SurfaceFrameYoloService, main() (+21 more)

### Community 5 - "Camera"
Cohesion: 0.05
Nodes (23): CameraConfig, Any, Kiểm tra miền giá trị số cơ bản trước khi áp dụng camera. Input: không có.…, Chuyển cấu hình thành dictionary để trả về API hoặc ghi JSON. Input: không có.…, Đọc các giá trị camera từ file GenApi ``features.cfg``. Input: đường dẫn file…, Cấu hình runtime ánh xạ trực tiếp vào camera feature file. Input: dictionary…, Cập nhật field vận hành, không cho operator sửa white balance. Input:…, Camera (+15 more)

### Community 6 - "capture_frame.js"
Cohesion: 0.06
Nodes (51): balanceAuto, balanceInputs, cameraConfigButton, cameraConfigFields, cameraConfigLog, cameraConfigPanel, openCameraConfigPanel(), renderCameraConfig() (+43 more)

### Community 7 - "api_product.py"
Cohesion: 0.06
Nodes (46): TypeSend, create_container(), get_services(), get_services_ws(), Request, WebSocket, create_app(), lifespan() (+38 more)

### Community 8 - "ServiceContainer"
Cohesion: 0.09
Nodes (47): Gửi log pipeline tới ô log phán định trên giao diện. Input: ``message`` là nội…, ServiceContainer, auto_create_line(), create_end_chipping_model(), create_foreign_object_model(), delete_end_chipping_model(), delete_end_chipping_runtime_image(), delete_foreign_object_model() (+39 more)

### Community 9 - "numpy"
Cohesion: 0.10
Nodes (26): ClassNameModelSurfaceConfig, ClassNameObjectStructureDetectConfig, ArmCoverDetector, So sánh yêu cầu tồn tại Cover Arm với output của ``define``. Input:…, Phán định Cover Arm và trả về đầy đủ dữ liệu OK/NG. Input: dict kết quả từ…, BaseJudgerAI, JudgmentResult, ABC (+18 more)

### Community 10 - "WeldMeamunetUnetService"
Cohesion: 0.05
Nodes (27): Vẽ danh sách các đoạn thẳng đo đạc (đã hoặc chưa kéo dài) lên bề mặt ảnh. Args:…, Khởi tạo service cấu hình và mô hình UNet để tự động phát hiện đường line.…, Vẽ các điểm lấy mẫu từ biên đa giác (polygon) lên bề mặt ảnh dưới dạng hình…, Kéo dài tuyến tính các đoạn thẳng hiện tại về cả hai đầu dựa theo hướng vector…, Tìm giao điểm giữa hai đoạn thẳng p1p2 và q1q2 bằng giải thuật nhân chéo…, Sinh các đoạn thẳng đo chiều rộng bằng cách bắn tia pháp tuyến từ biên hướng về…, Dự đoán mask phân đoạn từ ảnh đầu vào và trích xuất ra danh sách các đa giác…, Lấy mẫu các điểm phân bố cách đều nhau theo một khoảng nhất định dọc trên các… (+19 more)

### Community 11 - "create_obj_cross_item"
Cohesion: 0.09
Nodes (46): event_transition_items(), getInspector(), openRectangleEditor(), removeStoredRectangle(), selectStoredRectangle(), updateHighlight(), event_transition_items(), func_callback_click_mouse_right_into_line() (+38 more)

### Community 12 - "ModelPatchCore"
Cohesion: 0.07
Nodes (27): Khởi tạo frame processor. Input: ``model`` là instance ``ModelPatchCore`` đã…, ModelPatchCore, ndarray, Chạy thử nghiệm mô hình (Warmup) với một ảnh đen (dummy image) giúp khởi tạo…, Giải phóng hoàn toàn các tài nguyên nặng của mô hình, dọn dẹp RAM của FAISS…, Lớp thực hiện khởi tạo, dự đoán bất thường và trích xuất vùng lỗi (Bounding…, Dự đoán và trích xuất trực tiếp ảnh gốc được vẽ đè các khung bao quanh vùng bất…, Tính toán phân ngưỡng động bản đồ bất thường, lọc nhiễu hạt và trích xuất danh… (+19 more)

### Community 13 - "summary_tool.js"
Cohesion: 0.07
Nodes (34): openOptionPanel(), getNameEventActivate(), set_obj_product(), btn_border_film, btn_check_air_bubbles, btn_check_arm_cover, btn_check_arm_sensor, btn_check_end_chipping (+26 more)

### Community 14 - "FrameModelPatchCore"
Cohesion: 0.08
Nodes (30): FramePatchCoreObjectDetector, Khởi tạo detector. Input: patch_core_frame: instance ``FrameModelPatchCore`` đã…, Chạy PatchCore để tìm vùng bất thường, rồi infer bằng YOLO Object trên từng…, FrameModelPatchCore, Chạy PatchCore trên một ROI và quy đổi kết quả về ảnh gốc. ``ModelPatchCore``…, ForeignObjectPatchCoreService, Chuyển box ``(x, y, width, height)`` thành object response., Crop và mã hóa PNG từng vùng PatchCore bất thường. (+22 more)

### Community 15 - "ModelYoloSegment"
Cohesion: 0.09
Nodes (24): Cấu hình cho mô hình YOLO Segment., YoloSegmentConfig, FrameModelYoloSegment, ModelYoloSegment, Any, ndarray, Warmup mô hình. Args: None Returns: None, Giải phóng mô hình. Args: None Returns: None (+16 more)

### Community 16 - "home.js"
Cohesion: 0.08
Nodes (32): get_com_connection(), set_camera_connection(), set_com_connection(), SocketData, SocketLog, btn_left, btn_right, circle_status_connect_camera (+24 more)

### Community 17 - "JudmentLawProductRepository"
Cohesion: 0.07
Nodes (18): JudmentLawProductRepository, Khởi tạo repository, tạo file nếu chưa có và nạp dữ liệu., Lấy danh sách Product ID. Returns: list[str]: Danh sách Product ID., Lấy danh sách Frame ID. Args: product_id: ID sản phẩm. Returns: list[str]: Danh…, Lấy danh sách Item ID. Args: product_id: ID sản phẩm. frame_id: ID Frame.…, Nạp dữ liệu từ dict. Args: raw: Dữ liệu nguồn. merge: True để gộp, False để ghi…, Gộp đệ quy hai dict. Args: target: Dữ liệu đích. source: Dữ liệu nguồn.…, Tạo file JSON rỗng nếu chưa tồn tại. (+10 more)

### Community 18 - "Judment"
Cohesion: 0.12
Nodes (20): InspectorTask, Judment, Any, ndarray, Cấu hình một inspector trong một lần kiểm tra ảnh. Input: inspector: Instance…, Chuyển object config thành danh sách task có thể thực thi. Input: config:…, Alias dễ đọc hơn cho ``run``. Input: Giống ``run``. Output: Dictionary kết quả…, Chạy toàn bộ tool trên một ảnh và tạo output tổng để ghi log. Input: image: Ảnh… (+12 more)

### Community 19 - "foreign_object_tool.js"
Cohesion: 0.11
Nodes (33): obj_region_foreign_object_canvas, write_log_append(), activateForeignObjectPanel(), btnCreateModel, btnDeleteModel, btnDetectObject, btnExitForeignObject, btnRunModel (+25 more)

### Community 20 - "container.py"
Cohesion: 0.12
Nodes (15): EnumMode, Enum, AppContext, Enum, Các trạng thái tổng quát của pipeline runtime., RuntimePipelineState, Tổng hợp kết quả sản phẩm, lưu file và chờ chu kỳ Reset tiếp theo. Input: kết…, StageExport (+7 more)

### Community 21 - "IAIControl"
Cohesion: 0.10
Nodes (6): IAIControl, Hàm này để mở luồng xử lý STM32, Gửi lệnh Ready vào RX moniter để sẵn sàng chạy, Hàm này để xử lý logic mflow với biến input thread-safe, Hàm này xử lý đèn khi lần đầu chạy, Hàm này nhấp nháy led vì chạm cảm biến an toàn

### Community 22 - "slit_tool.js"
Cohesion: 0.09
Nodes (14): LineDrawer, ModelSlit, boxContentMeasureSlitWidth, obj_measure_slit_width_canvas, panner_measure_slit_width, btn_clear_slit, btn_exit_slit, btn_judment_slit (+6 more)

### Community 23 - "IAIService"
Cohesion: 0.10
Nodes (8): BaseConfig, ABC, IAIConfig, ModeState, Enum, Khởi tạo bộ điều khiển IAI dùng ManagerSerial bên ngoài. Input:…, IAIService, main()

### Community 24 - "WeldSeamAirBubbles"
Cohesion: 0.11
Nodes (22): ndarray, Chuyển box dạng (x, y, width, height) sang (x1, y1, x2, y2). Input: box gồm bốn…, Chuẩn hóa danh sách vùng về dạng ``(x, y, width, height)``. Input: Danh sách…, Quét bọt khí độc lập trên từng vùng cấm đã cấu hình. Args: img (np.ndarray):…, So sánh luật cấm bọt khí với kết quả quét runtime. Input: ``standard_data``…, Phán định bọt khí: có bọt khí là NG, không có là OK. Input: dict kết quả từ…, WeldSeamAirBubbles, create_detector() (+14 more)

### Community 25 - "Calibration"
Cohesion: 0.11
Nodes (4): Calibration, setter, Cập nhật các tham số cấu hình bằng cách truyền tham số đặt tên trực tiếp., Cập nhật các tham số kết quả đo (Result) bằng cách truyền tham số đặt tên trực…

### Community 26 - "StageTransform"
Cohesion: 0.12
Nodes (15): Path, Dừng stage nếu người dùng yêu cầu stop hoặc IAI đang ở lỗi., Xử lý một point và trả về payload JSON hóa được., Đưa sự kiện phán định vào queue gửi Socket.IO., Loại ảnh NumPy nội bộ, giữ overlay và đường dẫn ảnh đã lưu., Chuyển payload judgment về kiểu có thể truyền qua Socket.IO., Tạo thư mục lưu dữ liệu của một item trong một session., Lưu ảnh master cho item không có cấu hình inspector. (+7 more)

### Community 27 - "cnd_lybrary.js"
Cohesion: 0.15
Nodes (21): a(), i(), At(), c(), e(), Et(), f(), ft() (+13 more)

### Community 28 - "dimetional_calibration.js"
Cohesion: 0.07
Nodes (21): btn_calcular_calibration, calibration_loading, calibration_loading_bar, calibration_loading_percent, calibration_loading_status, cancel_calibration_button, config_calibration, coordinate_items_now (+13 more)

### Community 30 - "PatchCoreTrainConfig"
Cohesion: 0.11
Nodes (20): PatchCoreTrainConfig, Tham số train PatchCore, không chứa đường dẫn dữ liệu của phiên train., Khởi tạo trainer PatchCore. Args: config (PatchCoreTrainConfig | None,…, main(), Path, test_patchcore_train_record_service_logic(), _create_roi_dataset(), main() (+12 more)

### Community 31 - "CalibSearchCoordinator"
Cohesion: 0.10
Nodes (16): CalibSearchCoordinator, Any, setter, Thread-safe setter cập nhật số lượng ảnh đã xử lý hoàn thành. Args: value…, Khởi chạy thuật toán tìm kiếm calib trong một luồng riêng biệt (Non-blocking)., Vòng lặp chính xử lý thuật toán Calibration: Kiểm tra kết nối, điều khiển ARM…, Lớp phối hợp tính toán hệ số calibration cho frame ID trước khi sử dụng. Bắt…, Tạo luồng mới nhưng luồng này sẽ chịu sự kiểm soát số lượng của Semaphore. (+8 more)

### Community 32 - "SlitDetector"
Cohesion: 0.12
Nodes (22): Any, Đọc và kiểm tra khoảng widthMin/widthMax của line chuẩn., So sánh độ rộng khe runtime với khoảng chuẩn từng line. Input:…, Đo độ rộng khe hàn và phán định theo khoảng min/max., Phán định toàn bộ line khe hàn thành OK hoặc NG. Input: dict output của…, SlitDetector, create_detector(), create_runtime() (+14 more)

### Community 33 - "SerialConnect"
Cohesion: 0.11
Nodes (9): Đóng handle COM hiện tại và xóa trạng thái kết nối. Input: không có. Output:…, Ghi một lệnh xuống COM đang mở. Input: ``data`` là chuỗi lệnh không kèm newline…, Kiểm tra cổng serial có đang bị sử dụng hay không. Args: port_name (str): Tên…, Mở cổng COM và chỉ thành công khi handle thực sự đang mở. Input: không có; sử…, SerialConnect, test_check_port_busy(), test_check_port_exists(), test_list_ports() (+1 more)

### Community 34 - "ProductService"
Cohesion: 0.12
Nodes (8): ProductService, Liệt kê dữ liệu product sẽ bị xóa trước khi người dùng xác nhận. Input:…, Xóa toàn bộ dữ liệu liên quan product và trả báo cáo từng nhóm. Input:…, Tạo danh sách file/thư mục có dữ liệu riêng của product., Trả về danh sách dict thông tin sản phẩm + đường dẫn ảnh web, Lấy n phần tính từ dưới lên. levels=1: lấy tên file levels=2: lấy…, Tạo ảnh màu đen channels = 1 : ảnh grayscale channels = 3 : ảnh BGR (OpenCV), Product

### Community 35 - "end_chipping_tool.js"
Cohesion: 0.10
Nodes (25): boxContentEndChipping, obj_region_end_chipping_canvas, panner_region_end_chipping, activateEndChippingPanel(), btn_create_model_end_chipping, btn_delete_model_end_chipping, btn_exit_end_chipping, btn_judment_end_chipping (+17 more)

### Community 36 - "RuntimeState"
Cohesion: 0.08
Nodes (13): Lưu trạng thái dùng chung giữa pipeline và các service. Input: không có.…, Cập nhật trạng thái tổng thể của pipeline., Đọc trạng thái tổng thể hiện tại của pipeline., Cập nhật trạng thái kết nối COM và camera., Trả về ``(com_connected, camera_connected)``., Cập nhật cờ sản phẩm đang được phán định., Đọc cờ sản phẩm đang được phán định., Lưu kết quả sản phẩm cuối cùng cho stage export hoặc client. (+5 more)

### Community 37 - "model/__init__.py"
Cohesion: 0.12
Nodes (7): Line, Any, Queue, QueueManager, Worker, MockDeploymentUnet, uuid

### Community 38 - "repository/__init__.py"
Cohesion: 0.13
Nodes (9): CalibrationReponsitory, Chức năng: Đọc toàn bộ dữ liệu cấu hình từ file JSON. Input: None Output: dict…, Chức năng: Ghi đè cấu trúc dữ liệu dictionary hiện tại xuống file cấu hình…, Khởi tạo Repository quản lý file dữ liệu cấu hình các điểm (Points). Nếu file…, PointRepository, test_calibration_service(), test_point_service(), test_point_service() (+1 more)

### Community 39 - "border_film_tool.js"
Cohesion: 0.11
Nodes (13): FilmBorder, Line, btn_erase_border_film, btn_exit_border_film, btn_judment_border_film, createMeasureBorderFilmTable(), func_callback_click_on_line_drawn(), func_callback_click_on_line_have_aready() (+5 more)

### Community 40 - ".save_record"
Cohesion: 0.11
Nodes (13): Any, Path, Ghi danh sách record vào file manifest. Args: items: Danh sách metadata cần…, Kiểm tra record có cùng ROI với phiên train hiện tại không., Chuyển object config sang dict JSON-safe. Args: config: Object config dataclass…, Lưu metadata của phiên train vào manifest. Args: config: Cấu hình train.…, Khởi tạo service với manifest trung tâm. Args: root_dir: Folder tùy chọn dùng…, Lấy record mới nhất trong manifest. Returns: dict | None: Record đầu tiên hoặc… (+5 more)

### Community 41 - "TrainlerPatchCore"
Cohesion: 0.12
Nodes (15): Image, ndarray, Path, Trích xuất đặc trưng patch-level cho batch ảnh. Args: batch (torch.Tensor):…, Lấy danh sách thư mục ROI từ `data_root` sắp xếp theo tên. Returns: list[Path]:…, Chuẩn hóa tọa độ crop từ config thành ``(left, top, right, bottom)``. Returns:…, Huấn luyện một ROI và lưu index FAISS + memory bank tương ứng. Args: roi_path…, Thay thế session của ROI, chép ảnh đầu vào rồi train. Args: images: Danh sách… (+7 more)

### Community 42 - "Config_SoftWare"
Cohesion: 0.09
Nodes (3): Config_SoftWare, Quản lý cấu hình phần mềm & đường dẫn log, Thay đổi đường dẫn log theo tên sản phẩm. - name_product phải là chuỗi và độ…

### Community 43 - "measure_weld_width_tool.js"
Cohesion: 0.11
Nodes (21): obj_measure_weld_width_canvas, panner_measure_weld_width, bntJudment, boxContentMeasureWeldWidth, btnAutoRule, btnClearFrameMeasureWeldWidth, btnExitMeasureWeldWidth, checkSelected() (+13 more)

### Community 44 - "weld_seamunet_unet_service.py"
Cohesion: 0.10
Nodes (13): UnetCofigAutoDetectLineMaster, TypeDataSendClient, CalibrationConfig, QueueConfig, app_engines_unet_plus, main(), collections, dataclasses (+5 more)

### Community 45 - "ArmSensorDetector"
Cohesion: 0.13
Nodes (18): ArmSensorDetector, ndarray, Định nghĩa, đánh giá trạng thái và trả về ảnh trực quan của linh kiện Arm…, So sánh yêu cầu tồn tại Arm Sensor với output của ``define``. Input:…, Phán định Arm Sensor và trả về đầy đủ dữ liệu OK/NG. Input: dict kết quả từ…, create_detector(), main(), Chạy các kiểm tra logic ArmSensorDetector và báo kết quả console. Input: Không… (+10 more)

### Community 46 - ".error"
Cohesion: 0.13
Nodes (17): ndarray, Định nghĩa, đánh giá trạng thái và trả về ảnh trực quan của Scratch The Pipe.…, Kiểm tra vùng ảnh không được xuất hiện Scratch. Input: ``standard_data`` phải…, Phán định Scratch: có object là NG, không có object là OK. Input: dict kết quả…, ScratchThePipeDetector, create_detector(), main(), Tạo ScratchThePipeDetector với model phủ định giả. Input: ``runtime_result`` là… (+9 more)

### Community 47 - "SemiPermeableMembrane"
Cohesion: 0.15
Nodes (19): Kiểm tra luật inner phải nằm hoàn toàn trong border. Input: ``standard_data``…, Phán định quan hệ hình học giữa inner và border. Input: dict kết quả từ…, SemiPermeableMembrane, create_detector(), main(), Luật cố định phải từ chối standard_data khác True., Chạy test logic SemiPermeableMembrane và báo kết quả console. Input: Không có.…, Tạo detector với kết quả segmentation giả. Input: ``border_segments`` và… (+11 more)

### Community 48 - ".extract_membrane_polygons"
Cohesion: 0.12
Nodes (12): PermeableMembraneService, ndarray, Khởi tạo service nhận trực tiếp hai mô hình phân đoạn YOLO., Trích xuất đa giác của màng bán thấm. Args: img: Ảnh gốc. x1, y1, x2, y2: Tọa…, ndarray, Trích xuất polygon đầu tiên thuộc class xuất hiện đầu tiên trong danh sách…, Kiểm tra `polygon_inner` có nằm hoàn toàn trong `polygon_border` hay không.…, Vẽ các điểm giao (các điểm lỗi hình học) lên ảnh. Mỗi điểm được vẽ thành: - Một… (+4 more)

### Community 49 - "ManagerSerial"
Cohesion: 0.14
Nodes (4): ManagerSerial, Queue, Tạo queue riêng cho một consumer nhận bản tin Serial. Input: không có. Output:…, Dừng luồng kiểm tra COM, RX/TX và đóng cổng serial.

### Community 50 - "CalibrationService"
Cohesion: 0.11
Nodes (11): CalibrationService, Khởi tạo dịch vụ quản lý thông số Calibration cho từng Frame. :param…, Chức năng: Tạo mới hoàn toàn cấu hình Calibration cho một Frame từ một đối…, Chức năng: Xóa bỏ thông số cấu hình Calibration của Frame và dọn dẹp node cha…, Chức năng: Kiểm tra xem thông số cấu hình Calibration của một Frame có tồn tại…, Chức năng: Kiểm tra xem thông số cấu hình Calibration của một Frame có hợp lệ…, Chức năng: Kiểm tra xem cặp product_id và frame_id có tồn tại trong hệ thống…, Chuyển đổi dữ liệu thô (dict) từ Repository sang Object định dạng trong RAM (+3 more)

### Community 51 - "folder.py"
Cohesion: 0.15
Nodes (7): Log_CSV, Log_Img, Manager_Log, Queue, Dừng luồng ghi log an toàn., inspect, psutil

### Community 52 - "api_captureproduct.py"
Cohesion: 0.14
Nodes (17): camera_ws(), capture(), captureproduct_load(), erase_frame(), erase_item_img(), exit(), PointData, BaseModel (+9 more)

### Community 55 - "api_config_camera.py"
Cohesion: 0.15
Nodes (19): apply_camera_config(), camera_status(), CameraConfigUpdate, exit_camera_config(), get_camera_config(), _payload_values(), BaseModel, get (+11 more)

### Community 57 - "ModelHandler"
Cohesion: 0.13
Nodes (7): Làm sạch mask bằng phép Morphology Opening (Erosion + Dilation) Parameters:…, Tìm contour ngoài cùng, lọc theo diện tích và xấp xỉ polygon Parameters: mask…, Dự đoán mask và làm sạch các đốm nhiễu nhỏ xung quanh bằng toán tử Opening.…, Trích xuất tọa độ đa giác xấp xỉ của vùng đối tượng lớn nhất từ ảnh đầu vào.…, ModelHandler, Vẽ contours lên ảnh Parameters: image (np.ndarray): Ảnh gốc (BGR) contours…, Tìm contour ngoài cùng và lọc theo diện tích Parameters: mask (np.ndarray):…

### Community 58 - "Folder"
Cohesion: 0.12
Nodes (9): Folder, Path, Tạo folder nếu chưa tồn tại và trả về đường dẫn tuyệt đối. :param folder_name:…, Tạo toàn bộ thư mục từ đường dẫn nếu chưa tồn tại :param path: đường dẫn đầy đủ…, Đảm bảo thư mục và file tồn tại; tự động tạo nếu chưa có và trả về đường dẫn…, Lấy đường dẫn thư mục cha và nối thêm tên mới dùng thư viện os., Tạo folder nếu chưa tồn tại và trả về đường dẫn tuyệt đối., Lấy đường dẫn thư mục cha của file GỌI hàm này và nối thêm tên mới. (+1 more)

### Community 61 - "api_dimesional_calibration.py"
Cohesion: 0.18
Nodes (14): calculater_calibration(), CalibrationDeleteData, DataIn, delete_calibration(), exit(), header_function(), PointData, BaseModel (+6 more)

### Community 63 - ".get_objects"
Cohesion: 0.18
Nodes (9): ndarray, Vẽ khung chữ nhật lên ảnh., Nhận diện và kiểm tra đối tượng của một class trong vùng ảnh chỉ định. Args:…, Lấy danh sách các đối tượng detect được trên ảnh gốc (bằng cách infer trên vùng…, Kiểm tra xem vùng chỉ định có SẠCH/TRỐNG (không chứa vật thể mục tiêu) hay…, Kiểm tra xem vùng chỉ định có HOÀN TOÀN TRỐNG (không chứa bất kỳ vật thể nào)…, Vẽ bounding box và nhãn của danh sách đối tượng lên một bản sao của ảnh. Args:…, Hiển thị ảnh kết quả detection bằng cửa sổ OpenCV. Args: image: Ảnh gốc hoặc… (+1 more)

### Community 64 - "StagePreprocess"
Cohesion: 0.14
Nodes (10): PreparedProduct, Sắp xếp ID số trước ID chữ., Lấy scale calibration đầu tiên hợp lệ, mặc định 1.0., Kiểm tra COM đã sẵn sàng mà không điều khiển ARM về gốc. Input: không có; đọc…, Dữ liệu đã chuẩn hóa để Stage 2 xử lý tuần tự., Đọc và chuẩn hóa dữ liệu sản phẩm trước khi điều khiển IAI., Nạp points, judgment law, calibration và chuyển sang Stage 2. Input: dữ liệu…, Đọc một file JSON object. Input: ``path`` là đường dẫn file JSON. Output:… (+2 more)

### Community 65 - "add_new_product.js"
Cohesion: 0.14
Nodes (15): add_product, btn_cancel_delete, btn_confirm_delete, close_add_product, createDataShowTable(), form_add_new_product, imageInput, overlay_accpet_delete_product (+7 more)

### Community 66 - "DimesionalCalibrationCanvas"
Cohesion: 0.15
Nodes (3): DimesionalCalibrationCanvas, create_line(), func_callback_click_right_mouse_on_line()

### Community 68 - "ProductRepository"
Cohesion: 0.17
Nodes (3): ProductRepository, Ghi dữ liệu dạng JSON vào file. - file_path: đường dẫn tới file json - data:…, Lấy danh sách tên các file trong một thư mục. :param folder_path: Đường dẫn tới…

### Community 71 - "test_logic_measurement_welding_detector.py"
Cohesion: 0.21
Nodes (15): create_detector(), create_runtime(), main(), Kiểm tra tọa độ chuẩn được dùng làm line đo trên polygon runtime. Input: Cấu…, Kiểm tra line không cắt polygon luôn cho kết quả NG. Input: Runtime line có…, Chạy toàn bộ test logic MeasurementWeldingDetector bằng Python thường., Tạo detector với polygon chữ nhật giả để test logic không cần model thật.…, Tạo output define giả với khoảng cách pixel bằng khoảng cách mm. Input: Khoảng… (+7 more)

### Community 72 - "TrainWorkerPatchCore"
Cohesion: 0.15
Nodes (9): Any, Đưa một ảnh vào queue train. Args: image: PIL.Image, NumPy array hoặc bytes…, Lấy kết quả train hoặc lỗi từ result_queue. Args: timeout: Thời gian tối đa chờ…, Chạy một request train trên thread nền. Returns: None., Lấy đủ ảnh từ queue hoặc dừng nếu worker nhận tín hiệu stop. Args: image_count:…, Nhận ảnh qua queue và train PatchCore trên thread nền. Worker không chặn luồng…, Khởi tạo worker chỉ chứa quy tắc xử lý queue. Args: record_manager: Repository…, Dừng thread worker sau khi xử lý các queue đang chờ. Args: timeout: Thời gian… (+1 more)

### Community 73 - ".process_lines_from_polygon"
Cohesion: 0.15
Nodes (8): ndarray, Vẽ polygon, line kiểm tra và giao điểm lên ảnh output. Input: Ảnh BGR, polygon…, Hiển thị ảnh kết quả BorderDetector bằng cửa sổ OpenCV. Input: ``image`` là ảnh…, Nhận vào ảnh gốc, tự động chạy qua ModelUnet để lấy polygon, sau đó tìm giao…, Lấy giao điểm chính xác giữa các line và polygon UNet. Input: ảnh BGR, danh…, Đo giao điểm của từng đoạn line hữu hạn với polygon đã có. Input: ảnh gốc, danh…, Lấy các điểm biên từ kết quả giao Shapely và loại điểm trùng., Tạo kết quả chuẩn cho line không hợp lệ.

### Community 74 - "HandlerCalibration"
Cohesion: 0.23
Nodes (3): HandlerCalibration, setter, Nếu file JSON tồn tại → đọc và trả về data. Nếu chưa tồn tại → tạo folder +…

### Community 75 - "FrameHandlersCalibration"
Cohesion: 0.21
Nodes (4): FrameHandlersCalibration, Kiểm tra 2 đoạn thẳng p1-p2 và p3-p4 có cắt nhau không Nếu có trả về tọa độ…, Vẽ polygon lên ảnh Parameters: image (np.ndarray): Ảnh gốc (BGR) polygon…, Convert OpenCV frame sang base64 để gửi cho client

### Community 80 - "test_logic_armcoverdetector.py"
Cohesion: 0.23
Nodes (14): create_detector(), main(), Tạo detector với model giả trả về kết quả định trước. Input: ``search_result``…, Kiểm tra compare từ chối cấu hình chuẩn không phải bool., Chạy toàn bộ test ArmCoverDetector và báo kết quả ra console., Kiểm tra evaluate trả OK khi cấu hình yêu cầu và model phát hiện Cover Arm., Kiểm tra evaluate trả NG khi cấu hình yêu cầu Cover Arm nhưng model không phát…, Kiểm tra evaluate trả OK khi cấu hình yêu cầu vùng không có Cover Arm. (+6 more)

### Community 81 - "test_logic_border_detector.py"
Cohesion: 0.23
Nodes (14): create_detector(), main(), Dữ liệu chuẩn thiếu widthMin/widthMax phải báo ValueError., Chạy test logic BorderDetector và báo kết quả console. Input: Không có. Output:…, Tạo BorderDetector với polygon hình chữ nhật giả., Một ảnh có nhiều line chỉ gọi UNet một lần và lấy giao điểm chính xác., Line có khoảng cách trong min/max phải cho kết quả OK., Line đo vượt widthMax phải cho kết quả NG. (+6 more)

### Community 82 - "test_logic_hole.py"
Cohesion: 0.23
Nodes (14): create_detector(), main(), Kiểm tra compare từ chối chuẩn hoặc runtime sai cấu trúc., Chạy các kiểm tra logic HoleDetector và báo kết quả console. Input: Không có.…, Tạo HoleDetector với kết quả search giả. Input: ``search_result`` là output giả…, Kiểm tra evaluate trả OK khi runtime có Hole., Kiểm tra evaluate trả NG khi yêu cầu Hole nhưng không phát hiện., Kiểm tra evaluate trả OK khi vùng được cấu hình không có Hole. (+6 more)

### Community 83 - "services/__init__.py"
Cohesion: 0.37
Nodes (3): ErrorCode, Enum, copy

### Community 84 - "Point"
Cohesion: 0.25
Nodes (3): Point, Path, setter

### Community 85 - "test_choose_products.py"
Cohesion: 0.20
Nodes (6): ChooseProductRepository, ChooseProductService, print_result(), test_get_choose_product(), test_reset_choose_product(), test_set_choose_product_valid()

### Community 86 - "HandlerWorkDetect"
Cohesion: 0.19
Nodes (6): Hàm này dùng để tạo luồng xử lý phán định sản phẩm trong đa luồng., HandlerWorkDetect, Queue, setter, ChooseProduct, ProductManager

### Community 88 - "config_com.js"
Cohesion: 0.16
Nodes (13): baudSelect, comButton, comClose, comEmptyState, comForm, comInfo, comOverlay, comPorts (+5 more)

### Community 89 - "Pipeline"
Cohesion: 0.24
Nodes (5): Pipeline, Chuyển sang Stage 1 sau tín hiệu Reset của IAI., Theo dõi cạnh nhấn Reset và khóa Reset trong lúc phán định., Gửi log pipeline vào ô ``log_judment`` qua queue hiện có., Đọc trạng thái phần cứng và trạng thái IAI, không điều khiển phần cứng.

### Community 90 - "api_com.py"
Cohesion: 0.18
Nodes (12): ComConnectionUpdate, get_com_config(), open_panel_com(), BaseModel, get, post, Payload cấu hình cổng COM từ giao diện web., Tương thích endpoint cũ, trả dữ liệu để mở panel COM. (+4 more)

### Community 91 - ".compare"
Cohesion: 0.18
Nodes (7): Any, ndarray, Đọc và kiểm tra năm level tăng dần của một line chuẩn., Xếp level cho kích thước đo; chỉ level 4 được xem là OK., Đo giao điểm chỉ trong phạm vi từng đoạn line cấu hình. Input: ảnh runtime,…, So sánh chiều rộng runtime với level chuẩn của từng line. Input:…, Chuyển key line trong JSON thành số nguyên.

### Community 92 - ".fuc_update_input_queue_request_arm"
Cohesion: 0.18
Nodes (4): Cập nhật biến input với lock, thread-safe, Cập nhật trạng thái tất cả các biến từ chuỗi STM32, thread-safe data: chuỗi…, Cập nhật trạng thái nút và cảm biến từ RX queue của ManagerSerial., Đọc giá trị số của một bản tin input STM32. Input: chuỗi dạng ``btn_start:1``…

### Community 93 - "FrameHandlers"
Cohesion: 0.29
Nodes (3): FrameHandlers, points: list [(x,y), ...], p1, p2: (x, y) có thể là int hoặc float (subpixel) return: khoảng cách mm

### Community 94 - "JudmentLawProductSevice"
Cohesion: 0.21
Nodes (6): JudmentLawProductSevice, Tên tương thích cũ của ``convert_canvas_coordinates``. Input, output và lỗi:…, Xác định inspector chứa nhiều line/rectangle con. Input: Dict cấu hình của một…, Lấy dữ liệu của một Frame cụ thể thuộc Product. Args: product_id: ID sản phẩm.…, So sánh cấu trúc dict, cho phép data có nhiều key hơn. Args: data: Cấu trúc…, Chuyển tọa độ mọi inspector từ canvas sang pixel ảnh master. Input: ``data`` là…

### Community 96 - "Logic"
Cohesion: 0.18
Nodes (5): Logic, ndarray, Hàm này dùng để kiểm tra xem tất cả phần tử trong danh sách có phải là số…, Kiểm tra dữ liệu có đúng định dạng không và chuyển đổi về định dạng chuẩn. Ví…, Hàm này chờ tín hiệu cụ thể từ obj_manager_serial.Chờ thời gian timeout…

### Community 97 - "ComConfig"
Cohesion: 0.22
Nodes (7): ComConfig, Any, Chuẩn hóa và xác thực giá trị nhận từ API. Input: tên cổng và baudrate bất kỳ…, Chuyển sang cấu hình mà lớp serial hiện tại sử dụng. Input: cấu hình COM đã hợp…, Kiểm tra cấu hình trước khi lưu hoặc mở cổng. Input: không có. Output: không…, Trả về dữ liệu cấu hình dùng cho API và log. Input: không có. Output:…, Cấu hình kết nối COM ở biên config của ứng dụng. Input: tên cổng COM và…

### Community 98 - ".crop_image"
Cohesion: 0.25
Nodes (6): ndarray, Phát hiện vùng bất thường trong ROI và trả box theo ảnh gốc. Input: image: Ảnh…, Tính anomaly score và heatmap overlay trong một ROI. Input: Ảnh NumPy và tọa độ…, Dịch box từ hệ tọa độ ROI về hệ tọa độ ảnh gốc. Input: ``boxes`` dạng ``(x, y,…, Kiểm tra ảnh và ROI trước khi crop. Input: Ảnh NumPy và bốn tọa độ ROI. Output:…, Cắt ảnh theo hai điểm chéo. Args: image: Ảnh đầu vào. x1: Góc trái trên X. y1:…

### Community 99 - "ComService"
Cohesion: 0.22
Nodes (4): Khởi tạo tọa độ viên và cấu hình các dịch vụ liên quan. Args:…, ComService, Hàm này chờ tín hiệu cụ thể từ manager_serial.Chờ thời gian timeout giây.Sau…, Gửi dữ liệu và chờ ARM xác nhận. Returns: True : nhận đúng phản hồi False :…

### Community 100 - ".wait_for_specific_data"
Cohesion: 0.18
Nodes (5): Kiểm tra IAI đã hoàn tất về gốc trước khi cho phép di chuyển. Input:…, Gửi tọa độ đến ARM và chờ phản hồi trên queue lệnh riêng. Input: ``x``, ``y``,…, Gửi lệnh đưa ARM về gốc và chờ xác nhận. Input: ``timeout`` là thời gian chờ…, Chờ tín hiệu cụ thể từ queue_check_in_1. - expected_signal: tín hiệu mong đợi…, So khớp phản hồi ARM, kể cả dạng tọa độ có padding và hậu tố ``ok``. Input:…

### Community 101 - ".send_command_stm32"
Cohesion: 0.20
Nodes (5): show trạng thái hiện tại của của các Input Output, Luồng này đọc trạng thái từ các nút nhấn.Xủ lý Input và cập nhật trạng thái gửi…, Gửi lệnh qua ManagerSerial được truyền từ bên ngoài. Input: ``data`` là chuỗi…, Gửi lệnh xuống STM32 khi trạng thái output thay đổi, Hàm này xử lý khi người dùng nhấn nút nhấn về gốc

### Community 105 - "SerialConfig"
Cohesion: 0.24
Nodes (3): SerialConfig, test_save_config(), serial_tools_list_ports

### Community 106 - "CroppedImageFolder"
Cohesion: 0.20
Nodes (7): CroppedImageFolder, Path, Khởi tạo dataset ImageFolder có crop ảnh. Args: root: Thư mục dữ liệu theo cấu…, Đọc, crop và transform một ảnh theo chỉ số dataset. Args: index: Vị trí ảnh…, Khởi tạo dataset ảnh phẳng của PatchCore. Args: root: Folder chứa ảnh train…, ImageFolder crop ảnh trước khi áp dụng transform. Args: root: Thư mục dữ liệu…, ImageFolder

### Community 107 - "createCalibrationTable"
Cohesion: 0.20
Nodes (10): create_hight_light_items_for_frame(), createButton(), createCalibrationTable(), func_callback_check_line_exis(), func_callback_click_on_line_drawn(), get_data_create_calibrationTable_config(), high_light_item(), selection_data_input() (+2 more)

### Community 109 - "test_train_worker_patchcore.py"
Cohesion: 0.22
Nodes (7): FakeTrainer, main(), Kiểm thử worker queue của PatchCore., Trainer giả để kiểm tra giao tiếp queue mà không chạy model thật., Worker chỉ train sau khi nhận đủ image_count ảnh. Returns: None: Kết thúc không…, Chạy test worker độc lập không cần pytest., test_train_worker_waits_for_required_images()

### Community 110 - ".configure_connection"
Cohesion: 0.22
Nodes (3): Tạo cấu hình web từ cấu hình serial đang được sử dụng. Input: instance…, Lấy cấu hình COM hiện tại và danh sách cổng serial trên máy. Input: không có.…, Đổi cổng COM, lưu cấu hình và yêu cầu ManagerSerial kết nối lại. Input:…

### Community 111 - "train_worker.py"
Cohesion: 0.28
Nodes (6): PatchCoreTrainRequest, Path, Queue, Worker chạy train PatchCore trên thread riêng., Thông tin một yêu cầu train đang chờ xử lý., Bắt đầu một phiên train trên thread nền. Args: model_root: Folder gốc lưu ảnh…

### Community 112 - "PatchCoreImageDataset"
Cohesion: 0.22
Nodes (7): PatchCoreImageDataset, Trả về số lượng ảnh train hợp lệ. Returns: int: Số file ảnh được dataset thu…, Đọc, crop tùy chọn và transform một ảnh train. Args: index: Vị trí ảnh trong…, Dataset đọc ảnh trực tiếp trong folder PatchCore. Args: root: Folder chứa ảnh…, main(), Entry point CLI; nhận đường dẫn ảnh sau cờ ``--images``., Dataset

### Community 113 - "handler_work_detect.py"
Cohesion: 0.31
Nodes (3): ProductAggregator, Trả về: None -> chưa đủ frame True/False -> đã đủ frame, trả về kết quả sản phẩm, math

### Community 114 - "config_software.py"
Cohesion: 0.25
Nodes (3): Change_Disk, Hàm trả về list rỗng nếu không, Kiểm tra ổ này có đang được chọn trả về 0 nếu tồn tại nhưng chưa được chọn trả…

### Community 115 - "create_items_img"
Cohesion: 0.25
Nodes (9): create_box(), create_calibration_table_show(), create_img_items_dimesion_calibration(), create_items_img(), extractResultParameters(), loadPointCoordinates(), render_selected_calibration_result(), renderResultTableDiv() (+1 more)

### Community 117 - "test_product_service.py"
Cohesion: 0.39
Nodes (7): print_result(), test_add_roi_image(), test_delete_product(), test_get_all_products(), test_get_arr_path_img_roi_product_by_id(), test_get_product(), test_update_product()

### Community 118 - "create_recording_inspector"
Cohesion: 0.22
Nodes (7): create_recording_inspector(), judge(), load_item_config(), main(), Tạo detector giả có tên đúng với key trong cấu hình. Input: Tên inspector cần…, Đọc cấu hình judgment của product 1, frame 0, item 4. Input: Không có. Output:…, Kiểm tra Judment điều phối đúng config item 1/0/4 trên một ảnh. Input:…

### Community 119 - "Aggregate"
Cohesion: 0.22
Nodes (5): Aggregate, Nếu gặp ':\\' trong đường dẫn thì loại bỏ và chèn target_drive vào. Ví dụ:…, Chuyển tiếng Việt sang không dấu, thay khoảng trắng bằng '_', chỉ giữ…, re, unicodedata

### Community 120 - "._get_record_session_root"
Cohesion: 0.25
Nodes (4): Resolve đúng session từ record mới nhất của Point., Lấy toàn bộ ảnh runtime/good của session mới nhất., Xóa một ảnh runtime/good trong session được ghi nhận., Xóa session model và đúng các record manifest của item hiện tại. Args:…

### Community 123 - ".get_segments"
Cohesion: 0.29
Nodes (4): ndarray, Lấy segment trên ảnh gốc. Args: image: Ảnh đầu vào. x1: Góc trái trên X. y1:…, Chuyển tọa độ segment về ảnh gốc. Args: segments: Danh sách segment. left: Tọa…, Hiển thị ảnh cùng các segment. Args: image: Ảnh gốc. segments: Danh sách…

### Community 124 - ".predict"
Cohesion: 0.38
Nodes (4): ndarray, Preprocess input image. Args: image: Input image. Returns: Preprocessed image., Run object detection. Args: image: Input image. Returns: YOLO prediction result., Lấy danh sách kết quả detect và kiểm tra chạm biên trục X, Y. Args: image: Ảnh…

### Community 127 - "handler_calibration.py"
Cohesion: 0.29
Nodes (3): Queue, segmentation_models_pytorch, statistics

### Community 128 - "test_crop.py"
Cohesion: 0.38
Nodes (6): center_to_box(), crop_image(), main(), ndarray, Crop ảnh theo tọa độ góc trên bên trái. Args: image: Ảnh đầu vào. x: Tọa độ X.…, Chuyển tọa độ tâm thành hai góc. Args: x: Tọa độ tâm X. y: Tọa độ tâm Y. width:…

### Community 129 - ".send_log_html"
Cohesion: 0.33
Nodes (3): Hàm này xử lý khi nhả stop, Gửi log điều khiển; log queue UI được quản lý bên ngoài controller., Hàm này xử lý khi có người nhấn nút Start

### Community 131 - "test_run_train_worker_patchcore.py"
Cohesion: 0.40
Nodes (5): main(), Runtime test cho TrainWorkerPatchCore., Chạy worker thật, nhận ảnh qua queue và trả kết quả qua queue. Returns: None:…, Chạy runtime test độc lập không cần pytest.a Returns: None: In thông báo PASS…, test_run_train_worker_patchcore_runtime()

### Community 132 - ".detect_anomaly_objects"
Cohesion: 0.50
Nodes (3): ndarray, Trả về score PatchCore, heatmap và danh sách đối tượng YOLO trên vùng bất…, Tìm vùng bất thường bằng PatchCore và infer YOLO trên từng vùng đó. Input:…

### Community 133 - "add_product"
Cohesion: 0.40
Nodes (4): add_product(), post, ndarray, UploadFile

### Community 135 - "config_software.js"
Cohesion: 0.50
Nodes (3): btn_close_settings, btn_config_software, overlay_config_software

### Community 136 - "move_to_selected_point"
Cohesion: 0.67
Nodes (4): move_to_selected_point(), write_log_calibration_append(), write_log_calibration_clear(), writeValidationErrors()

## Knowledge Gaps
- **174 isolated node(s):** `AppContext`, `MockDeploymentUnet`, `btn_border_film`, `btn_check_air_bubbles`, `btn_check_arm_cover` (+169 more)
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1177 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **42 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ModelPatchCore` connect `ModelPatchCore` to `BaseAI`, `pathlib`, `config/__init__.py`, `FrameModelPatchCore`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `ServiceContainer` connect `ServiceContainer` to `StagePreprocess`, `.__init__`, `StageTransform`, `RuntimeState`, `add_product`, `api_product.py`, `container.py`, `IAIControl`, `api_captureproduct.py`, `Pipeline`, `api_com.py`, `api_dimesional_calibration.py`, `CalibSearchCoordinator`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `Camera` connect `Camera` to `.__init__`, `ComService`, `config/__init__.py`, `model/__init__.py`, `HandlerCalibration`, `container.py`, `handler_calibration.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 59 inferred relationships involving `ServiceContainer` (e.g. with `RuntimeState` and `CalibSearchCoordinator`) actually correct?**
  _`ServiceContainer` has 59 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AppContext`, `MockDeploymentUnet`, `btn_border_film` to the rest of the system?**
  _174 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `.Ok` be split into smaller, more focused modules?**
  _Cohesion score 0.04495504495504495 - nodes in this community are weakly interconnected._
- **Should `.__init__` be split into smaller, more focused modules?**
  _Cohesion score 0.0436036036036036 - nodes in this community are weakly interconnected._