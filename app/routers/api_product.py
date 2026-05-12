from fastapi import APIRouter, Form, File, UploadFile,Query,Depends
from app.core.dependencies import get_services
from app.container import ServiceContainer
from app.model import Product

router = APIRouter(
    prefix="/product",
    tags=["Product"]
)

@router.get("/get_inf_product")
def get_product(services: ServiceContainer = Depends(get_services)):
    data = services.obj_manager_product.get_to_dict_arr_path_src()
    select_product = services.obj_choose_product.get_choose_product()
    # print(data)
    return { "success": True, "data": data.data,"current_option":select_product.data}

@router.get("/select_product_new")
def select_product_new(services: ServiceContainer = Depends(get_services),ID_Choose:int = Query(...,description="San pham chon")):
    print(ID_Choose)
    result = services.obj_choose_product.set_choose_product(ID_Choose)
    # print(data)
    return {"success": True} if result.ok else {"success": False}
    
@router.get("/")
def list_product(services: ServiceContainer = Depends(get_services)):
    data = services.obj_manager_product.get_to_dict_arr_path_src()
    print("data.data",data.data)
    return { "success": True, "data": data.data}



@router.get("/erase_product")
def erase_product(services: ServiceContainer = Depends(get_services),ID_Erase:int = Query(...,description= "Xoa San Pham")):
    result  = services.obj_manager_product.delete_product(ID_Erase)
    if not result.ok:
        return {"success":False,"message":result.message()}
    else:
        result = services.obj_choose_product.get_choose_product()
        if result.data == ID_Erase:
            print("Xóa đúng phần tử đang chọn nên sé reset cái chọn bằng -1 để xóa thành công")
            services.obj_choose_product.reset_choose_product()
        return { "success": True,"message":"Xóa thành công sản phẩm"}



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
    obj_new_product = Product(id, name, description)
    result  = services.obj_manager_product.add_product(obj_new_product, await services.obj_logic.convert_uploadfile_to_numpy(images))
    if not result.ok:
        return { "success": False, "message": result.message()}
    return { "success": True}
       
   