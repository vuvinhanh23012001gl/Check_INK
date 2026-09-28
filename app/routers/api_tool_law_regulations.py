import asyncio
from fastapi import APIRouter,Body
from app.container import ServiceContainer
from app.core.dependencies import get_services
from fastapi import APIRouter, Depends
from app.core import Result,ErrorCode
from app.config import WIDTH_IMG_CAMERA_CAPTURE,HEIGHT_IMG_CAMERA_CAPTURE
from app.validate import ValidateToolLawRegulation
import cv2

router = APIRouter(
    prefix="/law_regulation",
    tags=["law_regulation"]
)

#------- main ---------------------

@router.get("/")
def header_function(services: ServiceContainer = Depends(get_services)):
    print("🔧 [Master] Người dùng đã nhấn 'Điều chỉnh master'.")
    print("🔎 [Master] Đang xác định sản phẩm hiện tại...")
    choose_product_current = services.obj_choose_product.get_choose_product()
    print("📦 [Master] Sản phẩm đang chọn:", choose_product_current)
    if not choose_product_current.ok:
        print("❌ [Master] Không xác định được sản phẩm đang chọn.")
        return Result.Fail(choose_product_current.error).to_dict()
    product_id = choose_product_current.data
    product_result = services.obj_products_service.get_product_by_id(product_id)
    if not product_result.ok:
        print(f"❌ [Master] Không lấy được thông tin sản phẩm: {product_id}")
        return Result.Fail(product_result.error).to_dict()
    product = product_result.data
    print(f"✅ [Master] Đã lấy thông tin sản phẩm: {product_id}")

    print("📸 [Master] Đang lấy danh sách ảnh master và điểm kiểm tra...")
    points_result = services.obj_point_service.get_points_by_product_id(product_id)
    if points_result.ok:
        print(f"✅ [Master] Đã lấy dữ liệu điểm/ảnh master cho sản phẩm: {product_id}")
    else:
        print("⚠️ [Master] Không lấy được đầy đủ dữ liệu điểm/ảnh master.")

    print("📋 [Master] Đang lấy cây luật phán định...")
    tree = services.obj_law_regulation_service.get_product_data(str(product_id))
    point_tree = services.obj_point_service.get_point_tree_by_product_id(product_id)
    if not tree.ok or tree.data is None:
        print("⚠️ [Master] Chưa có cây luật riêng, chuyển sang lấy cây điểm mặc định...")
        tree = point_tree
    elif point_tree.ok and point_tree.data:
        # Tự động đồng bộ các frame và point từ points.json vào cây luật master
        product_key = str(product_id)
        if product_key in point_tree.data and product_key in tree.data:
            base_frames = point_tree.data[product_key]
            current_frames = tree.data[product_key]
            for f_id, points_map in base_frames.items():
                if f_id not in current_frames:
                    current_frames[f_id] = {}
                for p_id in points_map.keys():
                    if p_id not in current_frames[f_id]:
                        current_frames[f_id][p_id] = {}
    if tree.ok and tree.data is not None:
        print("✅ [Master] Đã lấy cây luật phán định của master.")
    else:
        print("⚠️ [Master] Không có cây luật phán định để nạp.")
    print("✅ [Master] Hoàn tất chuẩn bị dữ liệu điều chỉnh master.")
    return Result.Ok({
        "wid_img": WIDTH_IMG_CAMERA_CAPTURE,
        "hei_img": HEIGHT_IMG_CAMERA_CAPTURE,
        "product": product,
        "data_point": points_result.data if points_result.ok else [],
        "data_master": None,
        "tree": tree.data if tree.ok else None,
    }).to_dict()

@router.get("/exit")
async def exit():
    return {
        "status": "ok",
        "redirect_url": "/"
}

