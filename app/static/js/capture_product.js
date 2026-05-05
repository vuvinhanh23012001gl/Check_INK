import {scroll_content,logSocket,postData,clearn_div,video_product,wrap_canvas,get_camera_connection,show_video_product}from "./common_value.js";

const paner_capture_product = document.getElementById("paner-capture-product");
const btn_function_capture_product = document.getElementById("header-ul-li-capture-product");
const btn_add_frame = document.getElementById("btn-add-frame");
const anonymous =  document.getElementById("anonymous");
const log_box   = document.getElementById("log-box");
const exit_add_capture_product  = document.getElementById("exit-add-capture-product");

 
let divCreateList = []; // biến toàn cục luu mang data gửi lên
let max_point_run ={}
max_point_run.x =  0;
max_point_run.y =  0;
max_point_run.k = 0;



exit_add_capture_product.addEventListener("click",()=>{
      fetch('/captureproduct/exit')
      .then(response => {
          console.log("responsd")
          if (response.redirected) {
              window.location.href = response.url;
          } else {
              response.json().then(data => {
                  window.location.href = data.redirect_url;
              });
          }
      });
});


logSocket.on("CaptureProduct", (data) => {
    console.log("---Mở SoketIO Capture Product---");
    log_box.innerHTML += `<p>${data?.msg}</p>`;
});

btn_function_capture_product.addEventListener("click",function(){       
        console.log("Bạn vừa click vào chụp ảnh sản phẩm");
        paner_capture_product.classList.add("active");
        video_product.style.width = "1365.33px";
        video_product.style.height = "1024px";
        video_product.style.objectFit = "contain";   // QUAN TRỌNG
        video_product.style.display = "flex";
        wrap_canvas.style.display = "none";
        write_log_capture_clear("✅ Nhấn \"Thêm master\" -> \"Ảnh master\" để mở video chụp ảnh.")
        postData("/captureproduct", {"status": "UI_Capture"}).then(data => {
            if (data?.status == "ok"){
                renderMaster(data);
               
            }
        });
        if(!get_camera_connection()){ write_log_capture_clear("❌ Camera hiện tại chưa kết nối.\n✅ Hãy kết nối với Camera."); return;}
    
});

