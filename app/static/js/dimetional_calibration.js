import {fetchGet,postData} from "./utills/api.js"
import {scroll_container,canvasManager,active_sceen_show_video,show_video_product,get_camera_connection}from "./common_value.js";
import {DimesionalCalibrationDraw} from "./model/dimesional_calibration_draw.js"
import {}from "./utills/logic.js";


const header_dimetional_calibration = document.getElementById("header-ul-li-dimensional-calibration");
const obj_draw_calibration = new DimesionalCalibrationDraw()
const paner_draw_calibration = document.getElementById("paner-calibration");
const open_video_calibration = document.getElementById("open-video-calibration");
const log_calibration       = document.getElementById("log-calibration");
const run_point             = document.getElementById("run-point-calibration");
const cancel_calibration_button  = document.getElementById("cancel-calibration-button");

let coordinate_items_now ={
    x:-1,
    y:-1,
    z:-1,
}
const selected = {
    frame_id: -1,
    point_id: -1
};
let  current_frame_box = null ; // Frame hiện tại đang đc click





header_dimetional_calibration.addEventListener("click",async ()=>{
         
    paner_draw_calibration.classList.add("active");
    canvasManager.setTool(obj_draw_calibration); 
    console.log("Bạn vừa click vào hiệu chuẩn kích thước");
    let head_data = await  fetchGet("/dimesional_calibration");
    console.log("Bạn nhấn vào hiệu chỉnh kích thước.");
    console.log("Data header dimesion calibration",head_data);
    let data_point =  head_data?.data?.data_point;
    create_img_items_dimesion_calibration(data_point);
    



});

run_point.addEventListener("click",()=>{
    console.log("Bạn vừa click vào run point");
    if (coordinate_items_now.x == -1 || coordinate_items_now.y == -1 || coordinate_items_now.z == -1){
         console.log("Muốn chạy điểm dữ liệu x y z phải khác -1");
         write_log_calibration_clear("❌Bạn chưa chọn điểm nào để di chuyển.\n✅ Hãy click vào hình muốn di chuyển đến.\n");
         return;
    }
    write_log_calibration_clear("");
     postData("/dimesional_calibration/run_point_define_value",{x:coordinate_items_now.x,y:coordinate_items_now.y,z:coordinate_items_now.z});   
});
open_video_calibration.addEventListener("click",()=>{
    console.log("Bạn vừa nhấn vào Stream video calibration");
    if(!get_camera_connection()){ write_log_calibration_clear("❌ Camera hiện tại chưa kết nối.\n✅ Hãy kiểm tra kết nối.\n"); return;}
    active_sceen_show_video();
    show_video_product();
});





let dict_lines_of_frames = {
    "0": {
           "line": {
            "xStart": 10, "yStart": 10, "xEnd": 300, "yEnd": 200
          },
          "items_id": "0", // Phải khớp với ID ảnh được tạo từ vòng lặp items
          "calibration": 1
    },
        "1": {
           "line": {
            "xStart": 330, "yStart": 10, "xEnd": 400, "yEnd": 200
          },
          "items_id": "0", // Phải khớp với ID ảnh được tạo từ vòng lặp items
          "calibration": 1
    }
}








function create_img_items_dimesion_calibration(points_and_box){
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
                    let calibration_frame =  dict_lines_of_frames[frame_id];
                    console.log("ahihih",calibration_frame)
                    canvasManager.show_img_items(img_img);
                    create_line(calibration_frame,img_item.dataset.id)
                    console.log("data_point",data_point);
                    let x = getValue(data_point?.x);
                    let y = getValue(data_point?.y);
                    let z = getValue(data_point?.z);
                    coordinate_items_now.x = x;
                    coordinate_items_now.y = y;
                    coordinate_items_now.z = z;
                    // console.log("coordinate x",x);
                    // console.log("coordinate y",y);
                    // console.log("coordinate z",z);
                    
                    img_item.classList.add("active");
                    current_frame_box = frame_box; //đối tượng dom
                    selected.point_id = Number(img_item.dataset.id);  
                    selected.frame_id = Number(frame_id);
                    console.log(`Point đang click frame: ${selected.frame_id} id: ${selected.point_id}`);
                    // write_log_capture_clear("✍️ Nhập vị trí cần chụp ảnh.")
                    // console.log("ID thật:", img_item.dataset.id);
                    // console.log("Tên hiển thị:", img_text.textContent);


                    return;
        });
    }
    else{
        console.log("Lỗi hoặc không có sản phẩm");
    }
}
    //   "line":{
    //         "xStart":-1,
    //         "yStart":-1,
    //         "xEnd":-1,
    //         "yEnd":-1, 
    //       },

function create_line(data, items_id_select_now){
    if (!data) return;
    let items_id = data.items_id;
    let line = data.line;
    if (String(items_id) === String(items_id_select_now)){
        // console.log("Tiến hành vẽ điểm");
        // console.log("lines", line);
        obj_draw_calibration.defined_line_segment.xStart = line?.xStart;
        obj_draw_calibration.defined_line_segment.yStart = line?.yStart;
        obj_draw_calibration.defined_line_segment.xEnd = line?.xEnd;
        obj_draw_calibration.defined_line_segment.yEnd = line?.yEnd;
        obj_draw_calibration.draw_defined_line_segment(canvasManager);
        return;
    }
    console.log(`Điểm này (${items_id_select_now}) không phải điểm đã cấu hình trong Mock Data (${items_id})`);
}

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

function write_log_calibration_clear(text){
    log_calibration.textContent = text;
}
function write_log_calibration_append(text){
    log_calibration.textContent += text;
}

function getValue(value) {
    return value ?? -1;
}

cancel_calibration_button.addEventListener("click",()=>{
    console.log("Tến hành thoát dimesionnal calibration");
      fetch('/dimesional_calibration/exit')
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