@router.post("/save")
def save(data:dict= Body(),services: ServiceContainer = Depends(get_services)):
    print("---API save---")
    print("Dữ liệu nhận save",data)
    logs = ["Bắt đầu lưu dữ liệu master."]

    def response_with_logs(result):
        """Bổ sung nhật ký các bước lưu vào response API."""
        response = result.to_dict()
        response["logs"] = logs
        return response

    if not data:
        logs.append("Dữ liệu master rỗng.")
        return response_with_logs(Result.Fail(ErrorCode.DATA_INVALID))
    canvas_width = data.get("WidthCanvas", 1024)
    canvas_height = data.get("HeightCanvas", 768)
    payload = data.get("data", data)
    try:
        canvas_width = int(canvas_width)
        canvas_height = int(canvas_height)
    except (TypeError, ValueError):
        logs.append("Kích thước canvas không hợp lệ.")
        return response_with_logs(Result.Fail(ErrorCode.INVALID_INPUT))
    logs.append(f"Đã nhận canvas {canvas_width} x {canvas_height}.")
    choose_product_current = services.obj_choose_product.get_choose_product()
    print("Sản phẩm đang chọn",choose_product_current)
    if not choose_product_current.ok:
        logs.append("Không xác định được sản phẩm đang chọn.")
        return response_with_logs(Result.Fail(choose_product_current.error))
    product_id = choose_product_current.data
    logs.append(f"Đang xử lý master của sản phẩm {product_id}.")
    tree = services.obj_point_service.get_point_tree_by_product_id(product_id)
    if not tree.ok or tree.data is None:
        logs.append("Không tìm thấy cấu trúc point/frame của sản phẩm.")
        return response_with_logs(Result.Fail(ErrorCode.FRAME_NOT_FOUND))
    logs.append("Đã kiểm tra cấu trúc point/frame.")

    # Làm sạch payload: loại bỏ các frame_id hoặc point_id rác (như "-1") không thuộc cây định danh hợp lệ của sản phẩm
    product_key = str(product_id)
    if isinstance(payload, dict) and product_key in payload and isinstance(payload[product_key], dict) and product_key in tree.data:
        valid_frames = tree.data[product_key]
        cleaned_product_frames = {}
        for f_id, f_data in payload[product_key].items():
            str_f_id = str(f_id)
            if str_f_id in valid_frames and isinstance(f_data, dict):
                cleaned_points = {}
                for p_id, p_data in f_data.items():
                    str_p_id = str(p_id)
                    if str_p_id in valid_frames[str_f_id]:
                        cleaned_points[str_p_id] = p_data
                    else:
                        print(f"⚠️ [Master][Save] Bỏ qua point_id không hợp lệ: {p_id}")
                cleaned_product_frames[str_f_id] = cleaned_points
            else:
                print(f"⚠️ [Master][Save] Bỏ qua frame_id không hợp lệ: {f_id}")
        payload[product_key] = cleaned_product_frames

    converted = services.obj_law_regulation_service.convert_canvas_coordinates(
        payload,
        product_id,
        services.obj_point_service,
        canvas_width,
        canvas_height,
    )
    if not converted.ok:
        logs.append("Quy đổi tọa độ master thất bại.")
        return response_with_logs(converted)
    logs.append("Đã chuyển tọa độ canvas sang pixel ảnh master.")
    result_save = services.obj_law_regulation_service.save_data(converted.data,tree.data)
    if result_save.ok:
        logs.append("Lưu dữ liệu master thành công.")
    else:
        logs.append(f"Lưu dữ liệu master thất bại: {result_save.message()}.")
    return response_with_logs(result_save)
   


#-------------------------measurement---------------------------
@router.post("/measurement/run_model")
@router.post("/slit/run_model")
async def run_model_measurement(
    data: dict = Body(),
    services: ServiceContainer = Depends(get_services)
):
    # print(data)
    result = ValidateToolLawRegulation.validate_judment_item(data)
    if result.ok:
        print("Kiểm tra dữ liệu đúng")
    try:
        product_id  =  int(data.get("product_id", -1))
        frame_id = int(data["frame_id"])
        items_id = int(data["items_id"])
    except (KeyError, TypeError, ValueError) as e:
        return Result.Fail(f"Dữ liệu không hợp lệ: {e}").to_dict()
    result_get_path_img_master = services.obj_point_service.get_path_img_point(
        product_id,
        frame_id,
        items_id
    )
    if not result_get_path_img_master.ok:
        return Result.Fail("Không tìm thấy ảnh master của item đang chọn.").to_dict()
    path_img = str(result_get_path_img_master.data)
    img = cv2.imread(path_img)
    if img is None:
        return Result.Fail("Không đọc được ảnh master của item đang chọn.").to_dict()
    _ , polygons = await asyncio.to_thread(
        services.obj_deployment_Unet.get_mask_and_polygon,
        img,
    )
    polygon_json = [p.squeeze(1).tolist() for p in polygons]
    return Result.Ok({
        "width":img.shape[1],
        "polygon":polygon_json,
    }).to_dict()