function renderMaster(data) {
        if (!data){
            write_log_capture_clear("❌Lỗi Server tắt đi bật lại phần mềm !");
            return;
        }
        if (data?.status == "error"){
            write_log_capture_clear(`Lỗi từ server:${data?.message}`)
            return;
        }
        create_table_product(data);
        scroll_content.innerHTML = "";
        const imgList = data?.path_arr_img;
        const list_point  = data?.arr_point;
      
        if(!imgList||!list_point){write_log_capture_clear("✔️ Loại sản phẩm mới chưa cấu hình chụp.\n✅ Hãy Chụp sản phẩm.");return;}
        if (!imgList || imgList.length === 0) {write_log_capture_clear("✔️Hệ thống chưa có ảnh master nào.\n✅ Hãy bắt đầu chụp ảnh và cấu hình");return}
        console.log("Danh sách điểm:", list_point);
        console.log("Danh sách ảnh:", imgList);
        imgList.forEach((imgPath, index) => {
                const div_create = document.createElement("div");
                div_create.className = "div-index-img-mater";
                const h_create = document.createElement("p");
                h_create.innerText = `Ảnh master ${index}`;
                h_create.className = "p-index-img-master";

                const img = document.createElement("img");
                img.src = `${imgPath}?t=${Date.now()}`;  // dam bao  goi moi nhat
                img.alt = "Ảnh sản phẩm";
                img.style.width = "200px";
                img.style.margin = "10px";

                div_create.appendChild(img);
                div_create.appendChild(h_create);
                scroll_content.appendChild(div_create);
                divCreateList.push(div_create);
                div_create.addEventListener("click",function(){
                        clearn_div(divCreateList);
                        div_create.classList.add("div_click");
                        video_product.src =  `${imgPath}?t=${Date.now()}`;
                        video_product.style.width = "1365.33px";
                        video_product.style.height = "1024px";
                        video_product.style.objectFit = "contain";   // QUAN TRỌNG
                        video_product.style.display = "block";
                        const index = Array.from(scroll_content.children).indexOf(this);
                        console.log("Ảnh master đang chỉ tới là:",index);
                        create_table_controler(index);

                    //   const input_x = document.getElementById(`input-x-${index}`);input_x.type = "number";
                    //   const input_y = document.getElementById(`input-y-${index}`);input_y.type = "number";
                    //   const input_k = document.getElementById(`input-k-${index}`);input_k.type = "number";
                    //   const btn_increase_x = document.getElementById(`btn-inc-x-${index}`);
                    //   const btn_decrease_x = document.getElementById(`btn-dec-x-${index}`);
                    //   const btn_increase_y = document.getElementById(`btn-inc-y-${index}`);
                    //   const btn_decrease_y = document.getElementById(`btn-dec-y-${index}`);
                    //   const btn_increase_z = document.getElementById(`btn-inc-z-${index}`);
                    //   const btn_decrease_z = document.getElementById(`btn-dec-z-${index}`);
                    //   const btn_increase_k = document.getElementById(`btn-inc-k-${index}`);
                    //   const btn_decrease_k = document.getElementById(`btn-dec-k-${index}`);
                    //   const btn_run          = document.getElementById(`btn-run-${index}`);
                    //   const btn_capture      = document.getElementById(`btn-capture-${index}`);
                    //   const btn_erase_master = document.getElementById(`btn-erase-master-${index}`);
                    //   if (
                    //       list_point[index]?.x == null ||
                    //       list_point[index]?.y == null ||
                    //       list_point[index]?.z == null ||
                    //       list_point[index]?.brightness == null
                    //     ) 
                    //           {
                    //             input_x.value = list_point[index]?.x ?? 0;
                    //             input_y.value = list_point[index]?.y ?? 0;
    
                    //             input_k.value = list_point[index]?.brightness ?? 0;
                    //           } else {
                    //             input_x.value = list_point[index].x;
                    //             input_y.value = list_point[index].y;
                    //             input_k.value = list_point[index].brightness;
                    //           }
                             
                    //   // Khai báo các handler (function reference)
                    //   const handleIncreaseX = () => HandleClickBtnIncrease_X(input_x, Max_X, input_x.value, input_y.value, input_z.value, input_k.value);
                    //   const handleDecreaseX = () => HandleClickBtnDecrease_X(input_x, Max_X, input_x.value, input_y.value, input_z.value, input_k.value);

                    //   const handleIncreaseY = () => HandleClickBtnIncrease_Y(input_y, Max_Y, input_x.value, input_y.value, input_z.value, input_k.value);
                    //   const handleDecreaseY = () => HandleClickBtnDecrease_Y(input_y, Max_Y, input_x.value, input_y.value, input_z.value, input_k.value);

                    //   const handleIncreaseZ = () => HandleClickBtnIncrease_Z(input_z, Max_Z, input_x.value, input_y.value, input_z.value, input_k.value);
                    //   const handleDecreaseZ = () => HandleClickBtnDecrease_Z(input_z, Max_Z, input_x.value, input_y.value, input_z.value, input_k.value);

                    //   const handleIncreaseK = () => HandleClickBtnIncrease_K(input_k, Max_K, input_x.value, input_y.value, input_z.value, input_k.value);
                    //   const handleDecreaseK = () => HandleClickBtnDecrease_K(input_k, Max_K, input_x.value, input_y.value, input_z.value, input_k.value);

                    //   const handleRun       = () => HandleClickBtnRun(input_x.value, input_y.value, input_z.value, input_k.value);
                    //   const handleCapture   = () => HandleClickBtnCapture(index, input_x.value, input_y.value, input_z.value, input_k.value);
                    //   const handleErase     = () => HandleClickBtnEraseMaster(index);

                    //   // Gắn event (trước khi add thì remove trước để tránh trùng)
                    //   btn_increase_x.removeEventListener("click", handleIncreaseX);
                    //   btn_increase_x.addEventListener("click", handleIncreaseX);

                    //   btn_decrease_x.removeEventListener("click", handleDecreaseX);
                    //   btn_decrease_x.addEventListener("click", handleDecreaseX);

                    //   btn_increase_y.removeEventListener("click", handleIncreaseY);
                    //   btn_increase_y.addEventListener("click", handleIncreaseY);

                    //   btn_decrease_y.removeEventListener("click", handleDecreaseY);
                    //   btn_decrease_y.addEventListener("click", handleDecreaseY);

                    //   btn_increase_z.removeEventListener("click", handleIncreaseZ);
                    //   btn_increase_z.addEventListener("click", handleIncreaseZ);

                    //   btn_decrease_z.removeEventListener("click", handleDecreaseZ);
                    //   btn_decrease_z.addEventListener("click", handleDecreaseZ);

                    //   btn_increase_k.removeEventListener("click", handleIncreaseK);
                    //   btn_increase_k.addEventListener("click", handleIncreaseK);

                    //   btn_decrease_k.removeEventListener("click", handleDecreaseK);
                    //   btn_decrease_k.addEventListener("click", handleDecreaseK);

                    //   btn_run.removeEventListener("click", handleRun);
                    //   btn_run.addEventListener("click", handleRun);

                    //   btn_capture.removeEventListener("click", handleCapture);
                    //   btn_capture.addEventListener("click", handleCapture);

                    //   btn_erase_master.removeEventListener("click", handleErase);
                    //   btn_erase_master.addEventListener("click", handleErase);
                });
        });
}



