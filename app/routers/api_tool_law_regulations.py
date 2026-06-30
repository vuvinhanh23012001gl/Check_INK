from fastapi import APIRouter,Body
from app.container import ServiceContainer
from app.core.dependencies import get_services
from fastapi import APIRouter, Depends
from app.core import Result
from app.config import WIDTH_IMG_CAMERA_CAPTURE,HEIGHT_IMG_CAMERA_CAPTURE
from app.validate import ValidateToolLawRegulation
import cv2

router = APIRouter(
    prefix="/law_regulation",
    tags=["Law_regulation"]
)


@router.post("/auto_create_line")
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
    

@router.get("/")
def header_function(services: ServiceContainer = Depends(get_services)):
    print("Client vừa nhấn cấu hình law_regulation")
    choose_product_current = services.obj_choose_product.get_choose_product()
    print("Sản phẩm đang chọn",choose_product_current)
    if not choose_product_current.ok:
        return Result.Fail(choose_product_current.error).to_dict()
    product_id = choose_product_current.data
    product_result = services.obj_products_service.get_product_by_id(product_id)
    if not product_result.ok:
        return Result.Fail(product_result.error).to_dict()
    product = product_result.data
    points_result = services.obj_point_service.get_points_by_product_id(product_id)
    tree = services.obj_point_service.get_point_tree_by_product_id(product_id)
    return Result.Ok({
        "wid_img":WIDTH_IMG_CAMERA_CAPTURE,"hei_img":HEIGHT_IMG_CAMERA_CAPTURE,
        "product": product,
        "data_point": points_result.data if points_result.ok else [],
        "data_master":None,
        "tree":tree,
    }).to_dict()



@router.post("/judment_item")
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
    polygons 
    polygon_json = [p.squeeze(1).tolist() for p in polygons]
    return Result.Ok({
        "width":img.shape[1],
        "polygon":polygon_json,
    }).to_dict()
