from fastapi import APIRouter, Form, File, UploadFile,Query,Depends
from app.core.dependencies import get_services
from app.services.container import ServiceContainer
from app.services.product import TypeProduct
router = APIRouter(
    prefix="/product",
    tags=["Product"]
)

@router.get("/get_inf_product")
def get_product(services: ServiceContainer = Depends(get_services)):
    data = services.obj_manager_product.get_to_dict_arr_path_src()
    select_product = services.obj_choose_product.get_choose_product_pick()
    # print(data)
    return { "success": True, "data": data,"current_option":select_product}

@router.get("/select_product_new")
def select_product_new(services: ServiceContainer = Depends(get_services),ID_Choose:int = Query(...,description="San pham chon")):
    print(ID_Choose)
    status_set = services.obj_choose_product.set_choose_product(ID_Choose)
    # print(data)
    return {"success": True} if status_set else {"success": False}
    
@router.get("/")
def list_product(services: ServiceContainer = Depends(get_services)):
    data = services.obj_manager_product.get_to_dict_arr_path_src()
    # print(data)
    return { "success": True, "data": data}

@router.get("/erase_product")
def erase_product(services: ServiceContainer = Depends(get_services),ID_Erase:int = Query(...,description= "Xoa San Pham")):
    status,message  = services.obj_manager_product.delete_product_by_id(ID_Erase)
    if not status:
        return {"success":False,"message":message}
    else:
        # Kiem tra san pham xoa co phai san pham dang chon khong neu la san pham dang chon thi reset  bien chon bang 1
        select_product = services.obj_choose_product.get_choose_product_pick()
        print("San pham xoa",select_product,ID_Erase)
        if select_product == ID_Erase:
            print("Xóa đúng phần tử đang chọn nên sé reset cái chọn bằng -1 để xóa thành công")
            services.obj_choose_product.set_value_default() #set lai choose -1
        return { "success": True}



@router.post("/add")
async def add_product(
    services: ServiceContainer = Depends(get_services),
    id: int = Form(...),
    name: str = Form(...),
    description: str = Form(...),
    images: UploadFile = File(...)
):
    status_check_id = services.obj_logic.is_valid_id(id)
    if not status_check_id:
        return { "success": False, "message": "ErroDataIncorectID" }
    print(
        "Received:",
        id,
        name,
        description,
        images.filename,
        images.content_type
    )

    obj_new_product = TypeProduct(id, name, description)
    status, message = services.obj_manager_product.add_product(obj_new_product, await services.obj_logic.convert_uploadfile_to_numpy(images))
    if not status:
        return { "success": False, "message": message}
    return { "success": True}
       
   