@router.post("/end_chipping/create_model")
async def create_end_chipping_model(
    data: dict = Body(),
    services: ServiceContainer = Depends(get_services),
):
    """Nhận ROI End Chipping và khởi động train PatchCore nền."""
    try:
        product_id = int(data["product_id"])
        frame_id = int(data["frame_id"])
        item_id = int(data.get("item_id", data.get("items_id")))
        image_count = int(data.get("image_count", 16))
        crop_roi = data["crop_roi"]
        width_canvas = int(data.get("width_canvas", 0)) or None
    except (KeyError, TypeError, ValueError):
        return Result.Fail(ErrorCode.INVALID_INPUT).to_dict()
    try:
        return services.obj_end_chipping_patch_core_service.create_model(
            product_id, frame_id, item_id, crop_roi, image_count, width_canvas
        )
    except ValueError as error:
        if "đang chạy" in str(error) or "bận" in str(error):
            return Result.Fail(ErrorCode.PATCHCORE_BUSY).to_dict()
        return Result.Fail(ErrorCode.INVALID_INPUT).to_dict()


@router.post("/end_chipping/run_model")
async def run_end_chipping_model(
    data: dict = Body(),
    services: ServiceContainer = Depends(get_services),
):
    """Chạy inference PatchCore cho item End Chipping."""
    try:
        product_id = int(data["product_id"])
        frame_id = int(data["frame_id"])
        item_id = int(data.get("item_id", data.get("items_id")))
        crop_roi = data["crop_roi"]
        width_canvas = int(data.get("width_canvas", 0)) or None
        return services.obj_end_chipping_patch_core_service.run_model(
            product_id, frame_id, item_id, crop_roi, width_canvas
        )
    except (KeyError, TypeError, ValueError):
        return Result.Fail(ErrorCode.INVALID_INPUT).to_dict()


@router.get("/end_chipping/train_status")
async def end_chipping_train_status(
    product_id: int,
    frame_id: int,
    item_id: int,
    services: ServiceContainer = Depends(get_services),
):
    """Lấy trạng thái phiên train PatchCore End Chipping."""
    try:
        return services.obj_end_chipping_patch_core_service.training_status(
            int(product_id), int(frame_id), int(item_id)
        )
    except (TypeError, ValueError, AttributeError, OSError):
        return Result.Fail(ErrorCode.INVALID_INPUT).to_dict()


@router.get("/end_chipping/runtime_images")
async def end_chipping_runtime_images(
    product_id: int,
    frame_id: int,
    item_id: int,
    services: ServiceContainer = Depends(get_services),
):
    """Lấy ảnh runtime/good của session End Chipping mới nhất."""
    return services.obj_end_chipping_patch_core_service.get_runtime_images(
        product_id, frame_id, item_id
    )


@router.delete("/end_chipping/runtime_image")
async def delete_end_chipping_runtime_image(
    data: dict = Body(),
    services: ServiceContainer = Depends(get_services),
):
    """Xóa một ảnh runtime/good của session End Chipping."""
    try:
        return services.obj_end_chipping_patch_core_service.delete_runtime_image(
            int(data["product_id"]),
            int(data["frame_id"]),
            int(data.get("item_id", data.get("items_id"))),
            str(data["image_name"]),
        )
    except (KeyError, TypeError, ValueError):
        return Result.Fail(ErrorCode.INVALID_INPUT).to_dict()


@router.delete("/end_chipping/model")
async def delete_end_chipping_model(
    data: dict = Body(),
    services: ServiceContainer = Depends(get_services),
):
    """Xóa session model PatchCore và record tương ứng của item End Chipping."""
    try:
        return services.obj_end_chipping_patch_core_service.delete_model(
            int(data["product_id"]),
            int(data["frame_id"]),
            int(data.get("item_id", data.get("items_id"))),
        )
    except (KeyError, TypeError, ValueError, OSError):
        return Result.Fail(ErrorCode.INVALID_INPUT).to_dict()


@router.post("/foreign_object/create_model")
async def create_foreign_object_model(
    data: dict = Body(),
    services: ServiceContainer = Depends(get_services),
):
    """Nhận ROI Dị vật và khởi động train PatchCore nền.

    Args:
        data: Product, frame, item, crop ROI, số lượng ảnh và canvas width.
        services: Container cung cấp service PatchCore Dị vật.

    Returns:
        dict: Trạng thái khởi động train hoặc lỗi dữ liệu đầu vào.

    Raises:
        Không phát sinh lỗi ra ngoài; lỗi được đóng gói bằng Result.
    """
    try:
        return services.obj_foreign_object_patch_core_service.create_model(
            int(data["product_id"]),
            int(data["frame_id"]),
            int(data.get("item_id", data.get("items_id"))),
            data["crop_roi"],
            int(data.get("image_count", 16)),
            int(data.get("width_canvas", 0)) or None,
        )
    except (KeyError, TypeError, ValueError):
        return Result.Fail(ErrorCode.INVALID_INPUT).to_dict()


