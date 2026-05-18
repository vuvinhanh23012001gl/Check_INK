from fastapi import APIRouter, Form, File, UploadFile,Query,Depends
from app.core.dependencies import get_services
from app.container import ServiceContainer
from app.model import Product
from app.utils import Tool_OpenCv2
router = APIRouter(
    prefix="/product",
    tags=["Product"]
)

@router.get("/get_inf_product")
def get_product(services: ServiceContainer = Depends(get_services)):
    data = services.obj_products_service.get_to_dict_arr_path_src()
    select_product = services.obj_choose_product.get_choose_product()
    print("get_inf_product",data)
    return { "success": True, "data": data.data,"current_option":select_product.data}

@router.get("/select_product_new")
def select_product_new(services: ServiceContainer = Depends(get_services),ID_Choose:int = Query(...,description="San pham chon")):
    print(ID_Choose)
    result = services.obj_choose_product.set_choose_product(ID_Choose)
    # print(data)
    return {"success": True} if result.ok else {"success": False}
    
@router.get("/")
def list_product(services: ServiceContainer = Depends(get_services)):
    data = services.obj_products_service.get_to_dict_arr_path_src()
    print("data.data",data.data)
    return { "success": True, "data": data.data}



@router.get("/erase_product")
def erase_product(
    services: ServiceContainer = Depends(get_services),
    ID_Erase: int = Query(..., description="Xoa San Pham")
):
    result = services.obj_products_service.delete_product(ID_Erase)
    if result.ok:
        if services.obj_choose_product.is_choose_product(ID_Erase):
            services.obj_choose_product.reset_choose_product()
    return {
        "success": result.ok,
        "message": result.message()
    }


   
@router.post("/add")
async def add_product(
    services: ServiceContainer = Depends(
        get_services
    ),
    id: int = Form(...),
    name: str = Form(...),
    description: str = Form(""),
    images: UploadFile | None = File(None)
):
    img_np = None
    if images:
        contents = await images.read()
        img_np = (
            Tool_OpenCv2.bytes_to_ndarray(
                contents
            )
        )
    product = Product(
        id=id,
        name=name,
        description=description
    )
    result = (
        services.obj_products_service
        .add_product(
            product=product,
            img=img_np
        )
    )

    return{ "success": result.ok , "message": result.message()}