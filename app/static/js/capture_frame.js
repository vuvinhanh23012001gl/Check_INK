// import {scroll_content,SocketLog,postData,clearn_div,video_product,wrap_canvas,get_camera_connection,show_video_product}from "./common_value.js"; co scroll
import {SocketLog,postData,clearn_div,video_product,wrap_canvas,get_camera_connection,show_video_product}from "./common_value.js";

console.log("-- Mở File capture hình ảnh thành công --");
const paner_capture_product = document.getElementById("paner-capture-product");
const btn_function_capture_product = document.getElementById("header-ul-li-capture-product");
const btn_add_frame = document.getElementById("btn-add-frame");
const btn_stream_video = document.getElementById("btn-stream-video");
const anonymous =  document.getElementById("anonymous");
const log_box   = document.getElementById("log-box");
const exit_add_capture_product  = document.getElementById("exit-add-capture-product");
const btn_add_point = document.getElementById("btn-add-point");
const scroll_container = document.querySelector(".scroll-container");
const btn_erase_frame =  document.getElementById("btn-erase-frame");
const btn_run_frame   = document.getElementById("btn-run-frame");
const btn_run_product = document.getElementById("btn-run-product");
let max_point_run ={}
max_point_run.x =  0;
max_point_run.y =  0;
max_point_run.z = 0;


let coordinate_after_taking_photo = {};
coordinate_after_taking_photo.x = -1;
coordinate_after_taking_photo.y = -1;
coordinate_after_taking_photo.z = -1;

const selected = {
    frame_id: -1,
    point_id: -1
};

let isSending = false; //Biến này giúp đợi  tránh làm cho gửi quá nhiều lần tới IAI
let  current_frame_box = null ; // Frame hiện tại đang đc click
let  id_product_selecting_now = null; //San pham dang chon



//Soket io
SocketLog.on("type_log_capture", (data) => {
    console.log("---Mở SoketIO Capture Product---");
    log_box.innerHTML += `<p>${data?.msg}</p>`;
});

// Action BTN
btn_stream_video.addEventListener("click",()=>{
     wrap_canvas.style.display = "none";
     console.log("đã nhấn nút Stream video");
     if(!get_camera_connection()){ write_log_capture_clear("❌ Camera hiện tại chưa kết nối.\n✅ Hãy kiểm tra kết nối.\n"); return;}
     show_video_product();
});


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



btn_add_point.addEventListener("click", () => {
    if (selected.frame_id == -1) {
        write_log_capture_clear("❌Hãy click vào frame trước khi thêm điểm");
        return;
    }
    // 🌟 THAY ĐỔI QUAN TRỌNG: Lấy ra đối tượng DOM mới nhất đang hiển thị trên màn hình
    const real_frame_box = document.querySelector(`.box-frame[data-frame-id="${selected.frame_id}"] .img-box`);
    
    if (!real_frame_box) {
        console.log("Không tìm thấy Frame thực tế trên giao diện!");
        return;
    }
    // Cập nhật lại biến global cho đúng chuẩn
    current_frame_box = real_frame_box; 

    let break_function = false;
    current_frame_box.querySelectorAll(".img-item").forEach((value, index) => {
        if (value.dataset.has_icon_add_new) {
            write_log_capture_clear("❌ Một Frame chỉ có một Point được thêm !");
            break_function = true;
        }
    });

    if (break_function) return;

    const box_frame = current_frame_box.querySelectorAll(".img-item");
    let arr_items_img_id = [];
    for (const i of box_frame) {
        arr_items_img_id.push(i.dataset.id);
    }
    
    let id_new = generateNewId(arr_items_img_id);
    let find_index_new = current_frame_box.querySelectorAll(".img-item").length; 
    
    let data_point = null;
    // 🌟 Truyền phần tử DOM thật vừa tìm được vào hàm tạo
    create_items_img(id_new, find_index_new, data_point, current_frame_box, selected.frame_id);
});



