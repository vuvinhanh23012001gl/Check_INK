# Graph Report - app  (2026-09-28)

## Corpus Check
- 273 files · ~10,486,853 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 48 file(s) not represented in the graph (top: .pt 15, .css 11, .pth 6)

## Summary
- 3203 nodes · 7100 edges · 162 communities (125 shown, 37 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 424 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9b0e6303`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Result
- cv2
- common_value_tool.js
- measure_weld_width_tool.js
- Worker
- Camera
- capture_frame.js
- get_instruct_fix_erro
- .Fail
- repository/__init__.py
- WeldMeamunetUnetService
- create_obj_cross_item
- border_film_tool.js
- summary_tool.js
- FrameModelPatchCore
- ComService
- home.js
- JudmentLawProductRepository
- Judment
- foreign_object_tool.js
- TrainWorkerPatchCore
- IAIControl
- slit_tool.js
- IAIService
- WeldSeamAirBubbles
- Calibration
- StageTransform
- cnd_lybrary.js
- dimetional_calibration.js
- ItemsInspector
- ArmSensorDetector
- CalibSearchCoordinator
- PointRepository
- SerialConnect
- ProductService
- end_chipping_tool.js
- RuntimeState
- StagePreprocess
- numpy
- test_serial_manager.py
- .save_record
- test_judment_config_item_1_0_4.py
- Config_SoftWare
- test_logic_semi_permeable_membrane.py
- JudmentLawProductSevice
- ServiceContainer
- .get_objects
- validate/__init__.py
- .extract_membrane_polygons
- ManagerSerial
- CalibrationService
- test_logic_measurement_welding_detector.py
- ._extract_features
- items_inspector.js
- MeasurementItemsInspector
- .predict
- CanvasManager
- ModelHandler
- Folder
- BorderFilmInspector
- SlitItemInspector
- TrainlerPatchCore
- Infor_Software
- test_find_runtime_session_preserves_existing_session
- PatchCoreInspectionService
- add_new_product.js
- DimesionalCalibrationCanvas
- EndChippingInspector
- ProductRepository
- PermeableMembraneInspector
- ScratchedPipeItemInspector
- controler.js
- .__init__
- BorderDetector
- HandlerCalibration
- FrameHandlersCalibration
- test_choose_products.py
- ArmCoverItemInspector
- ArmSensorItemInspector
- HoleItemInspector
- ArmCoverDetector
- Manager_Log
- MeasurementWeldingDetector
- config/__init__.py
- Logic
- Log_Txt
- HandlerWorkDetect
- RectangleDrawer
- config_com.js
- Pipeline
- update_com_config
- config_software.js
- .fuc_update_input_queue_request_arm
- FrameHandlers
- .update_operator_values
- AirBubblesItemInspector
- test_logic_hole.py
- openRectangleEditor
- SlitDetector
- SerialConfig
- .wait_for_specific_data
- .send_command_stm32
- test_logic_slit_detector.py
- test_logic_border_detector.py
- BaseConfig
- .error
- BaseAI
- Point
- apply_camera_config
- Tong hop du an Python Detect Width Line
- model/__init__.py
- SemiPermeableMembrane
- main.py
- test_train_worker_patchcore.py
- 5. API va giao dien
- .read_json_from_file
- SocketModel
- get_hardware_status
- ComRepository
- .define
- CroppedImageFolder
- test_product_service.py
- Quy chế Ứng dụng Graphify & Đọc Sửa Mã Nguồn Trọng Tâm
- createCalibrationTable
- .Ok
- api_captureproduct.py
- Product
- test_crop.py
- .send_log_html
- Change_Disk
- train_worker.py
- PatchCoreImageDataset
- create_items_img
- .predict
- .__init__
- .stop
- shutdown_system
- Senior Python & Computer Vision Web Engineer
- Workflow: graphify
- app_services_product_product
- logic/__init__.py
- runtime/__init__.py
- run.py
- .define
- .worker_judget
- JudgmentResult
- ProductCountRepository
- get_instruct_staff_ee
- PatchCoreTrainRecordRepository
- camera_status
- .start_thread_handl_request_stm32
- get_instruct_worker
- VideoManager
- software_information
- move_to_selected_point

## God Nodes (most connected - your core abstractions)
1. `ServiceContainer` - 96 edges
2. `IAIControl` - 58 edges
3. `JudgmentResult` - 57 edges
4. `create_obj_cross_item()` - 57 edges
5. `FrameModelYoloObject` - 47 edges
6. `Result` - 46 edges
7. `ItemsInspector` - 45 edges
8. `get_obj_product()` - 45 edges
9. `Camera` - 41 edges
10. `BaseJudgerAI` - 40 edges

## Surprising Connections (you probably didn't know these)
- `14.1. Camera configuration` --references--> `CameraConfig`  [INFERRED]
  SOURCE_CODE_SUMMARY.md → app/config/camera_config.py
- `3. Quy trình TRONG KHI SỬA (In-Edit Workflow)` --references--> `ServiceContainer`  [INFERRED]
  .agents/rules/graphify.md → app/container.py
- `13. Ket luan` --references--> `ServiceContainer`  [INFERRED]
  SOURCE_CODE_SUMMARY.md → app/container.py
- `4.10. `app/core/` va `app/validate/`` --references--> `ServiceContainer`  [INFERRED]
  SOURCE_CODE_SUMMARY.md → app/container.py
- `Law regulation / judgment` --references--> `Result`  [INFERRED]
  SOURCE_CODE_SUMMARY.md → app/core/result.py

## Import Cycles
- None detected.

## Communities (162 total, 37 thin omitted)

### Community 0 - "Result"
Cohesion: 0.06
Nodes (26): Result, PointService, ndarray, Chức năng: Lấy danh sách gốc dạng đối tượng Point của Product để xử lý trực…, Chức năng: Lấy đường dẫn tuyệt đối của ảnh gốc của một Point. Input: product_id…, Chức năng: Lấy danh sách thông tin cấu trúc điểm của sản phẩm dưới dạng…, Chức năng: Lấy bản đồ các điểm thuộc về một Frame cụ thể của sản phẩm. Input:…, Chức năng: Lấy thông tin chi tiết của một điểm cụ thể dựa trên ID. Input:… (+18 more)

### Community 1 - "cv2"
Cohesion: 0.04
Nodes (61): UnetCofigAutoDetectLineMaster, UnetConfig, ModelPatchCore, Giải phóng hoàn toàn các tài nguyên nặng của mô hình, dọn dẹp RAM của FAISS…, Lớp thực hiện khởi tạo, dự đoán bất thường và trích xuất vùng lỗi (Bounding…, Khởi tạo bộ chuyển đổi dữ liệu, nạp cơ sở dữ liệu vector FAISS (Index) và trích…, ModelUnet, Vẽ đa giác xấp xỉ lên ảnh gốc. Args: image (np.ndarray): Ảnh gốc (BGR) cần vẽ… (+53 more)

### Community 2 - "common_value_tool.js"
Cohesion: 0.07
Nodes (53): canvasManager, HEIGH_IMG_SHAPE, scroll_container, video_product, videoManager, WIDTH_IMG_SHAPE, clearButton, closeButton (+45 more)

### Community 3 - "measure_weld_width_tool.js"
Cohesion: 0.08
Nodes (22): Measurement, obj_measure_weld_width_canvas, panner_measure_weld_width, bntJudment, boxContentMeasureWeldWidth, btnAutoRule, btnClearFrameMeasureWeldWidth, btnExitMeasureWeldWidth (+14 more)

### Community 4 - "Worker"
Cohesion: 0.16
Nodes (5): Khởi tạo tọa độ viên và cấu hình các dịch vụ liên quan. Args:…, Any, Queue, QueueManager, Worker

### Community 5 - "Camera"
Cohesion: 0.06
Nodes (17): Đọc các giá trị camera từ file GenApi ``features.cfg``. Input: đường dẫn file…, Camera, Ghi giá trị float vào node camera. Input: tên node và giá trị số. Output: không…, Đọc giá trị float từ node camera. Input: tên node cần đọc. Output: giá trị…, Đọc symbolic value của node enumeration camera. Input: tên node enumeration.…, Đồng bộ cấu hình runtime từ nodemap đã nạp từ features.cfg. Input: nodemap…, Áp dụng cấu hình hiện tại vào các node camera. Input: không có, sử dụng…, Lấy cấu hình camera hiện tại. Input: không có. Output: dictionary JSON-… (+9 more)

### Community 6 - "capture_frame.js"
Cohesion: 0.06
Nodes (57): balanceAuto, balanceInputs, cameraConfigButton, cameraConfigFields, cameraConfigLog, cameraConfigPanel, openCameraConfigPanel(), renderCameraConfig() (+49 more)

### Community 7 - "get_instruct_fix_erro"
Cohesion: 0.50
Nodes (4): get_instruct_fix_erro(), FileResponse, get, Trả về file PDF tài liệu hướng dẫn đối ứng và xử lý lỗi hệ thống để xem trực…

### Community 8 - ".Fail"
Cohesion: 0.08
Nodes (45): auto_create_line(), create_end_chipping_model(), create_foreign_object_model(), delete_end_chipping_model(), delete_end_chipping_runtime_image(), delete_foreign_object_model(), delete_foreign_object_runtime_image(), end_chipping_runtime_images() (+37 more)

### Community 9 - "repository/__init__.py"
Cohesion: 0.35
Nodes (4): ErrorCode, Enum, copy, statistics

### Community 10 - "WeldMeamunetUnetService"
Cohesion: 0.05
Nodes (26): Vẽ danh sách các đoạn thẳng đo đạc (đã hoặc chưa kéo dài) lên bề mặt ảnh. Args:…, Vẽ các điểm lấy mẫu từ biên đa giác (polygon) lên bề mặt ảnh dưới dạng hình…, Kéo dài tuyến tính các đoạn thẳng hiện tại về cả hai đầu dựa theo hướng vector…, Tìm giao điểm giữa hai đoạn thẳng p1p2 và q1q2 bằng giải thuật nhân chéo…, Sinh các đoạn thẳng đo chiều rộng bằng cách bắn tia pháp tuyến từ biên hướng về…, Dự đoán mask phân đoạn từ ảnh đầu vào và trích xuất ra danh sách các đa giác…, Lấy mẫu các điểm phân bố cách đều nhau theo một khoảng nhất định dọc trên các…, Vẽ danh sách các điểm bất kỳ (ví dụ: điểm trung tâm skeleton) lên bề mặt ảnh.… (+18 more)

### Community 11 - "create_obj_cross_item"
Cohesion: 0.10
Nodes (44): btn_exit_arm_cover, btn_judment_arm_sensor, createMeasureShapeTable(), event_transition_items(), func_callback_click_mouse_right_into_line(), func_callback_click_on_line_have_aready(), func_callback_click_on_rect(), log_arm_cover (+36 more)

### Community 12 - "border_film_tool.js"
Cohesion: 0.11
Nodes (13): FilmBorder, Line, btn_erase_border_film, btn_exit_border_film, btn_judment_border_film, createMeasureBorderFilmTable(), func_callback_click_on_line_drawn(), func_callback_click_on_line_have_aready() (+5 more)

### Community 13 - "summary_tool.js"
Cohesion: 0.07
Nodes (33): openOptionPanel(), getNameEventActivate(), set_obj_product(), btn_border_film, btn_check_air_bubbles, btn_check_arm_cover, btn_check_arm_sensor, btn_check_end_chipping (+25 more)

### Community 14 - "FrameModelPatchCore"
Cohesion: 0.10
Nodes (25): FramePatchCoreObjectDetector, Khởi tạo detector. Input: patch_core_frame: instance ``FrameModelPatchCore`` đã…, Chạy PatchCore để tìm vùng bất thường, rồi infer bằng YOLO Object trên từng…, FrameModelPatchCore, Khởi tạo frame processor. Input: ``model`` là instance ``ModelPatchCore`` đã…, Chạy PatchCore trên một ROI và quy đổi kết quả về ảnh gốc. ``ModelPatchCore``…, build_patchcore_model(), build_yolo_model() (+17 more)

### Community 15 - "ComService"
Cohesion: 0.14
Nodes (8): ComService, Hàm này chờ tín hiệu cụ thể từ manager_serial.Chờ thời gian timeout giây.Sau…, Lấy cấu hình COM hiện tại và danh sách cổng serial trên máy. Input: không có.…, Đổi cổng COM, lưu cấu hình và yêu cầu ManagerSerial kết nối lại. Input:…, Gửi dữ liệu và chờ ARM xác nhận. Returns: True : nhận đúng phản hồi False :…, Kiểm tra dữ liệu có đúng định dạng không và chuyển đổi về định dạng chuẩn. Ví…, 15.2. COM, Calibration

### Community 16 - "home.js"
Cohesion: 0.07
Nodes (41): get_com_connection(), set_camera_connection(), set_com_connection(), SocketData, btn_left, btn_reset_count_total, btn_right, circle_status_connect_camera (+33 more)

### Community 17 - "JudmentLawProductRepository"
Cohesion: 0.07
Nodes (18): JudmentLawProductRepository, Khởi tạo repository, tạo file nếu chưa có và nạp dữ liệu., Lấy danh sách Product ID. Returns: list[str]: Danh sách Product ID., Lấy danh sách Frame ID. Args: product_id: ID sản phẩm. Returns: list[str]: Danh…, Lấy danh sách Item ID. Args: product_id: ID sản phẩm. frame_id: ID Frame.…, Nạp dữ liệu từ dict. Args: raw: Dữ liệu nguồn. merge: True để gộp, False để ghi…, Gộp đệ quy hai dict. Args: target: Dữ liệu đích. source: Dữ liệu nguồn.…, Tạo file JSON rỗng nếu chưa tồn tại. (+10 more)

### Community 18 - "Judment"
Cohesion: 0.11
Nodes (23): InspectorTask, Judment, Any, ndarray, Path, Cấu hình một inspector trong một lần kiểm tra ảnh. Input: inspector: Instance…, Chuyển object config thành danh sách task có thể thực thi. Input: config:…, Alias dễ đọc hơn cho ``run``. Input: Giống ``run``. Output: Dictionary kết quả… (+15 more)

### Community 19 - "foreign_object_tool.js"
Cohesion: 0.10
Nodes (35): boxContentForeignObject, obj_region_foreign_object_canvas, panner_region_foreign_object, write_log_append(), activateForeignObjectPanel(), btnCreateModel, btnDeleteModel, btnDetectObject (+27 more)

### Community 20 - "TrainWorkerPatchCore"
Cohesion: 0.13
Nodes (10): Khởi tạo facade với PointService và worker train. Args: point_service: Service…, Any, Đưa một ảnh vào queue train. Args: image: PIL.Image, NumPy array hoặc bytes…, Lấy kết quả train hoặc lỗi từ result_queue. Args: timeout: Thời gian tối đa chờ…, Chạy một request train trên thread nền. Returns: None., Lấy đủ ảnh từ queue hoặc dừng nếu worker nhận tín hiệu stop. Args: image_count:…, Nhận ảnh qua queue và train PatchCore trên thread nền. Worker không chặn luồng…, Khởi tạo worker chỉ chứa quy tắc xử lý queue. Args: record_manager: Repository… (+2 more)

### Community 21 - "IAIControl"
Cohesion: 0.10
Nodes (7): IAIControl, Gửi lệnh Ready vào RX moniter để sẵn sàng chạy, Hàm này để xử lý logic mflow với biến input thread-safe, Hàm này xử lý khi đợi Auto, Hàm này xừ lý khi người dùng vào chế độ Auto, Hàm này xử lý đèn khi lần đầu chạy, Hàm này nhấp nháy led vì chạm cảm biến an toàn

### Community 22 - "slit_tool.js"
Cohesion: 0.09
Nodes (14): LineDrawer, ModelSlit, boxContentMeasureSlitWidth, obj_measure_slit_width_canvas, panner_measure_slit_width, btn_clear_slit, btn_exit_slit, btn_judment_slit (+6 more)

### Community 23 - "IAIService"
Cohesion: 0.13
Nodes (4): IAIConfig, Khởi tạo bộ điều khiển IAI dùng ManagerSerial bên ngoài. Input:…, IAIService, main()

### Community 24 - "WeldSeamAirBubbles"
Cohesion: 0.10
Nodes (23): ndarray, Chuyển box dạng (x, y, width, height) sang (x1, y1, x2, y2). Input: box gồm bốn…, Chuẩn hóa danh sách vùng về dạng ``(x, y, width, height)``. Input: Danh sách…, Quét bọt khí độc lập trên từng vùng cấm đã cấu hình. Args: img (np.ndarray):…, So sánh luật cấm bọt khí với kết quả quét runtime. Input: ``standard_data``…, Phán định bọt khí: có bọt khí là NG, không có là OK. Input: dict kết quả từ…, WeldSeamAirBubbles, create_detector() (+15 more)

### Community 25 - "Calibration"
Cohesion: 0.11
Nodes (4): Calibration, setter, Cập nhật các tham số cấu hình bằng cách truyền tham số đặt tên trực tiếp., Cập nhật các tham số kết quả đo (Result) bằng cách truyền tham số đặt tên trực…

### Community 26 - "StageTransform"
Cohesion: 0.09
Nodes (20): 1. Nguyên tắc kiến trúc cốt lõi, 3. Quy chuẩn Hiển thị Tiến trình Runtime (Runtime Transparency), 4. Tiêu chuẩn phán định OK/NG đo độ rộng đường hàn (`StageTransform`), Quy chuẩn Dự án Python Detect Width Line, Any, Path, Dừng stage nếu người dùng yêu cầu stop hoặc IAI đang ở lỗi., Xử lý một point và trả về payload JSON hóa được. Input: Dữ liệu sản phẩm đã… (+12 more)

### Community 27 - "cnd_lybrary.js"
Cohesion: 0.15
Nodes (21): a(), i(), At(), c(), e(), Et(), f(), ft() (+13 more)

### Community 28 - "dimetional_calibration.js"
Cohesion: 0.07
Nodes (21): btn_calcular_calibration, calibration_loading, calibration_loading_bar, calibration_loading_percent, calibration_loading_status, cancel_calibration_button, config_calibration, coordinate_items_now (+13 more)

### Community 29 - "ItemsInspector"
Cohesion: 0.06
Nodes (3): Frame, Product, ItemsInspector

### Community 30 - "ArmSensorDetector"
Cohesion: 0.12
Nodes (19): ArmSensorDetector, ndarray, Định nghĩa, đánh giá trạng thái và trả về ảnh trực quan của linh kiện Arm…, So sánh yêu cầu tồn tại Arm Sensor với output của ``define``. Input:…, Phán định Arm Sensor và trả về đầy đủ dữ liệu OK/NG. Input: dict kết quả từ…, create_detector(), main(), Kiểm tra compare từ chối chuẩn hoặc runtime sai cấu trúc. (+11 more)

### Community 31 - "CalibSearchCoordinator"
Cohesion: 0.09
Nodes (17): CalibSearchCoordinator, Any, setter, Thread-safe setter cập nhật số lượng ảnh đã xử lý hoàn thành. Args: value…, Khởi chạy thuật toán tìm kiếm calib trong một luồng riêng biệt (Non-blocking)., Vòng lặp chính xử lý thuật toán Calibration: Kiểm tra kết nối, điều khiển ARM…, Lớp phối hợp tính toán hệ số calibration cho frame ID trước khi sử dụng. Bắt…, Tạo luồng mới nhưng luồng này sẽ chịu sự kiểm soát số lượng của Semaphore. (+9 more)

### Community 32 - "PointRepository"
Cohesion: 0.13
Nodes (10): CalibrationReponsitory, Chức năng: Đọc toàn bộ dữ liệu cấu hình từ file JSON. Input: None Output: dict…, Chức năng: Ghi đè cấu trúc dữ liệu dictionary hiện tại xuống file cấu hình…, Khởi tạo Repository quản lý file dữ liệu cấu hình các điểm (Points). Nếu file…, PointRepository, test_calibration_service(), Cho phép lưu các point có inspector mà không yêu cầu mọi point. Input: Cây đủ…, test_partial_judgment_tree_is_valid() (+2 more)

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
Cohesion: 0.07
Nodes (17): Enum, Lưu trạng thái dùng chung giữa pipeline và các service. Input: không có.…, Cập nhật trạng thái tổng thể của pipeline., Đọc trạng thái tổng thể hiện tại của pipeline., Cập nhật trạng thái kết nối COM và camera., Trả về ``(com_connected, camera_connected)``., Cập nhật cờ sản phẩm đang được phán định., Các trạng thái tổng quát của pipeline runtime. (+9 more)

### Community 37 - "StagePreprocess"
Cohesion: 0.16
Nodes (9): PreparedProduct, Sắp xếp ID số trước ID chữ., Lấy scale calibration đầu tiên hợp lệ, mặc định 1.0., Dữ liệu đã chuẩn hóa để Stage 2 xử lý tuần tự., Đọc và chuẩn hóa dữ liệu sản phẩm trước khi điều khiển IAI., Nạp points, judgment law, calibration và chuyển sang Stage 2. Input: dữ liệu…, Đọc một file JSON object. Input: ``path`` là đường dẫn file JSON. Output:…, Ghép bốn nguồn JSON thành danh sách frame/point có judgment config. (+1 more)

### Community 38 - "numpy"
Cohesion: 0.09
Nodes (28): Cấu hình cho mô hình YOLO Segment., YoloDetectObjectConfig, FrameModelYoloObject, ModelYoloObject, Release model from memory., Khởi tạo StructureFrameYoloService. Args: frame_model (FrameModelYoloObject):…, StructureFrameYoloService, Khởi tạo StructureFrameYoloService. Args: frame_model (FrameModelYoloObject):… (+20 more)

### Community 39 - "test_serial_manager.py"
Cohesion: 0.12
Nodes (3): Queue, Tạo queue riêng cho một consumer nhận bản tin Serial. Input: không có. Output:…, serial_tools_list_ports

### Community 40 - ".save_record"
Cohesion: 0.11
Nodes (13): Any, Path, Ghi danh sách record vào file manifest. Args: items: Danh sách metadata cần…, Kiểm tra record có cùng ROI với phiên train hiện tại không., Chuyển object config sang dict JSON-safe. Args: config: Object config dataclass…, Lưu metadata của phiên train vào manifest. Args: config: Cấu hình train.…, Lấy record mới nhất trong manifest. Returns: dict | None: Record đầu tiên hoặc…, Khởi tạo service với manifest trung tâm. Args: root_dir: Folder tùy chọn dùng… (+5 more)

### Community 41 - "test_judment_config_item_1_0_4.py"
Cohesion: 0.19
Nodes (11): create_recording_inspector(), judge(), load_item_config(), main(), Kiểm tra Judment điều phối đúng config item 1/0/4 trên một ảnh. Input:…, Tạo detector giả có tên đúng với key trong cấu hình. Input: Tên inspector cần…, Đọc cấu hình judgment của product 1, frame 0, item 4. Input: Không có. Output:…, Kiểm tra ảnh runtime có khung ROI xanh và nhãn lỗ thủng rõ ràng. Input: Ảnh đen… (+3 more)

### Community 42 - "Config_SoftWare"
Cohesion: 0.09
Nodes (3): Config_SoftWare, Quản lý cấu hình phần mềm & đường dẫn log, Thay đổi đường dẫn log theo tên sản phẩm. - name_product phải là chuỗi và độ…

### Community 43 - "test_logic_semi_permeable_membrane.py"
Cohesion: 0.22
Nodes (16): create_detector(), main(), Luật cố định phải từ chối standard_data khác True., Chạy test logic SemiPermeableMembrane và báo kết quả console. Input: Không có.…, Tạo detector với kết quả segmentation giả. Input: ``border_segments`` và…, Tạo một segment polygon tối thiểu cho test., Inner nằm hoàn toàn trong border phải trả về OK., Inner đè lên border phải trả về NG. (+8 more)

### Community 44 - "JudmentLawProductSevice"
Cohesion: 0.15
Nodes (8): JudmentLawProductSevice, Tên tương thích cũ của ``convert_canvas_coordinates``. Input, output và lỗi:…, Xác định inspector chứa nhiều line/rectangle con. Input: Dict cấu hình của một…, Lấy toàn bộ dữ liệu của một Product dựa trên product_id. Args: product_id: ID…, Lấy dữ liệu của một Frame cụ thể thuộc Product. Args: product_id: ID sản phẩm.…, Lấy chi tiết dữ liệu của một Item cụ thể từ Product và Frame. Args: product_id:…, Kiểm tra payload judgment là một phần hợp lệ của cây point/frame. Args: data:…, Chuyển tọa độ mọi inspector từ canvas sang pixel ảnh master. Input: ``data`` là…

### Community 45 - "ServiceContainer"
Cohesion: 0.09
Nodes (29): Dừng toàn bộ dịch vụ, giải phóng cổng COM, đóng Camera, ngắt luồng và giải…, Gửi log pipeline tới ô log phán định trên giao diện. Input: ``message`` là nội…, ServiceContainer, calculator(), capture(), post, camera_ws(), websocket (+21 more)

### Community 46 - ".get_objects"
Cohesion: 0.05
Nodes (28): ndarray, Trả về score PatchCore, heatmap và danh sách đối tượng YOLO trên vùng bất…, Tìm vùng bất thường bằng PatchCore và infer YOLO trên từng vùng đó. Input:…, ndarray, Phát hiện vùng bất thường trong ROI và trả box theo ảnh gốc. Input: image: Ảnh…, Tính anomaly score và heatmap overlay trong một ROI. Input: Ảnh NumPy và tọa độ…, Dịch box từ hệ tọa độ ROI về hệ tọa độ ảnh gốc. Input: ``boxes`` dạng ``(x, y,…, Kiểm tra ảnh và ROI trước khi crop. Input: Ảnh NumPy và bốn tọa độ ROI. Output:… (+20 more)

### Community 47 - "validate/__init__.py"
Cohesion: 0.14
Nodes (12): calculater_calibration(), CalibrationDeleteData, DataIn, delete_calibration(), PointData, BaseModel, post, Xóa kết quả calibration đã lưu của một frame. (+4 more)

### Community 48 - ".extract_membrane_polygons"
Cohesion: 0.33
Nodes (4): ndarray, Trích xuất đa giác của màng bán thấm. Args: img: Ảnh gốc. x1, y1, x2, y2: Tọa…, Trích xuất polygon đầu tiên thuộc class xuất hiện đầu tiên trong danh sách…, Chuyển tọa độ từ Canvas sang ảnh gốc. Args: x_start, y_start, x_end, y_end: tọa…

### Community 49 - "ManagerSerial"
Cohesion: 0.18
Nodes (3): ManagerSerial, Dừng luồng kiểm tra COM, RX/TX và đóng cổng serial., 14.3. COM configuration

### Community 50 - "CalibrationService"
Cohesion: 0.09
Nodes (14): CalibrationService, Khởi tạo dịch vụ quản lý thông số Calibration cho từng Frame. :param…, Chức năng: Tạo mới hoàn toàn cấu hình Calibration cho một Frame từ một đối…, Chức năng: Xóa bỏ thông số cấu hình Calibration của Frame và dọn dẹp node cha…, Chức năng: Kiểm tra xem thông số cấu hình Calibration của một Frame có tồn tại…, Chức năng: Kiểm tra xem thông số cấu hình Calibration của một Frame có hợp lệ…, Chức năng: Kiểm tra xem cặp product_id và frame_id có tồn tại trong hệ thống…, Chức năng: Xóa bỏ thông số cấu hình Calibration của một Frame dựa vào… (+6 more)

### Community 51 - "test_logic_measurement_welding_detector.py"
Cohesion: 0.13
Nodes (22): create_detector(), create_runtime(), main(), Kiểm tra Measurement không kéo dài line ngoài tọa độ cấu hình. Input: Ba đoạn…, Kiểm tra tọa độ chuẩn được dùng làm line đo trên polygon runtime. Input: Cấu…, Chỉ chạy UNet một lần khi hai detector cùng model đo cùng ảnh. Input: Cấu hình…, Lưu crop từng ROI và full-frame thực nhận của inspector đo line. Input: Ảnh giả…, Xác nhận ảnh train được ghi trước khi model UNet nhận ảnh. Input: Một item… (+14 more)

### Community 52 - "._extract_features"
Cohesion: 0.12
Nodes (12): ndarray, Chạy thử nghiệm mô hình (Warmup) với một ảnh đen (dummy image) giúp khởi tạo…, Dự đoán và trích xuất trực tiếp ảnh gốc được vẽ đè các khung bao quanh vùng bất…, Tính toán phân ngưỡng động bản đồ bất thường, lọc nhiễu hạt và trích xuất danh…, Gộp các box bất thường giao nhau hoặc nằm trong cùng một vùng. Args: boxes:…, Kiểm tra hai box có giao nhau với diện tích dương hay không., Trả box nhỏ nhất bao phủ toàn bộ hai box đầu vào., Thực hiện vẽ các hộp chữ nhật bao quanh vùng lỗi kèm nhãn nền màu tương ứng lên… (+4 more)

### Community 55 - ".predict"
Cohesion: 0.16
Nodes (9): Any, ndarray, Vẽ polygon của các segment lên ảnh. Args: image: Ảnh đầu vào. segments: Danh…, Thực hiện suy luận và vẽ kết quả lên ảnh. Args: image: Ảnh đầu vào. show_label:…, Hiển thị ảnh. Args: image: Ảnh cần hiển thị. window_name: Tên cửa sổ. Returns:…, Tiền xử lý ảnh. Args: image: Ảnh đầu vào. Returns: Any: Ảnh sau tiền xử lý., Thực hiện suy luận. Args: image: Ảnh đầu vào. Returns: Results: Kết quả suy…, Lấy danh sách kết quả segment. Args: image: Ảnh đầu vào. Returns: list[dict]:… (+1 more)

### Community 57 - "ModelHandler"
Cohesion: 0.21
Nodes (5): ModelHandler, Vẽ contours lên ảnh Parameters: image (np.ndarray): Ảnh gốc (BGR) contours…, Tìm contour ngoài cùng và lọc theo diện tích Parameters: mask (np.ndarray):…, Làm sạch mask bằng phép Morphology Opening (Erosion + Dilation) Parameters:…, Tìm contour ngoài cùng, lọc theo diện tích và xấp xỉ polygon Parameters: mask…

### Community 58 - "Folder"
Cohesion: 0.12
Nodes (9): Folder, Path, Tạo folder nếu chưa tồn tại và trả về đường dẫn tuyệt đối. :param folder_name:…, Tạo toàn bộ thư mục từ đường dẫn nếu chưa tồn tại :param path: đường dẫn đầy đủ…, Đảm bảo thư mục và file tồn tại; tự động tạo nếu chưa có và trả về đường dẫn…, Lấy đường dẫn thư mục cha và nối thêm tên mới dùng thư viện os., Tạo folder nếu chưa tồn tại và trả về đường dẫn tuyệt đối., Lấy đường dẫn thư mục cha của file GỌI hàm này và nối thêm tên mới. (+1 more)

### Community 61 - "TrainlerPatchCore"
Cohesion: 0.12
Nodes (15): Image, ndarray, Path, Trích xuất đặc trưng patch-level cho batch ảnh. Args: batch (torch.Tensor):…, Lấy danh sách thư mục ROI từ `data_root` sắp xếp theo tên. Returns: list[Path]:…, Chuẩn hóa tọa độ crop từ config thành ``(left, top, right, bottom)``. Returns:…, Huấn luyện một ROI và lưu index FAISS + memory bank tương ứng. Args: roi_path…, Thay thế session của ROI, chép ảnh đầu vào rồi train. Args: images: Danh sách… (+7 more)

### Community 63 - "test_find_runtime_session_preserves_existing_session"
Cohesion: 0.40
Nodes (5): main(), Path, Tìm đúng session có runtime/good và không chọn session the_first cũ. Returns:…, Chạy test độc lập không cần pytest., test_find_runtime_session_preserves_existing_session()

### Community 64 - "PatchCoreInspectionService"
Cohesion: 0.10
Nodes (17): PatchCoreInspectionService, Image, ndarray, Path, Resolve đúng session từ record mới nhất của Point., Tạo yêu cầu train PatchCore từ ảnh Point. Args: product_id: Mã sản phẩm.…, Chạy inference model PatchCore mới nhất của một Point. Args: product_id: Mã sản…, Lưu crop PatchCore trước inference mà không làm gián đoạn judgment. Input: Crop… (+9 more)

### Community 65 - "add_new_product.js"
Cohesion: 0.14
Nodes (15): add_product, btn_cancel_delete, btn_confirm_delete, close_add_product, createDataShowTable(), form_add_new_product, imageInput, overlay_accpet_delete_product (+7 more)

### Community 66 - "DimesionalCalibrationCanvas"
Cohesion: 0.15
Nodes (3): DimesionalCalibrationCanvas, create_line(), func_callback_click_right_mouse_on_line()

### Community 71 - "controler.js"
Cohesion: 0.12
Nodes (9): choose_product, close_choose_product, container, overlay_choose_product, btn_instruct_fix_erro, btn_instruct_staff_ee, btn_instruct_worker, btn_out_app (+1 more)

### Community 72 - ".__init__"
Cohesion: 0.08
Nodes (31): Cấu hình cho mô hình YOLO Segment., YoloSegmentConfig, FrameModelYoloSegment, ModelYoloSegment, Warmup mô hình. Args: None Returns: None, Giải phóng mô hình. Args: None Returns: None, YOLO Segment sử dụng Ultralytics., Khởi tạo mô hình. Args: config: Cấu hình mô hình. Returns: None (+23 more)

### Community 73 - "BorderDetector"
Cohesion: 0.11
Nodes (15): BorderDetector, Any, ndarray, Phán định Border Film theo giới hạn min/max của từng line. Input: dict output…, Khởi tạo BorderDetector với một thực thể của ModelUnet. Args: unet_model…, Vẽ polygon, line kiểm tra và giao điểm lên ảnh output. Input: Ảnh BGR, polygon…, Hiển thị ảnh kết quả BorderDetector bằng cửa sổ OpenCV. Input: ``image`` là ảnh…, Nhận vào ảnh gốc, tự động chạy qua ModelUnet để lấy polygon, sau đó tìm giao… (+7 more)

### Community 74 - "HandlerCalibration"
Cohesion: 0.19
Nodes (5): HandlerCalibration, Queue, setter, Hàm này dùng để tạo luồng xử lý phán định sản phẩm trong đa luồng., Nếu file JSON tồn tại → đọc và trả về data. Nếu chưa tồn tại → tạo folder +…

### Community 75 - "FrameHandlersCalibration"
Cohesion: 0.26
Nodes (4): FrameHandlersCalibration, points: list [(x,y), ...], Kiểm tra 2 đoạn thẳng p1-p2 và p3-p4 có cắt nhau không Nếu có trả về tọa độ…, Vẽ polygon lên ảnh Parameters: image (np.ndarray): Ảnh gốc (BGR) polygon…

### Community 76 - "test_choose_products.py"
Cohesion: 0.22
Nodes (6): ChooseProductRepository, ChooseProductService, print_result(), test_get_choose_product(), test_reset_choose_product(), test_set_choose_product_valid()

### Community 80 - "ArmCoverDetector"
Cohesion: 0.12
Nodes (19): ArmCoverDetector, ndarray, Định nghĩa và đánh giá trạng thái của linh kiện Cover Arm trong vùng chỉ định.…, So sánh yêu cầu tồn tại Cover Arm với output của ``define``. Input:…, Phán định Cover Arm và trả về đầy đủ dữ liệu OK/NG. Input: dict kết quả từ…, create_detector(), main(), Tạo detector với model giả trả về kết quả định trước. Input: ``search_result``… (+11 more)

### Community 81 - "Manager_Log"
Cohesion: 0.19
Nodes (5): Log_CSV, Log_Img, Manager_Log, Queue, Dừng luồng ghi log an toàn.

### Community 82 - "MeasurementWeldingDetector"
Cohesion: 0.17
Nodes (10): MeasurementWeldingDetector, Any, ndarray, Chuyển key line trong JSON thành số nguyên., Đọc và kiểm tra năm level tăng dần của một line chuẩn., Xếp khoảng cách vào level theo ngưỡng trên bao gồm. Input: ``distance_mm`` là…, Đo giao điểm chỉ trong phạm vi từng đoạn line cấu hình. Input: ảnh runtime,…, So sánh chiều rộng runtime với level chuẩn của từng line. Input:… (+2 more)

### Community 83 - "config/__init__.py"
Cohesion: 0.06
Nodes (30): TypeDataSendClient, CalibrationConfig, CameraConfig, Cấu hình runtime ánh xạ trực tiếp vào camera feature file. Input: dictionary…, ModeState, Enum, QueueConfig, EnumMode (+22 more)

### Community 84 - "Logic"
Cohesion: 0.12
Nodes (11): Logic, ndarray, Hàm này dùng để kiểm tra xem tất cả phần tử trong danh sách có phải là số…, Kiểm tra dữ liệu có đúng định dạng không và chuyển đổi về định dạng chuẩn. Ví…, Hàm này chờ tín hiệu cụ thể từ obj_manager_serial.Chờ thời gian timeout…, 15.1. Pipeline va startup, 15.3. Calibration va Draw Regulations, 15.4. Frontend va canvas (+3 more)

### Community 86 - "HandlerWorkDetect"
Cohesion: 0.15
Nodes (8): ProductAggregator, Trả về: None -> chưa đủ frame True/False -> đã đủ frame, trả về kết quả sản phẩm, HandlerWorkDetect, Queue, setter, Hàm này dùng để tạo luồng xử lý phán định sản phẩm trong đa luồng., ChooseProduct, ProductManager

### Community 88 - "config_com.js"
Cohesion: 0.16
Nodes (13): baudSelect, comButton, comClose, comEmptyState, comForm, comInfo, comOverlay, comPorts (+5 more)

### Community 89 - "Pipeline"
Cohesion: 0.09
Nodes (18): 2.1. Ngôn ngữ & Comment, 2.2. Type Hinting (Ép kiểu tham số và đầu ra), 2.3. Xử lý ngoại lệ (Exception Handling) & Bảo vệ luồng, 2.4. Phần cứng STM32 / IAI (Quy tắc bất khả xâm phạm), 2. Tiêu chuẩn viết code (Coding Standards), Pipeline, Chuyển sang Stage 1 sau tín hiệu Reset của IAI., Theo dõi cạnh nhấn Reset và khóa Reset trong lúc phán định. (+10 more)

### Community 90 - "update_com_config"
Cohesion: 0.25
Nodes (8): ComConnectionUpdate, open_panel_com(), BaseModel, post, Payload cấu hình cổng COM từ giao diện web., Tương thích endpoint cũ, trả dữ liệu để mở panel COM., Cập nhật cổng COM, lưu JSON và mở kết nối mới., update_com_config()

### Community 91 - "config_software.js"
Cohesion: 0.20
Nodes (9): btn_close_settings, btn_config_software, btn_exit_software_information, btn_software_information, overlay_config_software, renderInformationGroup(), showSoftwareInformation(), software_information_content (+1 more)

### Community 92 - ".fuc_update_input_queue_request_arm"
Cohesion: 0.18
Nodes (4): Cập nhật biến input với lock, thread-safe, Cập nhật trạng thái tất cả các biến từ chuỗi STM32, thread-safe data: chuỗi…, Cập nhật trạng thái nút và cảm biến từ RX queue của ManagerSerial., Đọc giá trị số của một bản tin input STM32. Input: chuỗi dạng ``btn_start:1``…

### Community 93 - "FrameHandlers"
Cohesion: 0.23
Nodes (5): FrameHandlers, points: list [(x,y), ...], Kiểm tra 2 đoạn thẳng p1-p2 và p3-p4 có cắt nhau không Nếu có trả về tọa độ…, p1, p2: (x, y) có thể là int hoặc float (subpixel) return: khoảng cách mm, Vẽ polygon lên ảnh Parameters: image (np.ndarray): Ảnh gốc (BGR) polygon…

### Community 94 - ".update_operator_values"
Cohesion: 0.29
Nodes (4): Any, Kiểm tra miền giá trị số cơ bản trước khi áp dụng camera. Input: không có.…, Chuyển cấu hình thành dictionary để trả về API hoặc ghi JSON. Input: không có.…, Cập nhật field vận hành, không cho operator sửa white balance. Input:…

### Community 96 - "test_logic_hole.py"
Cohesion: 0.23
Nodes (14): create_detector(), main(), Kiểm tra compare từ chối chuẩn hoặc runtime sai cấu trúc., Chạy các kiểm tra logic HoleDetector và báo kết quả console. Input: Không có.…, Tạo HoleDetector với kết quả search giả. Input: ``search_result`` là output giả…, Kiểm tra evaluate trả OK khi runtime có Hole., Kiểm tra evaluate trả NG khi yêu cầu Hole nhưng không phát hiện., Kiểm tra evaluate trả OK khi vùng được cấu hình không có Hole. (+6 more)

### Community 97 - "openRectangleEditor"
Cohesion: 0.43
Nodes (6): event_transition_items(), getInspector(), openRectangleEditor(), removeStoredRectangle(), selectStoredRectangle(), updateHighlight()

### Community 98 - "SlitDetector"
Cohesion: 0.16
Nodes (11): Any, Chuyển key line trong JSON thành số nguyên., Đọc và kiểm tra khoảng widthMin/widthMax của line chuẩn., So sánh độ rộng khe runtime với khoảng chuẩn từng line. Input:…, Đo độ rộng khe hàn và phán định theo khoảng min/max., Phán định toàn bộ line khe hàn thành OK hoặc NG. Input: dict output của…, SlitDetector, 20.2. Toa do canvas va anh output (+3 more)

### Community 99 - "SerialConfig"
Cohesion: 0.12
Nodes (10): ComConfig, Any, Tạo cấu hình web từ cấu hình serial đang được sử dụng. Input: instance…, Chuẩn hóa và xác thực giá trị nhận từ API. Input: tên cổng và baudrate bất kỳ…, Chuyển sang cấu hình mà lớp serial hiện tại sử dụng. Input: cấu hình COM đã hợp…, Kiểm tra cấu hình trước khi lưu hoặc mở cổng. Input: không có. Output: không…, Trả về dữ liệu cấu hình dùng cho API và log. Input: không có. Output:…, Cấu hình kết nối COM ở biên config của ứng dụng. Input: tên cổng COM và… (+2 more)

### Community 100 - ".wait_for_specific_data"
Cohesion: 0.18
Nodes (5): Kiểm tra IAI đã hoàn tất về gốc trước khi cho phép di chuyển. Input:…, Gửi tọa độ đến ARM và chờ phản hồi trên queue lệnh riêng. Input: ``x``, ``y``,…, Gửi lệnh đưa ARM về gốc và chờ xác nhận. Input: ``timeout`` là thời gian chờ…, Chờ tín hiệu cụ thể từ queue_check_in_1. - expected_signal: tín hiệu mong đợi…, So khớp phản hồi ARM, kể cả dạng tọa độ có padding và hậu tố ``ok``. Input:…

### Community 101 - ".send_command_stm32"
Cohesion: 0.20
Nodes (5): show trạng thái hiện tại của của các Input Output, Luồng này đọc trạng thái từ các nút nhấn.Xủ lý Input và cập nhật trạng thái gửi…, Gửi lệnh qua ManagerSerial được truyền từ bên ngoài. Input: ``data`` là chuỗi…, Gửi lệnh xuống STM32 khi trạng thái output thay đổi, Hàm này xử lý khi người dùng nhấn nút nhấn về gốc

### Community 102 - "test_logic_slit_detector.py"
Cohesion: 0.21
Nodes (16): create_detector(), create_runtime(), main(), Kiểm tra Judment dùng đúng tọa độ SlitWeldInspector để đo polygon., Kiểm tra line không cắt polygon luôn là NG., Kiểm tra widthMin lớn hơn hoặc bằng widthMax bị từ chối., Chạy toàn bộ test logic SlitDetector bằng Python thường., Tạo SlitDetector với polygon chữ nhật giả. Input: Không có. Output: Detector và… (+8 more)

### Community 103 - "test_logic_border_detector.py"
Cohesion: 0.23
Nodes (14): create_detector(), main(), Dữ liệu chuẩn thiếu widthMin/widthMax phải báo ValueError., Chạy test logic BorderDetector và báo kết quả console. Input: Không có. Output:…, Tạo BorderDetector với polygon hình chữ nhật giả., Một ảnh có nhiều line chỉ gọi UNet một lần và lấy giao điểm chính xác., Line có khoảng cách trong min/max phải cho kết quả OK., Line đo vượt widthMax phải cho kết quả NG. (+6 more)

### Community 105 - ".error"
Cohesion: 0.09
Nodes (23): ndarray, Định nghĩa, đánh giá trạng thái và trả về ảnh trực quan của Scratch The Pipe.…, Kiểm tra vùng ảnh không được xuất hiện Scratch. Input: ``standard_data`` phải…, Phán định Scratch: có object là NG, không có object là OK. Input: dict kết quả…, ScratchThePipeDetector, create_detector(), main(), Tạo ScratchThePipeDetector với model phủ định giả. Input: ``runtime_result`` là… (+15 more)

### Community 106 - "BaseAI"
Cohesion: 0.15
Nodes (7): BaseAI, ABC, gc, segmentation_models_pytorch, torch, ultralytics, ultralytics_engine_results

### Community 107 - "Point"
Cohesion: 0.21
Nodes (5): Point, Path, setter, 17. Tach output runtime khoi storage - 2026-08-28, 18.1. Tach output runtime

### Community 109 - "apply_camera_config"
Cohesion: 0.21
Nodes (12): apply_camera_config(), CameraConfigUpdate, _payload_values(), BaseModel, post, Khôi phục cấu hình từ file JSON và áp dụng lại vào camera., Payload cho các thông số camera operator được phép chỉnh., Lấy các giá trị khác None từ payload và báo lỗi nếu payload rỗng. Input:… (+4 more)

### Community 110 - "Tong hop du an Python Detect Width Line"
Cohesion: 0.09
Nodes (21): 11. Trang thai tong quat, 12. Thu tu nen doc khi tiep tuc phat trien, 13. Ket luan, 1. Muc dich du an, 2. Cach chay, 4.10. `app/core/` va `app/validate/`, 4.1. `app/main.py`, 4.5. `app/engines/` (+13 more)

### Community 111 - "model/__init__.py"
Cohesion: 0.21
Nodes (4): Line, MockDeploymentUnet, test_point_service(), uuid

### Community 112 - "SemiPermeableMembrane"
Cohesion: 0.12
Nodes (14): ndarray, Trích xuất polygon đầu tiên thuộc class xuất hiện đầu tiên trong danh sách…, Kiểm tra `polygon_inner` có nằm hoàn toàn trong `polygon_border` hay không.…, Vẽ các điểm giao (các điểm lỗi hình học) lên ảnh. Mỗi điểm được vẽ thành: - Một…, Vẽ hai polygon (border và inner) lên ảnh để trực quan hóa kết quả. Args: image…, Thực hiện suy luận segmentation cho hai lớp màng (border và inner), kiểm tra…, Hiển thị ảnh bằng OpenCV trong cửa sổ có thể resize. Chức năng: - Tạo window…, Kiểm tra luật inner phải nằm hoàn toàn trong border. Input: ``standard_data``… (+6 more)

### Community 113 - "main.py"
Cohesion: 0.27
Nodes (9): create_container(), create_app(), lifespan(), log_sender(), Task chạy nền để tiêu thụ dữ liệu từ queue và gửi qua Socket.io, contextlib, fastapi_staticfiles, socketio (+1 more)

### Community 114 - "test_train_worker_patchcore.py"
Cohesion: 0.22
Nodes (7): FakeTrainer, main(), Kiểm thử worker queue của PatchCore., Trainer giả để kiểm tra giao tiếp queue mà không chạy model thật., Worker chỉ train sau khi nhận đủ image_count ảnh. Returns: None: Kết thúc không…, Chạy test worker độc lập không cần pytest., test_train_worker_waits_for_required_images()

### Community 115 - "5. API va giao dien"
Cohesion: 0.22
Nodes (9): 5. API va giao dien, Camera, Capture product, COM va Socket.IO, Draw regulations, Home, Law regulation / judgment, Product va software (+1 more)

### Community 118 - "get_hardware_status"
Cohesion: 0.25
Nodes (8): get_hardware_status(), get_product_count(), home(), get, Request, Hiển thị màn hình chính cùng tên sản phẩm đang được chọn. Input: request…, Lấy số lượng sản phẩm OK, NG và Tổng đã lưu trong file JSON., Lấy trạng thái kết nối phần cứng thực tế cho Camera và cổng COM.

### Community 120 - ".define"
Cohesion: 0.27
Nodes (6): Any, ndarray, So sánh kết quả runtime với tiêu chuẩn kỹ thuật (không có dị vật). Args:…, Phán định trạng thái cuối cùng: Phát hiện dị vật -> NG, Không phát hiện -> OK.…, Vẽ các vùng bất thường PatchCore và bounding box của đối tượng YOLO lên ảnh.…, Thu thập dữ liệu dị vật từ FramePatchCoreObjectDetector và vẽ trực quan ảnh.…

### Community 121 - "CroppedImageFolder"
Cohesion: 0.20
Nodes (7): CroppedImageFolder, Path, Khởi tạo dataset ImageFolder có crop ảnh. Args: root: Thư mục dữ liệu theo cấu…, Đọc, crop và transform một ảnh theo chỉ số dataset. Args: index: Vị trí ảnh…, Khởi tạo dataset ảnh phẳng của PatchCore. Args: root: Folder chứa ảnh train…, ImageFolder crop ảnh trước khi áp dụng transform. Args: root: Thư mục dữ liệu…, ImageFolder

### Community 122 - "test_product_service.py"
Cohesion: 0.39
Nodes (7): print_result(), test_add_roi_image(), test_delete_product(), test_get_all_products(), test_get_arr_path_img_roi_product_by_id(), test_get_product(), test_update_product()

### Community 123 - "Quy chế Ứng dụng Graphify & Đọc Sửa Mã Nguồn Trọng Tâm"
Cohesion: 0.33
Nodes (5): 1. Nguyên tắc cốt lõi, 2. Quy trình TRƯỚC KHI SỬA (Pre-Edit Workflow), 3. Quy trình TRONG KHI SỬA (In-Edit Workflow), 4. Quy trình SAU KHI SỬA (Post-Edit Workflow), Quy chế Ứng dụng Graphify & Đọc Sửa Mã Nguồn Trọng Tâm

### Community 124 - "createCalibrationTable"
Cohesion: 0.20
Nodes (10): create_hight_light_items_for_frame(), createButton(), createCalibrationTable(), func_callback_check_line_exis(), func_callback_click_on_line_drawn(), get_data_create_calibrationTable_config(), high_light_item(), selection_data_input() (+2 more)

### Community 125 - ".Ok"
Cohesion: 0.12
Nodes (14): ndarray, Trích xuất đa giác đường biên từ ảnh bằng ModelUnet và trả về đối tượng Result.…, ndarray, Lấy danh sách đối tượng theo label trong vùng kiểm tra sau khi quy đổi tọa độ…, ndarray, Lấy danh sách đối tượng theo label trong vùng kiểm tra sau khi quy đổi tọa độ…, Phán định bọt khí trong nhiều vùng kiểm tra trên ảnh. Args: image: Ảnh master…, capture() (+6 more)

### Community 126 - "api_captureproduct.py"
Cohesion: 0.12
Nodes (24): TypeSend, get_services(), get_services_ws(), Request, WebSocket, exit(), init_data(), get (+16 more)

### Community 128 - "test_crop.py"
Cohesion: 0.38
Nodes (6): center_to_box(), crop_image(), main(), ndarray, Crop ảnh theo tọa độ góc trên bên trái. Args: image: Ảnh đầu vào. x: Tọa độ X.…, Chuyển tọa độ tâm thành hai góc. Args: x: Tọa độ tâm X. y: Tọa độ tâm Y. width:…

### Community 129 - ".send_log_html"
Cohesion: 0.33
Nodes (3): Hàm này xử lý khi nhả stop, Gửi log điều khiển; log queue UI được quản lý bên ngoài controller., Hàm này xử lý khi có người nhấn nút Start

### Community 130 - "Change_Disk"
Cohesion: 0.29
Nodes (3): Change_Disk, Hàm trả về list rỗng nếu không, Kiểm tra ổ này có đang được chọn trả về 0 nếu tồn tại nhưng chưa được chọn trả…

### Community 131 - "train_worker.py"
Cohesion: 0.28
Nodes (6): PatchCoreTrainRequest, Path, Queue, Worker chạy train PatchCore trên thread riêng., Thông tin một yêu cầu train đang chờ xử lý., Bắt đầu một phiên train trên thread nền. Args: model_root: Folder gốc lưu ảnh…

### Community 132 - "PatchCoreImageDataset"
Cohesion: 0.22
Nodes (7): PatchCoreImageDataset, Trả về số lượng ảnh train hợp lệ. Returns: int: Số file ảnh được dataset thu…, Đọc, crop tùy chọn và transform một ảnh train. Args: index: Vị trí ảnh trong…, Dataset đọc ảnh trực tiếp trong folder PatchCore. Args: root: Folder chứa ảnh…, main(), Entry point CLI; nhận đường dẫn ảnh sau cờ ``--images``., Dataset

### Community 133 - "create_items_img"
Cohesion: 0.25
Nodes (9): create_box(), create_calibration_table_show(), create_img_items_dimesion_calibration(), create_items_img(), extractResultParameters(), loadPointCoordinates(), render_selected_calibration_result(), renderResultTableDiv() (+1 more)

### Community 134 - ".predict"
Cohesion: 0.38
Nodes (4): ndarray, Preprocess input image. Args: image: Input image. Returns: Preprocessed image., Run object detection. Args: image: Input image. Returns: YOLO prediction result., Lấy danh sách kết quả detect và kiểm tra chạm biên trục X, Y. Args: image: Ảnh…

### Community 139 - ".stop"
Cohesion: 0.25
Nodes (5): Hàm này dùng để dừng luồng này dùng để khi giải phóng phần mềm, Hàm này dùng để dừng luồng này dùng để khi giải phóng phần mềm, Dừng luồng đọc dữ liệu đầu vào từ các nút nhấn vật lý của STM32., Dừng luồng chính xử lý logic và gửi dữ liệu Output tới STM32., Dừng toàn bộ các luồng hoạt động của bộ điều khiển STM32/IAI.

### Community 141 - "shutdown_system"
Cohesion: 0.29
Nodes (7): _delayed_exit(), post, Request, Chờ một khoảng thời gian ngắn để server trả về response cho client trước khi…, Dừng toàn bộ hệ thống, ngắt các luồng, đóng Camera, COM và giải phóng bộ nhớ.…, shutdown_system(), JSONResponse

### Community 142 - "Senior Python & Computer Vision Web Engineer"
Cohesion: 0.50
Nodes (3): 1. Năng lực cốt lõi, 2. Nguyên tắc giao tiếp & Thực thi, Senior Python & Computer Vision Web Engineer

### Community 143 - "Workflow: graphify"
Cohesion: 0.40
Nodes (4): 1. Khởi tạo toàn diện (Full Build), 2. Tra cứu & Phân tích tác động (Impact Analysis), 3. Cập nhật gia tăng sau khi code (Incremental Update), Workflow: graphify

### Community 155 - "JudgmentResult"
Cohesion: 0.11
Nodes (26): ClassNameModelSurfaceConfig, ClassNameObjectStructureDetectConfig, BaseJudgerAI, JudgmentResult, ABC, Any, Chuyển kết quả phán định sang dictionary dùng cho API hoặc log., Hợp đồng chung cho các lớp AI phán định trong structure. Mỗi lớp con bắt buộc… (+18 more)

### Community 156 - "ProductCountRepository"
Cohesion: 0.10
Nodes (13): ProductCountRepository, Khởi tạo file json mặc định nếu file chưa tồn tại trên ổ cứng., Đọc số lượng sản phẩm OK, NG và Tổng từ file JSON. Returns: Dict[str, int]:…, Lưu dữ liệu số lượng sản phẩm vào file JSON. Args: counts (Dict[str, int]):…, Đặt lại toàn bộ số đếm OK, NG, Tổng về 0 và lưu vào file. Returns: Dict[str,…, Tăng số lượng sản phẩm theo kết quả phán định (OK hoặc NG) và cộng vào Tổng.…, Repository quản lý đọc và ghi file lưu trữ số lượng sản phẩm OK, NG và Tổng., ProductCountService (+5 more)

### Community 157 - "get_instruct_staff_ee"
Cohesion: 0.50
Nodes (4): get_instruct_staff_ee(), FileResponse, get, Trả về file PDF tài liệu hướng dẫn sử dụng phần mềm dành cho kỹ sư EE để xem…

### Community 158 - "PatchCoreTrainRecordRepository"
Cohesion: 0.04
Nodes (67): PatchCoreAnomalyConfig, PatchCoreTrainConfig, Tham số train PatchCore, không chứa đường dẫn dữ liệu của phiên train., Khởi tạo cấu hình tham số cho mô hình PatchCore. Args: config…, EndChippingPatchCoreService, Cấu hình PatchCore cho workflow kiểm tra đầu ống mẻ., Cấu hình PatchCore cho kiểm tra đầu ống mẻ., Khởi tạo service End Chipping với manifest riêng. Args: point_service: Service… (+59 more)

### Community 159 - "camera_status"
Cohesion: 0.29
Nodes (7): camera_status(), exit_camera_config(), get_camera_config(), get, Trả về trạng thái kết nối và cấu hình camera. Input: service container từ…, Lấy cấu hình camera hiện tại, gồm cả white balance calibration., Xác nhận thoát cấu hình camera và yêu cầu frontend tải lại trang chính. Input:…

### Community 161 - "get_instruct_worker"
Cohesion: 0.50
Nodes (4): get_instruct_worker(), FileResponse, get, Trả về file PDF tài liệu hướng dẫn sử dụng phần mềm cho người thao tác để xem…

### Community 166 - "software_information"
Cohesion: 0.40
Nodes (4): get, Trả về metadata phần mềm và các đường dẫn model/output cho giao diện. Input:…, software_information(), software_version()

### Community 170 - "move_to_selected_point"
Cohesion: 0.67
Nodes (4): move_to_selected_point(), write_log_calibration_append(), write_log_calibration_clear(), writeValidationErrors()

## Knowledge Gaps
- **225 isolated node(s):** `AppContext`, `add_product`, `overlay_new_product`, `overlay_accpet_delete_product`, `close_add_product` (+220 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1308 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **37 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `18.5. Chuan hoa judger va inspector name` connect `.error` to `numpy`, `ScratchedPipeItemInspector`, `BorderDetector`, `BorderFilmInspector`, `HoleItemInspector`, `ArmCoverDetector`, `SemiPermeableMembrane`, `WeldSeamAirBubbles`, `JudgmentResult`, `ArmSensorDetector`, `AirBubblesItemInspector`?**
  _High betweenness centrality (0.219) - this node is a cross-community bridge._
- **Why does `20.1. Judment va registry detector` connect `Judment` to `SlitDetector`, `EndChippingInspector`, `ScratchedPipeItemInspector`, `.error`, `BorderFilmInspector`, `ComService`, `HoleItemInspector`, `JudgmentResult`, `AirBubblesItemInspector`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Why does `BorderFilmInspector` connect `BorderFilmInspector` to `.error`, `create_obj_cross_item`, `.fromDict`, `border_film_tool.js`, `Judment`, `items_inspector.js`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Are the 71 inferred relationships involving `ServiceContainer` (e.g. with `3. Quy trình TRONG KHI SỬA (In-Edit Workflow)` and `1. Nguyên tắc kiến trúc cốt lõi`) actually correct?**
  _`ServiceContainer` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `JudgmentResult` (e.g. with `ArmCoverDetector` and `ArmSensorDetector`) actually correct?**
  _`JudgmentResult` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AppContext`, `add_product`, `overlay_new_product` to the rest of the system?**
  _225 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Result` be split into smaller, more focused modules?**
  _Cohesion score 0.059506531204644414 - nodes in this community are weakly interconnected._