@router.get("/foreign_object/train_status")
async def foreign_object_train_status(
    product_id: int,
    frame_id: int,
    item_id: int,
    services: ServiceContainer = Depends(get_services),
):
    """Lấy trạng thái train PatchCore Dị vật của item hiện tại.

    Args:
        product_id: Mã product.
        frame_id: Mã frame.
        item_id: Mã item.
        services: Container cung cấp service PatchCore Dị vật.

    Returns:
        dict: Trạng thái worker và model đã tạo.

    Raises:
        Không phát sinh lỗi ra ngoài; lỗi được đóng gói bằng Result.
    """
    try:
        return services.obj_foreign_object_patch_core_service.training_status(
            product_id,
            frame_id,
            item_id,
        )
    except (TypeError, ValueError, AttributeError, OSError):
        return Result.Fail(ErrorCode.INVALID_INPUT).to_dict()


@router.get("/foreign_object/runtime_images")
async def foreign_object_runtime_images(
    product_id: int,
    frame_id: int,
    item_id: int,
    services: ServiceContainer = Depends(get_services),
):
    """Lấy danh sách ảnh runtime/good của model Dị vật.

    Args:
        product_id: Mã product.
        frame_id: Mã frame.
        item_id: Mã item.
        services: Container cung cấp service PatchCore Dị vật.

    Returns:
        dict: Danh sách ảnh runtime hoặc trạng thái không có model.

    Raises:
        Không phát sinh lỗi ra ngoài.
    """
    return services.obj_foreign_object_patch_core_service.get_runtime_images(
        product_id,
        frame_id,
        item_id,
    )


@router.delete("/foreign_object/runtime_image")
async def delete_foreign_object_runtime_image(
    data: dict = Body(),
    services: ServiceContainer = Depends(get_services),
):
    """Xóa một ảnh runtime/good của model Dị vật.

    Args:
        data: Product, frame, item và tên ảnh cần xóa.
        services: Container cung cấp service PatchCore Dị vật.

    Returns:
        dict: Tên ảnh đã xóa hoặc lỗi dữ liệu.

    Raises:
        Không phát sinh lỗi ra ngoài; lỗi được đóng gói bằng Result.
    """
    try:
        return services.obj_foreign_object_patch_core_service.delete_runtime_image(
            int(data["product_id"]),
            int(data["frame_id"]),
            int(data.get("item_id", data.get("items_id"))),
            str(data["image_name"]),
        )
    except (KeyError, TypeError, ValueError):
        return Result.Fail(ErrorCode.INVALID_INPUT).to_dict()


@router.post("/foreign_object/run_model")
async def run_foreign_object_model(
    data: dict = Body(),
    services: ServiceContainer = Depends(get_services),
):
    """Chạy inference PatchCore cho model Dị vật của item hiện tại.

    Args:
        data: Product, frame, item, crop ROI và canvas width.
        services: Container cung cấp service PatchCore Dị vật.

    Returns:
        dict: Ảnh overlay, anomaly score, bounding boxes hoặc lỗi.

    Raises:
        Không phát sinh lỗi ra ngoài; lỗi được đóng gói bằng Result.
    """
    try:
        return services.obj_foreign_object_patch_core_service.run_model(
            int(data["product_id"]),
            int(data["frame_id"]),
            int(data.get("item_id", data.get("items_id"))),
            data["crop_roi"],
            int(data.get("width_canvas", 0)) or None,
        )
    except (KeyError, TypeError, ValueError):
        return Result.Fail(ErrorCode.INVALID_INPUT).to_dict()


@router.post("/foreign_object/run_object_model")
async def run_foreign_object_detection_model(
    data: dict = Body(),
    services: ServiceContainer = Depends(get_services),
):
    """Chạy YOLO trên từng vùng bất thường do PatchCore phát hiện.

    Args:
        data: Product, frame, item, crop ROI và canvas width.
        services: Container cung cấp service PatchCore Dị vật.

    Returns:
        dict: Ảnh overlay, các vùng bất thường đã crop và detection YOLO.

    Raises:
        Không phát sinh lỗi ra ngoài; lỗi được đóng gói bằng Result.
    """
    try:
        return services.obj_foreign_object_patch_core_service.run_model_with_object_detection(
            int(data["product_id"]),
            int(data["frame_id"]),
            int(data.get("item_id", data.get("items_id"))),
            data["crop_roi"],
            int(data.get("width_canvas", 0)) or None,
        )
    except (KeyError, TypeError, ValueError):
        return Result.Fail(ErrorCode.INVALID_INPUT).to_dict()


