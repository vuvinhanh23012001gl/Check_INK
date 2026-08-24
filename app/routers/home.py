from fastapi import APIRouter, Request,Body,Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.dependencies import get_services
from app.container import ServiceContainer

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Hiển thị màn hình chính cùng tên sản phẩm đang được chọn.

    Input: request FastAPI và service container.
    Output: HTML response có tên sản phẩm hiện tại hoặc trạng thái chưa chọn.
    Errors: không phát sinh; sản phẩm không tồn tại được hiển thị là chưa chọn.
    """
    selected_product_name = "Chưa chọn sản phẩm"
    try:
        services = request.app.state.services
        selected_product_id = services.obj_choose_product.get_choose_product().data
        if selected_product_id != -1:
            product_result = services.obj_products_service.get_product_by_id(selected_product_id)
            if product_result.ok:
                selected_product_name = product_result.data.name
    except (AttributeError, KeyError, RuntimeError):
        pass
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "msg": "Xin chào Ánh 👋",
            "selected_product_name": selected_product_name,
        }
    )




@router.post("/data_home")
def data_home(services: ServiceContainer = Depends(get_services),bayload:dict =  Body(...)):
    # print("----Cung cấp data cho DOM --- ")
    # status = bayload.get("status")
    choose_product_current = services.obj_choose_product.get_choose_product()
    # print("Sản phẩm đang chọn là :",choose_product_current.data)
    if choose_product_current.data == -1:
        msg = " Hiện tại chưa chọn sản phẩm. Vui lòng chọn sản phẩm trước khi chụp!"
        return {"status":False, "message": msg}
    else:
        result = services.obj_products_service.get_arr_path_img_roi_product_by_id(choose_product_current.data)
        # print("result",result.data)
        # print("status result.ok path_arr_img result.data",result.ok ,result.data)
        return {"status": result.ok ,"path_arr_img":result.data}