function create_table_product(data) {
       console.log("-----------------------------------------------------------Ok---------------------");
       console.log(data)
       const tbody = document.querySelector(".product-table tbody");
       if (!tbody){
        console.log("Bảng không tồn tại");
        return;
       }
       if (!data){
            log_box.innerHTML = "Bạn chưa chọn loại sản phẩm.Hãy nhấn \"Chọn loại sản phẩm\"";
            return;
       }
       tbody.innerHTML = "";
       let log = data?.inf_product;
        console.log("Dữ liệu nhận được là ",log);
      //  let id =  log?.list_id[0]; //Id chua can de hien thi
       let name   = log?.name;
       let x = log?.xyz[0];
       max_point_run.x = x;
       let y = log?.xyz[1];
       max_point_run.y = y;
       let k = 100;
       max_point_run.k = k;
       console.log(name)
       console.log(x)
       console.log(y)
       console.log(k)
      const row = document.createElement("tr");
      row.innerHTML =  
      `<td>${name}</td>
       <td>${x}</td>
       <td>${y}</td>
       <td>${k}</td>
      `;
      tbody.appendChild(row);
};



btn_add_frame.addEventListener("click",function(){
    write_log_capture_clear("");
    console.log("Bạn vừa click vào thêm khung chụp sản phẩm");
    console.log("Đã nhấn vào nút thêm master");
    const div_create = document.createElement("div");
    div_create.className = "div-index-img-mater";

    const h_create = document.createElement("p");
    h_create.innerText = `Ảnh master`;
    h_create.className = "p-index-img-master";

    const img = document.createElement("img");
    img.src = "./static/img/plus.png";
    img.alt = "Click vào đây để chụp ảnh";
    img.style.padding = "35px";
    img.style.width = "200px";
    
    div_create.appendChild(img);
    div_create.appendChild(h_create);
    scroll_content.appendChild(div_create); 
    div_create.addEventListener("click", function() {

        show_video_product();
        console.log("Mở camera để chụp ảnh master");
        const index = Array.from(scroll_content.children).indexOf(this);
        console.log("Index của khung master vừa thêm:", index);
        create_table_controler(index);

            const input_x = document.getElementById(`input-x-${index}`);input_x.type = "number";
            const input_y = document.getElementById(`input-y-${index}`);input_y.type = "number";
            const input_k = document.getElementById(`input-k-${index}`);input_k.type = "number";
            

            input_x.value = 1;  // vi du
            input_y.value = 1;
            input_k.value = 1;

            const btn_increase_x = document.getElementById(`btn-inc-x-${index}`);
            const btn_decrease_x = document.getElementById(`btn-dec-x-${index}`);
            const btn_increase_y = document.getElementById(`btn-inc-y-${index}`);
            const btn_decrease_y = document.getElementById(`btn-dec-y-${index}`);
            const btn_increase_k = document.getElementById(`btn-inc-k-${index}`);
            const btn_decrease_k = document.getElementById(`btn-dec-k-${index}`);

            const btn_run          = document.getElementById(`btn-run-${index}`);
            const btn_capture      = document.getElementById(`btn-capture-${index}`);
            const btn_erase_master = document.getElementById(`btn-erase-master-${index}`);

            //     // Khai báo các handler (function reference)
            // const handleIncreaseX = () => HandleClickBtnIncrease_X(input_x, Max_X, input_x.value, input_y.value, input_z.value, input_k.value);
            // const handleDecreaseX = () => HandleClickBtnDecrease_X(input_x, Max_X, input_x.value, input_y.value, input_z.value, input_k.value);

            // const handleIncreaseY = () => HandleClickBtnIncrease_Y(input_y, Max_Y, input_x.value, input_y.value, input_z.value, input_k.value);
            // const handleDecreaseY = () => HandleClickBtnDecrease_Y(input_y, Max_Y, input_x.value, input_y.value, input_z.value, input_k.value);

            // const handleIncreaseK = () => HandleClickBtnIncrease_K(input_k, Max_K, input_x.value, input_y.value, input_z.value, input_k.value);
            // const handleDecreaseK = () => HandleClickBtnDecrease_K(input_k, Max_K, input_x.value, input_y.value, input_z.value, input_k.value);

            // const handleRun       = () => HandleClickBtnRun(input_x.value, input_y.value, input_z.value, input_k.value);
            const handleCapture   = () => HandleClickBtnCapture(index, input_x.value, input_y.value, input_k.value);
            // const handleErase     = () => HandleClickBtnEraseMaster(index);

            // Gắn event (trước khi add thì remove trước để tránh trùng)
            // btn_increase_x.removeEventListener("click", handleIncreaseX);
            // btn_increase_x.addEventListener("click", handleIncreaseX);

            // btn_decrease_x.removeEventListener("click", handleDecreaseX);
            // btn_decrease_x.addEventListener("click", handleDecreaseX);

            // btn_increase_y.removeEventListener("click", handleIncreaseY);
            // btn_increase_y.addEventListener("click", handleIncreaseY);

            // btn_decrease_y.removeEventListener("click", handleDecreaseY);
            // btn_decrease_y.addEventListener("click", handleDecreaseY);

            // btn_increase_k.removeEventListener("click", handleIncreaseK);
            // btn_increase_k.addEventListener("click", handleIncreaseK);

            // btn_decrease_k.removeEventListener("click", handleDecreaseK);
            // btn_decrease_k.addEventListener("click", handleDecreaseK);

            // btn_run.removeEventListener("click", handleRun);
            // btn_run.addEventListener("click", handleRun);

            btn_capture.removeEventListener("click", handleCapture);
            btn_capture.addEventListener("click", handleCapture);

            // btn_erase_master.removeEventListener("click", handleErase);
            // btn_erase_master.addEventListener("click", handleErase);

    });
        
});

