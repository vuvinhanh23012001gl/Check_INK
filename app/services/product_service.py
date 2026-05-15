# =========================
# FILE: product_service.py
# =========================

import cv2
import datetime
import numpy as np
from app.model import Product
from app.repository import (
    ProductRepository
)
from app.utils import (
    Tool_OpenCv2,Folder
)
from app.core import (
    Result,
    ErrorCode
)


class ProductService:

    def __init__(
        self,
        repository: ProductRepository,
    ):

        self.repository = repository

       
    
        self.products = (
            self._load_products()
        )

    # =========================
    # LOAD
    # =========================

    def _load_products(self):

        data_products = (
            self.repository.load_products()
        )

        products = {}

        for product_id, item in data_products.items():

            sp = Product(
                id=item.get("id"),
                name=item.get("name"),
                description=item.get("description")
            )

            sp.created_at = item.get(
                "created_at"
            )

            sp.updated_at = item.get(
                "updated_at"
            )

            products[int(product_id)] = sp

        return products

    # =========================
    # SAVE
    # =========================

    def _save_products(self):

        self.repository.save_products(
            self.products
        )

    # =========================
    # GET PRODUCT
    # =========================

    def get_product_by_id(
        self,
        product_id
    ):

        product = self.products.get(
            product_id
        )

        if not product:

            return Result.Fail(
                ErrorCode.PRODUCT_NOT_FOUND
            )

        return Result.Ok(product)

    # =========================
    # GET ALL PRODUCT
    # =========================

    def get_all_products(self):

        return Result.Ok(
            list(self.products.values())
        )

    # =========================
    # ADD PRODUCT
    # =========================

    def add_product(
        self,
        product: Product,
        img=None
    ):

        result_find = (
            self.get_product_by_id(
                product.id
            )
        )

        if result_find.ok:

            return Result.Fail(
                ErrorCode.PRODUCT_ALREADY_EXISTED
            )

        # =====================
        # UPDATE TIME
        # =====================

        time_now = str(
            datetime.datetime.now()
        )

        product.created_at = time_now

        product.updated_at = time_now

        # =====================
        # IMAGE PATH
        # =====================

        path_img = (
            self.repository
            .get_product_image_path(
                product.id
            )
        )

        # =====================
        # SAVE IMAGE
        # =====================

        if isinstance(
            img,
            np.ndarray
        ):

            success = (
                Tool_OpenCv2.save_image(
                    img,
                    str(path_img)
                )
            )

        else:

            img_black = (
                Tool_OpenCv2
                .create_black_image(
                    1920,
                    1200
                )
            )

            success = (
                Tool_OpenCv2.save_image(
                    img_black,
                    str(path_img)
                )
            )

        if not success:

            return Result.Fail(
                ErrorCode.PRODUCT_SAVE_IMAGE_FAIL
            )

        # =====================
        # CREATE ROI FOLDER
        # =====================

        self.repository.create_roi_folder(
            product.id
        )

        # =====================
        # SAVE PRODUCT
        # =====================

        self.products[
            product.id
        ] = product

        self._save_products()

        return Result.Ok(product)

    # =========================
    # DELETE PRODUCT
    # =========================

    def delete_product(
        self,
        product_id
    ):

        result_find = (
            self.get_product_by_id(
                product_id
            )
        )

        if not result_find.ok:

            return Result.Fail(
                ErrorCode.PRODUCT_NOT_FOUND
            )

        product = result_find.data

        # =====================
        # DELETE IMAGE
        # =====================

        path_img = (
            self.repository
            .get_product_image_path(
                product.id
            )
        )

        Tool_OpenCv2.delete_image(
            str(path_img)
        )

        # =====================
        # DELETE ROI FOLDER
        # =====================

        self.repository.delete_roi_folder(
            product.id
        )

        # =====================
        # DELETE PRODUCT
        # =====================

        del self.products[
            product.id
        ]

        self._save_products()

        return Result.Ok()

    # =========================
    # ADD ROI IMAGE
    # =========================

    def add_roi_image(
        self,
        product_id,
        img
    ):

        result_find = (
            self.get_product_by_id(
                product_id
            )
        )

        if not result_find.ok:

            return Result.Fail(
                ErrorCode.PRODUCT_NOT_FOUND
            )

        if img is None:

            return Result.Fail(
                ErrorCode.PRODUCT_IMAGE_EMPTY
            )

        product = result_find.data

        # =====================
        # ROI FOLDER
        # =====================

        folder_roi = (
            self.repository
            .create_roi_folder(
                product.id
            )
        )

        list_file = (
            self.repository
            .get_roi_files(
                product.id
            )
        )

        # =====================
        # CREATE FILE NAME
        # =====================

        new_index = len(list_file)

        path_file = (
            folder_roi /
            f"coordinates_{new_index}.jpg"
        )

        # =====================
        # SAVE ROI IMAGE
        # =====================

        success = cv2.imwrite(
            str(path_file),
            img
        )

        if not success:

            return Result.Fail(
                ErrorCode.PRODUCT_SAVE_IMAGE_FAIL
            )

        return Result.Ok(
            str(path_file)
        )
    
    def update_product(
        self,
        product_id,
        name=None,
        description=None
    ):

        result_find = (
            self.get_product_by_id(
                product_id
            )
        )

        if not result_find.ok:

            return Result.Fail(
                ErrorCode.PRODUCT_NOT_FOUND
            )

        product = result_find.data

        # =====================
        # UPDATE DATA
        # =====================

        if name is not None:

            product.name = name

        if description is not None:

            product.description = description

        # =====================
        # UPDATE TIME
        # =====================

        product.updated_at = str(
            datetime.datetime.now()
        )

        # =====================
        # SAVE
        # =====================

        self._save_products()

        return Result.Ok(product)
    def get_arr_path_img_roi_product_by_id(
        self,
        product_id
    ):

        print(
            "---- Vào hàm Lấy danh sách ảnh ROI của sản phẩm ---"
        )

        # =====================
        # CHECK PRODUCT
        # =====================

        result_find = (
            self.get_product_by_id(
                product_id
            )
        )

        if not result_find.ok:

            print("Không tìm thấy ID")

            print(
                "---- Hết hàm lấy danh sách ảnh sp ---"
            )

            return Result.Fail(
                ErrorCode.PRODUCT_NOT_FOUND
            )

        # =====================
        # ROI FOLDER
        # =====================

        path_folder_roi_product = (
            self.repository
            .get_roi_folder(
                product_id
            )
        )

        # =====================
        # GET ROI FILES
        # =====================

        list_name_file = (
            self.repository
            .get_roi_files(
                product_id
            )
        )

        if len(list_name_file) == 0:

            print(
                f"Chưa có ảnh ROI cho sản phẩm id={product_id}"
            )

            print(
                "---- Hết hàm lấy danh sách ảnh sp ---"
            )

            return Result.Ok([])

        # =====================
        # CREATE WEB PATH
        # =====================

        arr_path_img_roi = []

        for file_name in list_name_file:

            full_path = (
                path_folder_roi_product
                / file_name
            )

            # =====================
            # WEB PATH
            # =====================

            path_poxis = (
                Folder
                .get_parts_from_bottom(
                    full_path,
                    levels=4
                )
            )

            arr_path_img_roi.append(
                str(path_poxis)
            )

        print(
            "danh sách ảnh ROI:",
            arr_path_img_roi
        )

        print(
            "---- Hết hàm lấy danh sách ảnh sp ---"
        )

        return Result.Ok(
            arr_path_img_roi
        )
    
    
    def get_to_dict_arr_path_src(
        self
    ):

        """
        Trả về danh sách dict thông tin
        sản phẩm + đường dẫn ảnh web
        """

        arr_product = []

        for product in self.products.values():

            dict_out = (
                product.to_dict()
            )

            # =====================
            # IMAGE PATH
            # =====================

            path_save_img = (
                self.repository
                .get_product_image_path(
                    product.id
                )
            )

            path_poxis = (
                self.repository.folder
                .get_parts_from_bottom(
                    path_save_img,
                    levels=3
                )
            )

            dict_out["image_src"] = (
                str(path_poxis)
            )

            arr_product.append(
                dict_out
            )

        return Result.Ok(
            arr_product
        )
    
