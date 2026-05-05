import {fetchGet,fetchGetSendData} from "./common_value.js";

const add_product = document.getElementById("add-product");
const overlay_new_product =  document.getElementById("overlay-new-product");
const close_add_product = document.getElementById("close-add-product");
const form_add_new_product = document.getElementById("form-add-new-product");
const previewImg = document.getElementById("previewImg");
const imageInput = document.getElementById("imageInput");
const preview_box = document.querySelector(".preview-box");
const table_product_list = document.getElementById("table-product-list");

close_add_product.addEventListener("click", function() {
    overlay_new_product.style.display = "none";
    console.log("Close add new product");
});
add_product.addEventListener("click",function() {
    console.log("Add new product clicked");
    UpDateTable();
});
async function UpDateTable(){
    overlay_new_product.style.display = "flex";
    let get_data_product = await fetchGet("/product");
    console.log(get_data_product);
    table_product_list.innerHTML = "";
    createDataShowTable(get_data_product);
}


form_add_new_product.addEventListener("submit", function(e) {
    e.preventDefault();
    console.log("Form submitted");
    let formData = new FormData(form_add_new_product);
    console.log(formData);
    let id = formData.get("id");
    // let name = formData.get("name");
    // let descripttion = formData.get("description");
    //console.log("id"+id,"name", name,"descripttion",descripttion);
    if (!isValidId(id)) {
        alert("ID không hợp lệ. Vui lòng nhập số nguyên dương.");
        return;
    }
    fetch(form_add_new_product.action, {
      method: "POST",
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data?.success == true) {
        UpDateTable();
        alert("Lưu thành công sản phẩm mới!");
      }   
      else{
            if (data?.message == "ErrorIDExists") {alert("Loại sản phẩm đã tồn tại trong cơ sở dữ liệu");   }
            else if (data?.message == "ErrorDataIncorect") {alert("Lỗi dữ liệu đầu vào.");}
            else if (data?.message == "ErroDataIncorectID") {alert("ID phải là số nguyên dương.");}
            else {alert("Lưu không thành công!");}
      }
    })
    .catch(err => {
      console.error(err);
      alert("Lỗi kết nối server!");
    });
});

function isValidId(id) {
    return /^[0-9]+$/.test(String(id));
}

imageInput.addEventListener("change", function(e) {
    const file = this.files[0];
    if (!file){
        return;
    }
    if (!file.type.startsWith("image/")) {
        alert("Vui lòng chọn file ảnh!");
        this.value = "";
        previewImg.style.display = "none";
        preview_box.style.display = "none";
        return;
    }
    const reader = new FileReader();
       reader.onload = function (e) {
        previewImg.src = e.target.result;
        previewImg.style.display = "block";
        preview_box.style.display = "block";
    };
    reader.readAsDataURL(file);
});

function createDataShowTable(data) {
    data?.data.forEach((item, index) => {
        // console.log("index", index, "item", item);
        let row = document.createElement("tr");
        // ID
        let cellId = document.createElement("td");
        cellId.textContent = item.id; // phải là item.id chứ không phải data.id

        // Name
        let cellName = document.createElement("td");
        cellName.textContent = item.name;

        // Description
        let cellDesc = document.createElement("td");
        cellDesc.textContent = item.description || "";

        // Image
        let cellImg = document.createElement("td");
        if(item.image_src){ // nếu có trường image
            let img = document.createElement("img");
            img.src = item.image_src; // đường dẫn ảnh
            img.alt = item.name || "Ảnh sản phẩm";
            img.style.width = "100px"; // chỉnh kích thước nhỏ vừa
            img.style.height = "auto";
            cellImg.appendChild(img);
        } else {
            cellImg.textContent = "Chưa có ảnh";
        }
        // Action buttons
        let cellAction = document.createElement("td");
        let btn  = document.createElement("button");
        btn.textContent = "Xóa sản phẩm"; // an toàn hơn innerHTML
        btn.classList.add("btn_erase");
        cellAction.appendChild(btn);
        btn.addEventListener("click",async ()=>{
            let status_erase = await fetchGetSendData("/product/erase_product",{"ID_Erase":item.id});
            if (status_erase?.success){
                console.log("Xóa thành công ",item.id);
            }
            else{
                let message = status_erase?.message; 
                if (message == "ErroEmpytyData"){
                    console.log("Danh sách hiện tại đang rỗng không thể xóa được");
                }
                else if (message ==  "ErroNoFind"){
                    console.log("Không tìm thấy ID để xóa");
                }
                else {
                    console.log("Lỗi gửi dữ liệu");
                }
            }
            status_erase?.message 
            row.innerHTML = "";
            return;
            
        });
        // Append cells to row
        row.appendChild(cellId);
        row.appendChild(cellName);
        row.appendChild(cellDesc);
        row.appendChild(cellImg);
        row.appendChild(cellAction);
        // Append row to table
        table_product_list.appendChild(row);
    });

}
