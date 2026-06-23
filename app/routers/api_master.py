from fastapi import APIRouter,Body
from app.container import ServiceContainer
from app.core.dependencies import get_services
from fastapi import APIRouter, Depends
from app.core import (Result,ErrorCode)
from app.config import WIDTH_IMG_CAMERA_CAPTURE,HEIGHT_IMG_CAMERA_CAPTURE


router = APIRouter(
    prefix="/master",
    tags=["Master"]
)




@router.get("/")
def header_function(services: ServiceContainer = Depends(get_services)):
    print("Client vừa nhấn cấu hình master")
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