@router.delete("/foreign_object/model")
async def delete_foreign_object_model(
    data: dict = Body(),
    services: ServiceContainer = Depends(get_services),
):
    """Xóa session PatchCore và record manifest đúng của model Dị vật.

    Args:
        data: Product, frame và item của model cần xóa.
        services: Container cung cấp service PatchCore Dị vật.

    Returns:
        dict: Thư mục model, số record đã xóa hoặc lỗi.

    Raises:
        Không phát sinh lỗi ra ngoài; lỗi được đóng gói bằng Result.
    """
    try:
        return services.obj_foreign_object_patch_core_service.delete_model(
            int(data["product_id"]),
            int(data["frame_id"]),
            int(data.get("item_id", data.get("items_id"))),
        )
    except (KeyError, TypeError, ValueError, OSError):
        return Result.Fail(ErrorCode.INVALID_INPUT).to_dict()


@router.post("/measurement/auto_create_line")
async def auto_create_line(
    data: dict = Body(),
    services: ServiceContainer = Depends(get_services)
):
    result = ValidateToolLawRegulation.validate_levels(data)
    if not result.ok:
        return result.to_dict()
    try:
        lengthen_line  =  int(data.get("lengthen_line", -1))
        product_select_now = int(data["product"])
        frame_select_now = int(data["frame"])
        item_select_now = int(data["items"])
        distance_line = int(data.get("distance_line", -1))
        levels = [
            float(data["Level1_auto"]),
            float(data["Level2_auto"]),
            float(data["Level3_auto"]),
            float(data["Level4_auto"]),
            float(data["Level5_auto"]),
        ]
    except (KeyError, TypeError, ValueError) as e:
        return Result.Fail(f"Dữ liệu không hợp lệ: {e}").to_dict()
    result_get_path_img_master = services.obj_point_service.get_path_img_point(
        product_select_now,
        frame_select_now,
        item_select_now
    )
    if not result_get_path_img_master.ok:
        return result_get_path_img_master.to_dict()
    path_img = str(result_get_path_img_master.data)
    img = cv2.imread(path_img)
    print("distance_line",distance_line,type(distance_line))
    print("lengthen_line",lengthen_line,type(lengthen_line))
    if img is None:
        return Result.Fail("Không thể đọc ảnh").to_dict()
    lines_final, (width, height), polygon = (
        services.obj_deployment_Unet.automate_sampling_for_checking(
            img,
            distance_line,lengthen_line
        )
    )
    polygon_json = [p.squeeze(1).tolist() for p in polygon]
    print("polygon_json",polygon_json)
    # print("type polygon",type(polygon))
    # print("polygon",polygon)
    return Result.Ok({
        "level": levels,
        "lines": lines_final,
        "width": width,
        "height": height,
        "polygon":polygon_json,
    }).to_dict()

# ARM sensor


@router.post("/arm_sensor/run_model")
async def run_model_arm_sensor(
    data: dict = Body(), services: ServiceContainer = Depends(get_services)
):
    print("Payload nhận được:", data)
    result_val = ValidateToolLawRegulation.validate_judment_item(data)
    if not result_val.ok:
        # Trả về lỗi định dạng kèm Message lỗi tương ứng
        return result_val.to_dict()
    print("Kiểm tra dữ liệu thành công")
    select_data = data["select"]
    box_data = data["box"]
    product_id = int(select_data["product_id"])
    frame_id = int(select_data["frame_id"])
    items_id = int(select_data["items_id"])
    
    x_start = int(box_data["xStart"])
    y_start = int(box_data["yStart"])
    x_end = int(box_data["xEnd"])
    y_end = int(box_data["yEnd"])
    width_canvas = int(data.get("WidthCanvas", 1)) 
    label_name = services.CLASS_STRUCTURE_NAME.SENSOR_ARM.value
    try:
        result_get_path_img_master = (
            services.obj_point_service.get_path_img_point(
                product_id, frame_id, items_id
            )
        )
        print("result_get_path_img_master:", result_get_path_img_master)
        if not result_get_path_img_master.ok:
            return result_get_path_img_master.to_dict()
        path_img = str(result_get_path_img_master.data)
        img = cv2.imread(path_img)
        
        if img is None:
            print("Không tìm thấy ảnh tại đường dẫn:", path_img)
            return Result.Fail(ErrorCode.IMAGE_NOT_FOUND).to_dict()
        result_objects = (
            services.obj_structure_model_service.get_objects_by_label(
                image=img, 
                x1=x_start, 
                y1=y_start, 
                x2=x_end, 
                y2=y_end, 
                label=label_name, 
                width_canvas=width_canvas
            )
        )
        
        if not result_objects.ok:
            return result_objects.to_dict()
        detected_objects = result_objects.data
        return Result.Ok(
            {
                "width": img.shape[1],
                "objects": detected_objects,
            }
        ).to_dict()

    except Exception as e:
        print(f"Lỗi hệ thống trong quá trình xử lý: {str(e)}")
        return {
            "ok": False,
            "data": None,
            "error_code": ErrorCode.DATA_INVALID.value,
            "error_name": ErrorCode.DATA_INVALID.name,
            "message": f"[Lỗi hệ thống] {str(e)}"
        }
    
