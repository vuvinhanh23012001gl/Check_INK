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
    tags=["Law_regulation"]
)

#------- main ---------------------

@router.get("/")
def header_function(services: ServiceContainer = Depends(get_services)):
    print("Client vừa nhấn cấu hình law_regulation")
    choose_product_current = services.obj_choose_product.get_choose_product()
    print("Sản phẩm đang chọn", choose_product_current)
    if not choose_product_current.ok:
        return Result.Fail(choose_product_current.error).to_dict()
    product_id = choose_product_current.data
    product_result = services.obj_products_service.get_product_by_id(product_id)
    if not product_result.ok:
        return Result.Fail(product_result.error).to_dict()
    product = product_result.data
    points_result = services.obj_point_service.get_points_by_product_id(product_id)
    # Ưu tiên lấy dữ liệu từ law_regulation_service
    tree = services.obj_law_regulation_service.get_product_data(str(product_id))
    # Nếu thất bại thì dùng dữ liệu từ point_service
    if not tree.ok or tree.data is None:
        tree = services.obj_point_service.get_point_tree_by_product_id(product_id)
    # print("tree:", tree.data if tree.ok else None)
    return Result.Ok({
        "wid_img": WIDTH_IMG_CAMERA_CAPTURE,
        "hei_img": HEIGHT_IMG_CAMERA_CAPTURE,
        "product": product,
        "data_point": points_result.data if points_result.ok else [],
        "data_master": None,
        "tree": tree,
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
    if not data:
        return Result.Fail(ErrorCode.DATA_INVALID).to_dict()
    choose_product_current = services.obj_choose_product.get_choose_product()
    print("Sản phẩm đang chọn",choose_product_current)
    if not choose_product_current.ok:
        return Result.Fail(choose_product_current.error).to_dict()
    product_id = choose_product_current.data
    tree = services.obj_point_service.get_point_tree_by_product_id(product_id)
    if not tree.ok or tree.data is None:
        return Result.Fail(ErrorCode.FRAME_NOT_FOUND).to_dict()
    result_save = services.obj_law_regulation_service.save_data(data,tree.data)
    return result_save.to_dict()
   


#-------------------------measurement---------------------------
@router.post("/measurement/judment_item")
async def judment_item(
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
    path_img = str(result_get_path_img_master.data)
    img = cv2.imread(path_img)
    _ , polygons = services.obj_deployment_Unet.get_mask_and_polygon(img) 
    polygon_json = [p.squeeze(1).tolist() for p in polygons]
    return Result.Ok({
        "width":img.shape[1],
        "polygon":polygon_json,
    }).to_dict()


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


@router.post("/arm_sensor/judment_item")
async def judment_item_arm_sensor(
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

@router.post("/arm_cover/judment_item")
async def judment_item_arm_cover(
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

# Border Film judgment
@router.post("/boder_film/judment_item")
async def judment_item_boder_film(
    data: dict = Body(),
    services: ServiceContainer = Depends(get_services)
):
    print("nhan vao data nay roi nha", data)
    
    result = ValidateToolLawRegulation.validate_judment_item(data)
    if result.ok:
        print("Kiểm tra dữ liệu đúng")
        
    try:
        product_id = int(data.get("product_id", -1))
        frame_id = int(data["frame_id"])
        items_id = int(data["items_id"])
    except (KeyError, TypeError, ValueError) as e:
        return Result.Fail(f"Dữ liệu không hợp lệ: {e}").to_dict()
        
    result_get_path_img_master = services.obj_point_service.get_path_img_point(
        product_id,
        frame_id,
        items_id
    )
    
    path_img = str(result_get_path_img_master.data)
    img = cv2.imread(path_img)
    if img is None:
        return Result.Fail(ErrorCode.IMAGE_NOT_FOUND).to_dict()
        
    config = services.obj_unet_border_film_service.model_unet.config
    result_polygon = services.obj_unet_border_film_service.extract_border_polygon(
        img=img,
        approx_value=config.epsilon_ratio,
        min_area=config.min_area
    )
    
    if not result_polygon.ok:
        return result_polygon.to_dict()
        
    polygon = result_polygon.data
    polygon_json = polygon.tolist()
    
    return Result.Ok({
        "width": img.shape[1],
        "polygon": polygon_json,
    }).to_dict()



# Permeable membrane
@router.post("/permemble_membrane/judment_item")
async def judment_item_permeable_membrane(
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



@router.post("/hole/judment_item")
async def judment_item_hole(
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
    

@router.post("/scratched_pipe/judment_item")
async def judment_scratched_pipe(
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