btn_function_capture_product.addEventListener("click",function(){       
        console.log("Click vào chụp ảnh sản phẩm");
        paner_capture_product.classList.add("active");
        video_product.style.width = "1365.33px";
        video_product.style.height = "1024px";
        video_product.style.objectFit = "contain";   // QUAN TRỌNG
        video_product.style.display = "flex";
        wrap_canvas.style.display = "none";
        // write_log_capture_clear("✅ Nhấn \"Thêm master\" -> \"Ảnh master\" để mở video chụp ảnh.")
        postData("/captureproduct", {"status": "UI_Capture"}).then(data => {
            console.log("Data Receive:",data.data);
            renderMaster(data?.data);
            // console.log("data moi vao",data?.data);
        });
});
        
               


function renderMaster(data) {
        scroll_container.innerHTML = "";
        process_table_product(data);
        create_img_items(data.data_point);
}

function create_img_items(points_and_box){
        // console.log("Data create_img_items",data?.data);
        // console.log("data đúng của product");
        // console.log("points_and_box",points_and_box);
        let index_frame = 0;
        for (const boxs in points_and_box){
            // console.log("boxs",boxs);
            let index_items = 0;
            let result_create_box = create_box(boxs,index_frame);
            let div_img_box = result_create_box.div_img_box;
            let div_box_frame = result_create_box.div_box_frame;
            //Kiểm tra xem cái nào đang chọn thì chọn nó.
            if (boxs == selected.frame_id){
                // console.log("Vẫn còn nha");
                div_box_frame.classList.add("box-frame-selected");
            }
            // console.log("frame_current",frame_current);
            index_frame++;
            for (const items in points_and_box[boxs]){
                // console.log("data nhan dc la",points_and_box[boxs][items]);
                // console.log("dsaddsdsadsds123",items,points_and_box[boxs][items]);
                let data_point =  points_and_box[boxs][items];
                create_items_img(items,index_items,data_point,div_img_box,boxs);
                index_items++;
            }
        }
}


function process_table_product(data) {
    //   console.log("process_table_product",data);
       const tbody = document.querySelector(".product-table tbody");
       if (!tbody){console.log("Bảng không tồn tại");
        return;
       }
       tbody.innerHTML = "";  
       let product = data?.product;
       let infor_iai = data?.infor_iai;
       let id = product?._id;
       id_product_selecting_now = id;  
       let name = `${id}.${product?._name}`;
       let x = infor_iai?.limit_x_max;
       max_point_run.x = x;
       let y = infor_iai?.limit_y_max;
       max_point_run.y = y;
       let z = infor_iai?.limit_z_max;
       max_point_run.z = z;
       console.log(`Sản phẩm ${id}:${name}, max X:${x}, max Y:${y}, max Z:${z}`);
    //    console.log(data)
    //    console.log(name)
    //    console.log(x)
    //    console.log(y)
    //    console.log(z)
      const row = document.createElement("tr");
      row.innerHTML =  
      `<td>${name}</td>
       <td>${x}</td>
       <td>${y}</td>
       <td>${z}</td>
      `;
      tbody.appendChild(row);
};




function generateNewId(arr){
    if (arr.length === 0){
        return 0;
    }
    return Math.max(...arr) + 1;
}