# ARM cover

@router.post("/arm_cover/run_model")
async def run_model_arm_cover(
    data: dict = Body(), services: ServiceContainer = Depends(get_services)
):
    print("Payload nhận được:", data)
    result_val = ValidateToolLawRegulation.validate_judment_item(data)
    if not result_val.ok:
        # Trả về lỗi định dạng kèm Message lỗi tương ứng
        return result_val.to_dict()
    print("Kiểm tra dữ liệu thành công")
    select_data = data["select"]
    box_data = data["box"]
    product_id = int(select_data["product_id"])
    frame_id = int(select_data["frame_id"])
    items_id = int(select_data["items_id"])
    
    x_start = int(box_data["xStart"])
    y_start = int(box_data["yStart"])
    x_end = int(box_data["xEnd"])
    y_end = int(box_data["yEnd"])
    width_canvas = int(data.get("WidthCanvas", 1)) 
    label_name = services.CLASS_STRUCTURE_NAME.COVER_ARM.value
    print("label_name",label_name)
    try:
        result_get_path_img_master = (
            services.obj_point_service.get_path_img_point(
                product_id, frame_id, items_id
            )
        )
        print("result_get_path_img_master:", result_get_path_img_master)
        if not result_get_path_img_master.ok:
            return result_get_path_img_master.to_dict()
        path_img = str(result_get_path_img_master.data)
        img = cv2.imread(path_img)
        
        if img is None:
            print("Không tìm thấy ảnh tại đường dẫn:", path_img)
            return Result.Fail(ErrorCode.IMAGE_NOT_FOUND).to_dict()
        result_objects = (
            services.obj_structure_model_service.get_objects_by_label(
                image=img, 
                x1=x_start, 
                y1=y_start, 
                x2=x_end, 
                y2=y_end, 
                label=label_name, 
                width_canvas=width_canvas
            )
        )
        
        if not result_objects.ok:
            return result_objects.to_dict()
        detected_objects = result_objects.data
        return Result.Ok(
            {
                "width": img.shape[1],
                "objects": detected_objects,
            }
        ).to_dict()

    except Exception as e:
        print(f"Lỗi hệ thống trong quá trình xử lý: {str(e)}")
        return {
            "ok": False,
            "data": None,
            "error_code": ErrorCode.DATA_INVALID.value,
            "error_name": ErrorCode.DATA_INVALID.name,
            "message": f"[Lỗi hệ thống] {str(e)}"
        }

# Weld seam air bubbles judgment

@router.post("/air_bubbles/run_model")
async def run_model_air_bubbles(
    data: dict = Body(), services: ServiceContainer = Depends(get_services)
):
    """Phán định bọt khí trên toàn bộ các vùng đã cấu hình của item."""
    result_val = ValidateToolLawRegulation.validate_judment_item(data)
    if not result_val.ok:
        return result_val.to_dict()
    try:
        select_data = data["select"]
        regions = data["boxes"]
        product_id = int(select_data["product_id"])
        frame_id = int(select_data["frame_id"])
        items_id = int(select_data["items_id"])
        width_canvas = int(data.get("WidthCanvas", 1))
    except (KeyError, TypeError, ValueError) as error:
        return Result.Fail(f"Dữ liệu không hợp lệ: {error}").to_dict()
    if not isinstance(regions, list) or not regions:
        return Result.Fail(ErrorCode.INVALID_INPUT).to_dict()
    try:
        result_path = services.obj_point_service.get_path_img_point(
            product_id, frame_id, items_id
        )
        if not result_path.ok:
            return result_path.to_dict()
        image = cv2.imread(str(result_path.data))
        result_judgment = services.obj_surface_model_service.judge_regions(
            image, regions, width_canvas
        )
        return result_judgment.to_dict()
    except Exception as error:
        print(f"Lỗi phán định bọt khí đường hàn: {error}")
        return Result.Fail(f"[Lỗi hệ thống] {error}").to_dict()