function HandleClickBtnCapture(index,x,y,k){
    console.log("-Đã nhấn vào chụp-");
    postData("/captureproduct/capture", { "status": "200OK","index":index,"x":x,"y":y,"k":k})
    .then(data => {
        if (data?.status == "ok"){
            renderMaster(data);
            write_log_capture_clear("✔️ Chụp ảnh thành công \n✅ Hãy chụp điểm tiếp theo.");
        }
    });
}



function create_table_controler(index){

      anonymous.innerHTML = "";
      anonymous.appendChild(createInputRow("Nhập X","Nhập X > 0", `input-x-${index}`),);
      anonymous.appendChild(createInputRow("Nhập Y", "Nhập Y > 0", `input-y-${index}`));
      anonymous.appendChild(createInputRow("Mức sáng", "Nhập độ sáng > 0",`input-k-${index}`));

      anonymous.appendChild(createButtonRow([
          {id: `btn-inc-x-${index}`, icon: "./static/img/add1.png", alt: "Tăng X", text: "Tăng X"},
          {id: `btn-dec-x-${index}`, icon: "./static/img/minus.png", alt: "Giảm X", text: "Giảm X"}
      ]));

      anonymous.appendChild(createButtonRow([
          {id: `btn-inc-y-${index}`, icon: "./static/img/add1.png", alt: "Tăng Y", text: "Tăng Y"},
          {id: `btn-dec-y-${index}`, icon: "./static/img/minus.png", alt: "Giảm Y", text: "Giảm Y"}
      ]));

      anonymous.appendChild(createButtonRow([
          {id: `btn-inc-k-${index}`, icon: "./static/img/add1.png", alt: "Tăng ánh sáng", text: "Tăng ánh sáng"},
          {id: `btn-dec-k-${index}`, icon: "./static/img/minus.png", alt: "Giảm ánh sáng", text: "Giảm ánh sáng"}
      ]));

      anonymous.appendChild(createButtonRow([
          {id: `btn-run-${index}`, icon: "./static/img/check.png", alt: "Chạy", text: "Chạy"},
          {id: `btn-capture-${index}`, icon: "./static/img/camera.png", alt: "Chụp", text: "Chụp"},
          {id: `btn-erase-master-${index}`, icon: "./static/img/running.png", alt: "Xóa Master", text: "Xóa Master này"}
      ]));                  
      // Hiện div anonymous
      anonymous.style.display = "block";
}