function container_driver(selected,Max_X,Max_Y,Max_Z,x=null,y=null,z=null){

                const input_x = document.getElementById(`input-x-${selected.point_id}`);input_x.type = "number";
                const input_y = document.getElementById(`input-y-${selected.point_id}`);input_y.type = "number";
                const input_z = document.getElementById(`input-z-${selected.point_id}`);input_z.type = "number";
        
                if (
                    x !== null && x !== undefined && x !== -1 &&
                    y !== null && y !== undefined && y !== -1 &&
                    z !== null && z !== undefined && z !== -1
                ) {
                    input_x.value = x;
                    input_y.value = y;
                    input_z.value = z;
                }

        
                const btn_increase_x = document.getElementById(`btn-inc-x-${selected.point_id}`);
                const btn_decrease_x = document.getElementById(`btn-dec-x-${selected.point_id}`);
                const btn_increase_y = document.getElementById(`btn-inc-y-${selected.point_id}`);
                const btn_decrease_y = document.getElementById(`btn-dec-y-${selected.point_id}`);
                const btn_increase_z = document.getElementById(`btn-inc-z-${selected.point_id}`);
                const btn_decrease_z = document.getElementById(`btn-dec-z-${selected.point_id}`);
                const btn_run          = document.getElementById(`btn-run-${selected.point_id}`);  // May cai nay khong can du lieu frame nen cu de no chay bang id du idtrung nhung n o 1 nhanh khac


                const btn_capture      = document.getElementById(`btn-capture-${selected.frame_id}-${selected.point_id}`);
                const btn_erase_master = document.getElementById(`btn-erase-${selected.frame_id}-${selected.point_id}`);
             
       
                const handleIncreaseX = () => HandleClickBtnIncrease_X(input_x, Max_X, input_x.value, input_y.value, input_z.value);
                const handleDecreaseX = () => HandleClickBtnDecrease_X(input_x, Max_X, input_x.value, input_y.value, input_z.value);

                const handleIncreaseY = () => HandleClickBtnIncrease_Y(input_y, Max_Y, input_x.value, input_y.value, input_z.value);
                const handleDecreaseY = () => HandleClickBtnDecrease_Y(input_y, Max_Y, input_x.value, input_y.value, input_z.value);

                const handleIncreaseZ = () => HandleClickBtnIncrease_Z(input_z, Max_Z, input_x.value, input_y.value, input_z.value);
                const handleDecreaseZ = () => HandleClickBtnDecrease_Z(input_z, Max_Z, input_x.value, input_y.value, input_z.value);


                const handleRun       = () => HandleClickBtnRun(input_x.value, input_y.value, input_z.value);
                const handleCapture   = () => HandleClickBtnCapture( selected.frame_id, selected.point_id, input_x.value, input_y.value, input_z.value);
                const handleErase     = () => HandleClickBtnEraseItemProduct(selected.frame_id,selected.point_id);
         

                // Gắn event (trước khi add thì remove trước để tránh trùng)
                btn_increase_x.removeEventListener("click", handleIncreaseX);
                btn_increase_x.addEventListener("click", handleIncreaseX);

                btn_decrease_x.removeEventListener("click", handleDecreaseX);
                btn_decrease_x.addEventListener("click", handleDecreaseX);

                btn_increase_y.removeEventListener("click", handleIncreaseY);
                btn_increase_y.addEventListener("click", handleIncreaseY);

                btn_decrease_y.removeEventListener("click", handleDecreaseY);
                btn_decrease_y.addEventListener("click", handleDecreaseY);

                btn_increase_z.removeEventListener("click", handleIncreaseZ);
                btn_increase_z.addEventListener("click", handleIncreaseZ);

                btn_decrease_z.removeEventListener("click", handleDecreaseZ);
                btn_decrease_z.addEventListener("click", handleDecreaseZ);

                btn_run.removeEventListener("click", handleRun);
                btn_run.addEventListener("click", handleRun);

                btn_capture.addEventListener("click", handleCapture);

                btn_erase_master.removeEventListener("click", handleErase);
                btn_erase_master.addEventListener("click", handleErase);
                
         
               
}

btn_erase_frame.addEventListener("click",()=>{
    console.log("selected.id_product_selecting_now ",id_product_selecting_now );
    if (!id_product_selecting_now ){
        write_log_capture_clear("Hiện tại chưa chọn loại model. Hãy chọn loại model cần xóa trước");
        return;
    }
    if (selected.frame_id == -1){
        write_log_capture_clear("Hãy chọn loại Frame cần xóa trước.");
        return;
    }
    console.log(`Xóa Frame Product = ${id_product_selecting_now} Item Frame ID = ${selected.frame_id}`);
    postData("/captureproduct/erase_frame",{"id_product_selecting_now":id_product_selecting_now,"FrameID":selected.frame_id}).then(data => {
        console.log("Data Receive Erase Frame",data?.data);
        renderMaster(data?.data);
    });
});

  



async function sendPoint(x, y, z) {
    if (isSending) {
      console.warn("⚠️ Đang gửi dữ liệu, vui lòng đợi...");
      write_log_capture_clear("⚠️ Đang gửi dữ liệu vui lòng đợi ...")
      return null; 
    }
    isSending = true; 
    try {
      const response = await fetch(`/captureproduct/run_point`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ x, y, z})
      });
      const data = await response.json();
    //   console.log("data?.status",data);
      if (data?.status){
        write_log_capture_clear(data?.message);
        return true;
      }
       write_log_capture_clear(data.message);//Server gui du lieu bi qua han
       return null;
    } catch (error) {
      console.error('Lỗi khi gửi điểm:', error);
      alert('❌ Gửi dữ liệu thất bại.');
      return null;
    } finally {
      isSending = false; 
    }
}