# Border Film judgment
@router.post("/border_film/run_model")
async def run_model_border_film(
    data: dict = Body(),
    services: ServiceContainer = Depends(get_services)
):
    """Chạy model phát hiện polygon đường biên film.

    Input: Payload trực tiếp ``product_id/frame_id/items_id`` hoặc được bọc
        trong object ``select``.
    Output: Polygon model phát hiện và kích thước ảnh cho client hiển thị.
    Errors: Trả về lỗi input, product/frame/item hoặc ảnh khi không thể chạy model.
    """
    print("nhan vao data nay roi nha", data)
    
    selected = data.get("select", data) if isinstance(data, dict) else None
    validation_payload = {"select": selected}
    result = ValidateToolLawRegulation.validate_judment_item(validation_payload)
    if not result.ok:
        return result.to_dict()
    print("Kiểm tra dữ liệu đúng")
        
    try:
        product_id = int(selected["product_id"])
        frame_id = int(selected["frame_id"])
        items_id = int(selected["items_id"])
    except (KeyError, TypeError, ValueError) as e:
        return Result.Fail(f"Dữ liệu không hợp lệ: {e}").to_dict()
        
    result_get_path_img_master = services.obj_point_service.get_path_img_point(
        product_id,
        frame_id,
        items_id
    )
    if not result_get_path_img_master.ok:
        return result_get_path_img_master.to_dict()
    
    path_img = str(result_get_path_img_master.data)
    img = cv2.imread(path_img)
    if img is None:
        return Result.Fail(ErrorCode.IMAGE_NOT_FOUND).to_dict()
        
    config = services.obj_border_detector.unet_model.config
    polygon = services.obj_border_detector.unet_model.get_polygon(
        img,
        Approx_value=config.epsilon_ratio,
        min_area=config.min_area,
    )
    return Result.Ok({
        "model": "border_film",
        "width": img.shape[1],
        "height": img.shape[0],
        "polygon": polygon.tolist() if polygon is not None else None,
    }).to_dict()



# Permeable membrane
@router.post("/permeable_membrane/run_model")
async def run_model_permeable_membrane(
    data: dict = Body(), services: ServiceContainer = Depends(get_services)
):
    print("Payload nhận được:", data)
    result_val = ValidateToolLawRegulation.validate_judment_item(data)
    if not result_val.ok:
        # Trả về lỗi định dạng kèm Message lỗi tương ứng
        return result_val.to_dict()
    print("Kiểm tra dữ liệu thành công")
    select_data = data["select"]
    box_data = data["box"]
    product_id = int(select_data["product_id"])
    frame_id = int(select_data["frame_id"])
    items_id = int(select_data["items_id"])
    
    x_start = int(box_data["xStart"])
    y_start = int(box_data["yStart"])
    x_end = int(box_data["xEnd"])
    y_end = int(box_data["yEnd"])
    width_canvas = int(data.get("WidthCanvas", 1)) 
    try:
        result_get_path_img_master = (
            services.obj_point_service.get_path_img_point(
                product_id, frame_id, items_id
            )
        )
        print("result_get_path_img_master:", result_get_path_img_master)
        if not result_get_path_img_master.ok:
            return result_get_path_img_master.to_dict()
        path_img = str(result_get_path_img_master.data)
        img = cv2.imread(path_img)
        
        if img is None:
            print("Không tìm thấy ảnh tại đường dẫn:", path_img)
            return Result.Fail(ErrorCode.IMAGE_NOT_FOUND).to_dict()
        
        result_objects = services.obj_judment_permeable_membrane_service.extract_membrane_polygons(img,x_start,y_start,x_end,y_end,width_canvas)
        print("result_objects",result_objects)
        
        if not result_objects.ok:
            return result_objects.to_dict()
        detected_objects = result_objects.data
        return Result.Ok(
            {
                "width": img.shape[1],
                "objects": detected_objects,
            }
        ).to_dict()

    except Exception as e:
        print(f"Lỗi hệ thống trong quá trình xử lý: {str(e)}")
        return {
            "ok": False,
            "data": None,
            "error_code": ErrorCode.DATA_INVALID.value,
            "error_name": ErrorCode.DATA_INVALID.name,
            "message": f"[Lỗi hệ thống] {str(e)}"
        }



