from fastapi import APIRouter, Request,Body,Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.dependencies import get_services
from app.container import ServiceContainer

router = APIRouter()
templates = Jinja2Templates(directory="app/static/templates")

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "msg": "Xin chào Ánh 👋"
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
        result = services.obj_manager_product.get_arr_path_img_roi_product_by_id(choose_product_current.data)
        # print("result",result.data)
        # print("status result.ok path_arr_img result.data",result.ok ,result.data)
        return {"status": result.ok ,"path_arr_img":result.data}