function HandleClickBtnRun(input_x_value,input_y_value,input_z_value){
    let status_check = validatePoint(input_x_value,input_y_value,input_z_value,max_point_run.x ,max_point_run.y ,max_point_run.z);
    if(!status_check){
    //   console.log("Dữ liệu không hợp lệ");
    //   write_log_capture_clear("❌ Dữ liệu không nằm trong giới hạn trục.\n✅ Hãy kiểm tra lại\n");
      return;
    }
    sendPoint(input_x_value,input_y_value,input_z_value);    
}


btn_add_frame.addEventListener("click",function(){
    let arr_id_frame = [];
    scroll_container.querySelectorAll(".box-frame").forEach(frame => {
        arr_id_frame.push(frame.dataset.frameId)
    });
    // console.log("arr_id_frame",arr_id_frame);

    write_log_capture_clear("");
    let new_id_frame = generateNewId(arr_id_frame);
    let length_arr_frame = arr_id_frame.length;  // Length la index
    // console.log("Bạn vừa click vào thêm frame");
    create_box(new_id_frame,length_arr_frame);
});


function create_box(box_id,index){
    console.log(`Tạo box ID= ${box_id},Index:${index}`);
    const div_box_frame = document.createElement("div");
    div_box_frame.className = "box-frame";
    div_box_frame.dataset.frameId = box_id; // gán id cho frame
    const div_text_box_frame =  document.createElement("div");
    div_text_box_frame.textContent = `Ảnh sản phẩm thứ ${index}`;
    div_text_box_frame.className = "text_inf_frame";
    const div_img_box =  document.createElement("div");
    div_img_box.className = "img-box";
    div_box_frame.addEventListener("click", () => {
        scroll_container.querySelectorAll(".box-frame").forEach(frame => {frame.classList.remove("box-frame-selected");});
        const id = div_box_frame.dataset.frameId;
        div_box_frame.classList.add("box-frame-selected");
        console.log("Bạn vừa click vào frame:", id);
        selected.frame_id = id;
        current_frame_box = div_img_box; // lưu frame hiện tại
    });
    div_box_frame.appendChild(div_text_box_frame);
    div_box_frame.appendChild(div_img_box);
    scroll_container.appendChild(div_box_frame);
    return {div_img_box,div_box_frame}
}
 

function getValue(data_value, coordinate_value,element_input) {
    if (data_value !== null && data_value !== undefined) {
        return data_value;
    }
    if (coordinate_value === -1) {
        return 0;
    }
    return coordinate_value;
}


function create_items_img(id, index ,data_point=null, frame_box =null, frame_id =  null){
    const img_text = document.createElement("div");
    img_text.className = "img-text";
    img_text.textContent = `Ảnh ${index}`;
    const img_img = document.createElement("img");
    img_img.className = "img_show_point";
    const img_item = document.createElement("div");
    if (data_point==null) {img_img.src = "../static/img/plus.png";img_item.dataset.has_icon_add_new = true;} else {img_img.src = `${data_point.path_img_point}?v=${Math.random()}`;}
    img_item.className = "img-item";
    img_item.dataset.id = id;
    img_item.appendChild(img_img);
    img_item.appendChild(img_text);
    if (frame_box){
            frame_box.appendChild(img_item);
            img_item.addEventListener("click",()=>{
                    // Cập nhật các biến global
                    scroll_container.querySelectorAll(".box-frame").forEach(frame => {
                            frame.querySelectorAll(".img-item").forEach(items => {
                        items.classList.remove("active");
                    });
                    });
                
                    img_item.classList.add("active");
                    current_frame_box = frame_box; //đối tượng dom
                    selected.point_id = Number(img_item.dataset.id);  
                    selected.frame_id = Number(frame_id);
                    console.log(`Point đang click frame: ${selected.frame_id} id: ${selected.point_id}`);
                    write_log_capture_clear("✍️ Nhập vị trí cần chụp ảnh.")
                    // console.log("ID thật:", img_item.dataset.id);
                    // console.log("Tên hiển thị:", img_text.textContent);
                    let x = getValue(data_point?.x, coordinate_after_taking_photo.x);
                    let y = getValue(data_point?.y, coordinate_after_taking_photo.y);
                    let z = getValue(data_point?.z, coordinate_after_taking_photo.z);
                    console.log("coordinate x",x);
                    console.log("coordinate y",y);
                    console.log("coordinate z",z);
                    create_table_controler(selected);
                    container_driver(selected,max_point_run.x,max_point_run.y,max_point_run.z,x,y,z);
                    return;
        });
    }
    else{
        console.log("Lỗi hoặc không có sản phẩm");
    }
}