function createInputRow(labelText, placeholder, id = null) {
    const div = document.createElement("div");
    div.className = "Alight-items-x";

    const label = document.createElement("label");
    label.innerText = labelText;
    if (id) label.setAttribute("for", id);

    const input = document.createElement("input");
    input.type = "number";
    input.placeholder = placeholder;
    if (id) input.id = id;   // ✅ gán id cho input
    input.className = "input-value-xyk";
    div.appendChild(label);
    div.appendChild(input);

    return div;
}



function createButtonRow(buttons) {
    const div = document.createElement("div");
    div.className = "Alight-items-x";

    buttons.forEach(btn => {
        const button = document.createElement("button");
        button.className = "btn";
        if (btn.id) button.id = btn.id;   // ✅ gán id cho button

        const img = document.createElement("img");
        img.src = btn.icon;
        img.alt = btn.alt;

        button.appendChild(img);
        button.append(` ${btn.text}`);
        div.appendChild(button);
    });

    return div;
}


function HandleClickBtnIncrease_X(element,max_element,input_x_value,input_y_value,input_z_value,input_k_value){
       let status_check = CheckData(element,"X",input_x_value,max_element);
       if(status_check){
          console.log("input_x_value", input_x_value);
         element.value = parseInt(input_x_value) + 1;
         HandleClickBtnRun(element.value,input_y_value,input_z_value,input_k_value);
       }

}
function HandleClickBtnDecrease_X(element,max_element,input_x_value,input_y_value,input_z_value,input_k_value) {
    let new_value = parseInt(input_x_value) - 1;
    let status_check = CheckData(element,"X", new_value, max_element);
    if (status_check) {
        element.value = new_value; 
        HandleClickBtnRun(element.value,input_y_value,input_z_value,input_k_value);
    } else {
        element.value = 0; 
    }
}   

function HandleClickBtnIncrease_Y(element,max_element,input_x_value,input_y_value,input_z_value,input_k_value){
       let status_check = CheckData(element,"Y",input_y_value,max_element);
       if(status_check){
         element.value = parseInt(input_y_value) + 1;
          HandleClickBtnRun(input_x_value,element.value,input_z_value,input_k_value);
       }
}
function HandleClickBtnDecrease_Y(element,max_element,input_x_value,input_y_value,input_z_value,input_k_value){
    let new_value = parseInt(input_y_value) - 1;
    let status_check = CheckData(element,"Y", new_value, max_element);
    if (status_check) {
        element.value = new_value; 
        HandleClickBtnRun(input_x_value,element.value,input_z_value,input_k_value);
    } else {
        element.value = 0; 
    }
}

function HandleClickBtnIncrease_K(element,max_element,input_x_value,input_y_value,input_z_value,input_k_value){
        let status_check = CheckData(element,"K",input_k_value,max_element);
        if(status_check){
          element.value = parseInt(input_k_value) + 1;
           HandleClickBtnRun(input_x_value,input_y_value,input_z_value,element.value);
    } 
}
function HandleClickBtnDecrease_K(element,max_element,input_x_value,input_y_value,input_z_value,input_k_value){
    let new_value = parseInt(input_k_value) - 1;
    let status_check = CheckData(element,"K", new_value, max_element);
    if (status_check) {
        element.value = new_value; 
        HandleClickBtnRun(input_x_value,input_y_value,input_z_value,element.value);
    } else {
        element.value = 0; 
    }
}

function CheckData(element,str_name, data, value_max) {
    if (str_name == null || data == null || value_max == null ||element.value == ""||element.value == null ) {
        console.log(`⚠️ Dữ liệu "${str_name}" không có giá trị`);
        log_box.innerHTML = `⚠️ Dữ liệu "${str_name}" không có giá trị`;
        element.value = 0;
        return false;
    }
    if (data < 0) {
        console.log(`❌ Giá trị "${str_name}" phải lớn hơn hoặc bằng 0`);
        log_box.innerHTML = `❌ Giá trị "${str_name}" phải lớn hơn hoặc bằng 0`;
        element.value = 0;
        console.log("vao day");
        return false;
    }

    if (data >= value_max) {
        console.log(`❌ Giá trị "${str_name}" phải nhỏ hơn hoặc bằng ${value_max}`);
        log_box.innerHTML = `❌ Giá trị "${str_name}" phải nhỏ hơn hoặc bằng ${value_max}`;
         element.value = value_max;
        return false;
    }
    console.log("data",data);
    console.log(`✅ Giá trị ${str_name} hợp lệ`);
    log_box.innerHTML = `✅ Giá trị ${str_name} hợp lệ`;
    return true;
}


function write_log_capture_clear(text){
    log_box.textContent = text;
}

function write_log_capture_append(text){
    log_box.textContent += text;
}