@router.post("/hole/run_model")
async def run_model_hole(
    data: dict = Body(), services: ServiceContainer = Depends(get_services)
):
    print("Payload nhận được:", data)
    result_val = ValidateToolLawRegulation.validate_judment_item(data)
    if not result_val.ok:
        # Trả về lỗi định dạng kèm Message lỗi tương ứng
        return result_val.to_dict()
    print("Kiểm tra dữ liệu thành công")
    select_data = data["select"]
    box_data = data["box"]
    product_id = int(select_data["product_id"])
    frame_id = int(select_data["frame_id"])
    items_id = int(select_data["items_id"])
    
    x_start = int(box_data["xStart"])
    y_start = int(box_data["yStart"])
    x_end = int(box_data["xEnd"])
    y_end = int(box_data["yEnd"])
    width_canvas = int(data.get("WidthCanvas", 1)) 
    label_name = services.CLASS_STRUCTURE_NAME.HOLE.value
    print("label_name",label_name)
    try:
        result_get_path_img_master = (
            services.obj_point_service.get_path_img_point(
                product_id, frame_id, items_id
            )
        )
        print("result_get_path_img_master:", result_get_path_img_master)
        if not result_get_path_img_master.ok:
            return result_get_path_img_master.to_dict()
        path_img = str(result_get_path_img_master.data)
        img = cv2.imread(path_img)
        
        if img is None:
            print("Không tìm thấy ảnh tại đường dẫn:", path_img)
            return Result.Fail(ErrorCode.IMAGE_NOT_FOUND).to_dict()
        result_objects = (
            services.obj_structure_model_service.get_objects_by_label(
                image=img, 
                x1=x_start, 
                y1=y_start, 
                x2=x_end, 
                y2=y_end, 
                label = label_name, 
                width_canvas = width_canvas
            )
        )
        
        if not result_objects.ok:
            return result_objects.to_dict()
        detected_objects = result_objects.data
        return Result.Ok(
            {
                "width": img.shape[1],
                "objects": detected_objects,
            }
        ).to_dict()

    except Exception as e:
        print(f"Lỗi hệ thống trong quá trình xử lý: {str(e)}")
        return {
            "ok": False,
            "data": None,
            "error_code": ErrorCode.DATA_INVALID.value,
            "error_name": ErrorCode.DATA_INVALID.name,
            "message": f"[Lỗi hệ thống] {str(e)}"
        }
    

@router.post("/scratched_pipe/run_model")
async def run_model_scratched_pipe(
    data: dict = Body(), services: ServiceContainer = Depends(get_services)
):
    print("Payload nhận được:", data)
    result_val = ValidateToolLawRegulation.validate_judment_item(data)
    if not result_val.ok:
        # Trả về lỗi định dạng kèm Message lỗi tương ứng
        return result_val.to_dict()
    print("Kiểm tra dữ liệu thành công")
    select_data = data["select"]
    box_data = data["box"]
    product_id = int(select_data["product_id"])
    frame_id = int(select_data["frame_id"])
    items_id = int(select_data["items_id"])
    
    x_start = int(box_data["xStart"])
    y_start = int(box_data["yStart"])
    x_end = int(box_data["xEnd"])
    y_end = int(box_data["yEnd"])
    width_canvas = int(data.get("WidthCanvas", 1)) 
    label_name = services.CLASS_SURFACE_NAME.SCRATCH.value #cai nay can sua
    print("label_name",label_name)
    try:
        result_get_path_img_master = (
            services.obj_point_service.get_path_img_point(
                product_id, frame_id, items_id
            )
        )
        print("result_get_path_img_master:", result_get_path_img_master)
        if not result_get_path_img_master.ok:
            return result_get_path_img_master.to_dict()
        path_img = str(result_get_path_img_master.data)
        img = cv2.imread(path_img)
        
        if img is None:
            print("Không tìm thấy ảnh tại đường dẫn:", path_img)
            return Result.Fail(ErrorCode.IMAGE_NOT_FOUND).to_dict()
        result_objects = (
            services.obj_surface_model_service.get_objects_by_label(
                image=img, 
                x1=x_start, 
                y1=y_start, 
                x2=x_end, 
                y2=y_end, 
                label = label_name, 
                width_canvas = width_canvas
            )
        )
        
        if not result_objects.ok:
            return result_objects.to_dict()
        detected_objects = result_objects.data
        return Result.Ok(
            {
                "width": img.shape[1],
                "objects": detected_objects,
            }
        ).to_dict()

    except Exception as e:
        print(f"Lỗi hệ thống trong quá trình xử lý: {str(e)}")
        return {
            "ok": False,
            "data": None,
            "error_code": ErrorCode.DATA_INVALID.value,
            "error_name": ErrorCode.DATA_INVALID.name,
            "message": f"[Lỗi hệ thống] {str(e)}"
        }