btn_run_frame.addEventListener("click",()=>{

    console.log(`RunFrame Send Product ID:${id_product_selecting_now},Frame ID:${selected.frame_id}`);
    if (id_product_selecting_now == -1){
        console.log("Hiện tại bạn chưa chọn loại sản phẩm");
        return;
    }
    if (selected.frame_id == -1){
        console.log("Hiện tại bạn chưa chọn Frame cần chạy");
        return;
    }
    postData("/captureproduct/run_frame", {"ProductID":id_product_selecting_now,"FrameID":selected.frame_id}).then(data => {
            console.log("Data Receive RunFrame:",data);
    });

});

btn_run_product.addEventListener("click",()=>{
    console.log(`RunProduct Send Product ID:${id_product_selecting_now}}`);
    if (id_product_selecting_now == -1){
        console.log("Hiện tại bạn chưa chọn loại sản phẩm");
        return;
    }
    postData("/captureproduct/run_product", {"ProductID":id_product_selecting_now}).then(data => {
            console.log("Data Receive RunProduct:",data);
    });

});


function HandleClickBtnEraseItemProduct(FrameID,PointID){
    console.log(`Đã nhấn vào xóa ${FrameID},${PointID}`);
    if (!id_product_selecting_now ){
        write_log_capture_clear("Hiện tại chưa chọn loại model. Hãy chọn loại model cần xóa trước");
        return;
    }
    if (FrameID == -1){
        write_log_capture_clear("Bạn chưa chọn Frame nào. Hãy chọn ảnh trong Frame cần xóa");
        return;
    }
    if (PointID == -1){
        write_log_capture_clear("Bạn chưa chọn bức ảnh nào. Hãy chọn bức ảnh cần xóa");
        return;
    }

    postData("/captureproduct/erase_item_img",{"id_product_selecting_now":id_product_selecting_now,"FrameID":FrameID,"PointID":PointID}).then(data => {
        console.log("Data Receive Erase Items IMG",data?.data);
        renderMaster(data?.data);
    });
}

 
function HandleClickBtnCapture(frame_id,point_id, x , y , z){

    coordinate_after_taking_photo.x = x;
    coordinate_after_taking_photo.y = y;
    coordinate_after_taking_photo.z = z;
    console.log("----Đã nhấn vào chụp-----");

    if (current_frame_box){
    console.log("Frame box hiện tại đang click là:",current_frame_box);
    current_frame_box.querySelectorAll(".img-item").forEach((value ,index) => {
        // console.log("index",index,"value",value.dataset.has_icon_add_new);
        if (value.dataset.has_icon_add_new){
            // console.log("datsadds tat duoc nha");
            delete value.dataset.has_icon_add_new;
        }
    });}

    let status_check = validatePoint(x,y,z,max_point_run.x ,max_point_run.y ,max_point_run.z);
    if (status_check){
            console.log(`Data gửi chụp ảnh Product:${id_product_selecting_now} Frame ID:${frame_id} Point ID${point_id} X:${x},Y:${y} Z:${z}`);
            postData("/captureproduct/capture",{"product_selecting":id_product_selecting_now,"id_frame":frame_id,"id_point":point_id,"x":x,"y":y,"z":z})
            .then(data => {
                    renderMaster(data?.data);
                    // console.log("data chup anh",data?.data);
        });
    }
}



function create_table_controler(selected){
      anonymous.innerHTML = "";
      anonymous.appendChild(createInputRow("Nhập x:", "X là số nguyên dương", `input-x-${selected.point_id}`));
      anonymous.appendChild(createInputRow("Nhập y:", "Y là số nguyên dương", `input-y-${selected.point_id}`));
      anonymous.appendChild(createInputRow("Nhập z:", "Z là số nguyên dương", `input-z-${selected.point_id}`));

      anonymous.appendChild(createButtonRow([
          {id: `btn-inc-x-${selected.point_id}`, icon: "../static/img/add1.png", alt: "Tăng X", text: "Tăng X"},
          {id: `btn-dec-x-${selected.point_id}`, icon: "../static/img/minus.png", alt: "Giảm X", text: "Giảm X"}
      ]));
      anonymous.appendChild(createButtonRow([
          {id: `btn-inc-y-${selected.point_id}`, icon: "../static/img/add1.png", alt: "Tăng Y", text: "Tăng Y"},
          {id: `btn-dec-y-${selected.point_id}`, icon: "../static/img/minus.png", alt: "Giảm Y", text: "Giảm Y"}
      ]));
      anonymous.appendChild(createButtonRow([
          {id: `btn-inc-z-${selected.point_id}`, icon: "../static/img/add1.png", alt: "Tăng Z", text: "Tăng Z"},
          {id: `btn-dec-z-${selected.point_id}`, icon: "../static/img/minus.png", alt: "Giảm Z", text: "Giảm Z"}
      ]));

      anonymous.appendChild(createButtonRow([
          {id: `btn-run-${selected.point_id}`, icon: "../static/img/run_point_location.png", alt: "Chạy", text: "Chạy điểm"},
          {id: `btn-capture-${selected.frame_id}-${selected.point_id}`, icon: "../static/img/camera.png", alt: "Chụp", text: "Chụp"},
          {id: `btn-erase-${selected.frame_id}-${selected.point_id}`, icon: "../static/img/eraser (5).png", alt: "Xóa Ảnh", text: "Xóa ảnh"},
      ])); 
      anonymous.style.display = "block";
}



function createInputRow(labelText, placeholder, id = null) {
    const div = document.createElement("div");
    div.className = "Alight-items";

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
    div.className = "btn-driver-capture-point";
    buttons.forEach(btn => {
        const button = document.createElement("button");
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








function HandleClickBtnIncrease_X(element,max_element,input_x_value,input_y_value,input_z_value){
       let status_check = CheckData(element,"X",input_x_value,max_element);
       if(status_check){
        //   console.log("input_x_value", input_x_value);
         element.value = parseInt(input_x_value) + 1;
         HandleClickBtnRun(element.value,input_y_value,input_z_value);
       }

}
function HandleClickBtnDecrease_X(element,max_element,input_x_value,input_y_value,input_z_value) {
    let new_value = parseInt(input_x_value) - 1;
    let status_check = CheckData(element,"X", new_value, max_element);
    if (status_check) {
        element.value = new_value; 
        HandleClickBtnRun(element.value,input_y_value,input_z_value);
    } else {
        element.value = 0; 
    }
}   

function HandleClickBtnIncrease_Y(element,max_element,input_x_value,input_y_value,input_z_value){
       let status_check = CheckData(element,"Y",input_y_value,max_element);
       if(status_check){
         element.value = parseInt(input_y_value) + 1;
          HandleClickBtnRun(input_x_value,element.value,input_z_value);
       }
}
function HandleClickBtnDecrease_Y(element,max_element,input_x_value,input_y_value,input_z_value){
    let new_value = parseInt(input_y_value) - 1;
    let status_check = CheckData(element,"Y", new_value, max_element);
    if (status_check) {
        element.value = new_value; 
        HandleClickBtnRun(input_x_value,element.value,input_z_value);
    } else {
        element.value = 0; 
    }
}

function HandleClickBtnIncrease_Z(element,max_element,input_x_value,input_y_value,input_z_value){
        let status_check = CheckData(element,"Z",input_z_value,max_element);
        if(status_check){
          element.value = parseInt(input_z_value) + 1;
          HandleClickBtnRun(input_x_value,input_y_value,element.value);
        }
}
function HandleClickBtnDecrease_Z(element,max_element,input_x_value,input_y_value,input_z_value){
    let new_value = parseInt(input_z_value) - 1;
    let status_check = CheckData(element,"Z", new_value, max_element);
    if (status_check) {
        element.value = new_value; 
        HandleClickBtnRun(input_x_value,input_y_value,element.value);
    } else {
        element.value = 0; 
    }

}



function write_log_capture_clear(text){
    log_box.textContent = text;
}

function write_log_capture_append(text){
    log_box.textContent += text;
}


//validate
function validate_render_data(data){
    if (data?.error_code == 5002){ 
            const tbody = document.querySelector(".product-table tbody");
            if (!tbody){console.log("Bảng không tồn tại");
                return;
            }
            tbody.innerHTML = "";  
            const row = document.createElement("tr");
            let name = "?"; let x = "?"; let y = '?';let z = "?";
            row.innerHTML =  
                `<td>${name}</td>
                    <td>${x}</td>
                    <td>${y}</td>
                    <td>${z}</td>
                    `;
            tbody.appendChild(row);            
            write_log_capture_clear("❌ Hiện tại chưa chọn sản phẩm.\n✅ Hãy chọn lại sản phấm.");
            return;
    }
}

// Hàm validate toàn bộ điểm
function validatePoint(x, y, z, Limit_x, Limit_y, Limit_z) {
    // console.log("Dữ liệu trước khi chạy",x, y, z, Limit_x, Limit_y, Limit_z);
    if (
      isInvalid(x) || 
      isInvalid(y) || 
      isInvalid(z) || 
      isInvalid(Limit_x) ||
      isInvalid(Limit_y) ||
      isInvalid(Limit_z) 
    ) {
      write_log_capture_clear(`❌ Các giá trị X, Y, Z, K và giới hạn phải là số nguyên hợp lệ và không được để trống`);
      console.log(`❌ Các giá trị X, Y, Z, K và giới hạn phải là số nguyên hợp lệ và không được để trống`);
      return false;  // trả về false thay vì string
    }

    // Ép kiểu int sau khi đã check hợp lệ
    x = parseInt(x);
    y = parseInt(y);
    z = parseInt(z);
    Limit_x = parseInt(Limit_x);
    Limit_y = parseInt(Limit_y);
    Limit_z = parseInt(Limit_z);

    // Các điều kiện giới hạn
    if (x < 0 || y < 0 || z < 0 ) {
      write_log_capture_clear(`❌ Giá trị X, Y, Z, K phải lớn hơn hoặc bằng 0`);
      console.log(`❌ Giá trị X, Y, Z, K phải lớn hơn hoặc bằng 0`);
      return false;
    }
    if (x > Limit_x) {
      write_log_capture_clear(`❌ Giá trị X phải nhỏ hơn hoặc bằng ${Limit_x}`)
      console.log(`❌ Giá trị X phải nhỏ hơn hoặc bằng ${Limit_x}`);
      return false;
    }
    if (y > Limit_y) {
      write_log_capture_clear(`❌ Giá trị Y phải nhỏ hơn hoặc bằng ${Limit_y}`)
      console.log(`❌ Giá trị Y phải nhỏ hơn hoặc bằng ${Limit_y}`);
      return false;
    }
    if (z > Limit_z) {
        write_log_capture_clear(`❌ Giá trị Z phải nhỏ hơn hoặc bằng ${Limit_z}`);
      console.log(`❌ Giá trị Z phải nhỏ hơn hoặc bằng ${Limit_z}`);
      return false;
    }
    // console.log("✅ Dữ liệu hợp lệ");
    return true; // hợp lệ
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
        return false;
    }

    if (data >= value_max) {
        console.log(`❌ Giá trị "${str_name}" phải nhỏ hơn hoặc bằng ${value_max}`);
        log_box.innerHTML = `❌ Giá trị "${str_name}" phải nhỏ hơn hoặc bằng ${value_max}`;
         element.value = value_max;
        return false;
    }
    // console.log("data",data);
    console.log(`✅ Giá trị ${str_name} hợp lệ`);
    log_box.innerHTML = `✅ Giá trị ${str_name} hợp lệ`;
    return true;
}


// Hàm kiểm tra một giá trị có hợp lệ hay không
function isInvalid(value) {
  let num = Number(value);
  return (
    value === null ||        // null
    value === undefined ||   // undefined
    value === "" ||          // rỗng
    isNaN(num) ||            // không phải số
    !Number.isInteger(num)   // không phải số nguyên
  );
}