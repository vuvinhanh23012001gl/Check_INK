import {fetchGet, postData} from "../utills/api.js"
import {scroll_container,canvasManager}from "../common_value.js"
import {getValue} from "../utills/logic.js"
import {write_log_clear,write_log_append} from "./common_value_tool.js"
import {panner_measure_weld_width,panner_measure_slit_width,
    obj_measure_weld_width_canvas,obj_measure_slit_width_canvas,
    obj_region_arm_sensor_canvas,panner_region_arm_sensor,obj_region_arm_cover_canvas,
    panner_region_cover_sensor,additional_events,obj_measure_film_border_canvas,
    panner_measure_border_film,panner_permeable_membrane,obj_region_permeable_membrane_canvas,obj_region_hole_canvas,panner_region_hole
    ,panner_region_scratched_pipe,obj_region_scratched_pipe_canvas
    ,panner_region_end_chipping,obj_region_end_chipping_canvas,refesh_btn,setNameEventActivate,getNameEventActivate
   ,set_obj_product,get_obj_product} from "./common_value_tool.js"
import {Product} from "../model/model_product.js"
import { ItemsInspector } from "../services/items_inspector.js"
import { event_transition_items as eventTransitionSlit } from "./slit_tool.js";
import { event_transition_items as eventTransitionScratchedPipe } from "./scratched_pipe_tool.js";
import { event_transition_items as eventTransitionPermeableMembrane } from "./permeable_membrane_tool.js";
import { event_transition_items as eventTransitionMeasureWeldWidth } from "./measure_weld_width_tool.js";
import { event_transition_items as eventTransitionHole } from "./hole_tool.js";
import { event_transition_items as eventTransitionEndChipping } from "./end_chipping_tool.js";
import { event_transition_items as eventTransitionBorderFilm } from "./border_film_tool.js";
import { event_transition_items as eventTransitionArmCover } from "./arm_cover_tool.js";
import { event_transition_items as eventTransitionArmSensor } from "./arm_sensor_tool.js";
import {openOptionPanel} from "../panel_manager.js";


const panner_adjust_master = document.getElementById("panner-adjust-master");
const header_adjust_master = document.getElementById("header-ul-li-adjustment-master");
const btn_measure_weld_width = document.getElementById("btn-measure-weld-width");
const btn_save_law_regulation = document.getElementById("btn-save-law-regulation");
const btn_measurement_slit = document.getElementById("btn-measurement-slit");
const btn_check_arm_sensor  = document.getElementById("btn-check-arm-sensor");
const btn_check_arm_cover  = document.getElementById("btn-check-arm-cover");
const btn_border_film      =  document.getElementById("btn-border-film");
const btn_check_permeable_membrane = document.getElementById("btn-check-permeable-membrane");
const btn_check_hole = document.getElementById("btn-check-hole");
const btn_check_scratched_pipe = document.getElementById("btn-check-scratched-pipe");
const btn_check_end_chipping = document.getElementById("btn-check-end-chipping");
const btn_erase_all_draw = document.getElementById("btn-erase-all-draw");
const confirm_overlay = document.getElementById("confirm-exit-overlay");
const btn_confirm_yes = document.getElementById("btn-confirm-yes");
const btn_confirm_no = document.getElementById("btn-confirm-no");
const close_adjust_master = document.getElementById("close-adjust-master");
const log_regulations = document.getElementById("log-regulations");
const master_tool_buttons = panner_adjust_master.querySelectorAll(".tool-btn");
// Ở cấp con nhất (ScratchedPipeItemInspector, SlitItemInspector, ...): Khi !this.rectangle hoặc không có dữ liệu, phương thức toDict() trả về null
// Ở cấp ItemsInspector: Loại bỏ các inspector bị null. Nếu cả item không còn inspector nào $\rightarrow$ ItemsInspector.toDict() trả về null.
// Ở cấp Frame: Bỏ qua các Item trả về null. Nếu Frame không có Item nào $\rightarrow$ Frame.toDict() trả về null.
// Ở cấp Product: Chỉ thu thập các Frame còn dữ liệu. Chuỗi JSON cuối cùng thu được từ obj_product.toDict() sẽ sạch sẽ và không chứa bất kỳ key dư thừa nào.

let current_frame_box = null;
let has_clicked_tool = false; 
let master_load_promise = null;
let selected =  {
        product_id: -1,
        frame_id: -1,
        items_id: -1
}
close_adjust_master.addEventListener("click",()=>{
    console.log("Tến hành thoát thay đổi master");
      fetch('/law_regulation/exit')
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




btn_erase_all_draw.addEventListener("click",()=>{
    confirm_overlay.style.display = "flex";
});

btn_confirm_no.addEventListener("click",()=>{
    confirm_overlay.style.display = "none";

});

btn_confirm_yes.addEventListener("click",()=>{
    console.log("Xác nhận xóa ARM cover");
    let obj_product = get_obj_product();
    let status_erase  = obj_product.clearAllInspectors();
    canvasManager.clearAllCanvas();
    canvasManager.setTool(null);//đặt canvas bằng null
    refesh_btn();
    get_obj_product().clearHighlight(scroll_container);
    setNameEventActivate(null);
    refreshPanels();
    confirm_overlay.style.display = "none";
});



btn_check_end_chipping.addEventListener("click",()=>{
    console.log("bạn vừa click vào check end chipping");
    has_clicked_tool = true; // đã click tool
    refreshPanels();
    changeToolEvent(btn_check_end_chipping, btn_check_end_chipping.dataset.tool);
    canvasManager.setTool(obj_region_end_chipping_canvas);
    canvasManager.clearPreviewCanvas();
    canvasManager.clearShapeCanvas();
    panner_region_end_chipping.classList.add("active");
    eventTransitionEndChipping();
});

btn_check_scratched_pipe.addEventListener("click",()=>{
    console.log("bạn vừa click vào check scratched pipe");
    has_clicked_tool = true; // đã click tool
    refreshPanels();
    changeToolEvent(btn_check_scratched_pipe, btn_check_scratched_pipe.dataset.tool);
    canvasManager.setTool(obj_region_scratched_pipe_canvas);
    canvasManager.clearPreviewCanvas();
    canvasManager.clearShapeCanvas();
    panner_region_scratched_pipe.classList.add("active");
    eventTransitionScratchedPipe();
});


btn_check_hole.addEventListener("click",()=>{
    console.log("bạn vừa click vào check hole");
    has_clicked_tool = true; // đã click tool
    console.log("Bạn vừa nhấn vào nút check cảm biến sensor");
    refreshPanels();
    changeToolEvent(btn_check_hole, btn_check_hole.dataset.tool);
    canvasManager.setTool(obj_region_hole_canvas);
    canvasManager.clearPreviewCanvas();
    canvasManager.clearShapeCanvas();
    panner_region_hole.classList.add("active");
    eventTransitionHole();

});


btn_check_arm_sensor.addEventListener("click",()=>{
    has_clicked_tool = true; // đã click tool
    console.log("Bạn vừa nhấn vào nút check cảm biến sensor");
    refreshPanels();
    changeToolEvent(btn_check_arm_sensor, btn_check_arm_sensor.dataset.tool);
    canvasManager.setTool(obj_region_arm_sensor_canvas);
    canvasManager.clearPreviewCanvas();
    canvasManager.clearShapeCanvas();
    panner_region_arm_sensor.classList.add("active");
    eventTransitionArmSensor();
});

btn_check_permeable_membrane.addEventListener("click",()=>{
    console.log("bạn vừa nhấn vào nút kiểm tra màng bán thấm");
    has_clicked_tool = true; // đã click tool
    refreshPanels();
    changeToolEvent(btn_check_permeable_membrane, btn_check_permeable_membrane.dataset.tool);
    canvasManager.setTool(obj_region_permeable_membrane_canvas);
    canvasManager.clearPreviewCanvas();
    canvasManager.clearShapeCanvas();
    panner_permeable_membrane.classList.add("active");
    eventTransitionPermeableMembrane();
});




btn_check_arm_cover.addEventListener("click",()=>{
    has_clicked_tool = true; 
    console.log("Bạn vừa nhấn vào nút check cảm biến sensor");
    refreshPanels();
    changeToolEvent(btn_check_arm_cover, btn_check_arm_cover.dataset.tool);
    canvasManager.setTool(obj_region_arm_cover_canvas);
    canvasManager.clearPreviewCanvas();
    canvasManager.clearShapeCanvas();
    panner_region_cover_sensor.classList.add("active");
    eventTransitionArmCover();
    
});



btn_measurement_slit.addEventListener("click",()=>{
    has_clicked_tool = true;  // đã click tool
    refreshPanels();
    changeToolEvent(btn_measurement_slit, btn_measurement_slit.dataset.tool);
    console.log("Bạn vừa nhấn vào đo khoảng cách khe hàn");
    canvasManager.setTool(obj_measure_slit_width_canvas);
    canvasManager.clearPreviewCanvas();
    canvasManager.clearShapeCanvas();
    panner_measure_slit_width.classList.add("active");
    eventTransitionSlit();
});

btn_border_film.addEventListener("click",function(){
    console.log("Bạn vừa nhấn vào đo khoảng cách mép film");
    has_clicked_tool = true;  // đã click tool
    refreshPanels();
    changeToolEvent(btn_border_film, btn_border_film.dataset.tool);
    console.log("Bạn vừa nhấn vào đo khoảng cách khe hàn");
    canvasManager.setTool(obj_measure_film_border_canvas);
    canvasManager.clearPreviewCanvas();
    canvasManager.clearShapeCanvas();
    panner_measure_border_film.classList.add("active");
    eventTransitionBorderFilm();
});




btn_measure_weld_width.addEventListener("click",()=>{
    has_clicked_tool = true; // đã click tool
    changeToolEvent(btn_measure_weld_width, btn_measure_weld_width.dataset.tool);
    canvasManager.clearPreviewCanvas();
    canvasManager.clearShapeCanvas();
    console.log("--------Vào Tool nhận diện khoảng cách đường line-------");
    refreshPanels();
    panner_measure_weld_width.classList.add("active");
    canvasManager.setTool(obj_measure_weld_width_canvas);
    eventTransitionMeasureWeldWidth();

});

function changeToolEvent(button, tool) {
    refesh_btn();
    setNameEventActivate(tool);
    button.classList.add("active");
}





btn_save_law_regulation.addEventListener("click",async ()=>{
    console.log("Bạn vừa click vào lưu dữ liệu luật phán định");
    let obj_product = get_obj_product();
    let data_all = obj_product.toDict();
    let status_send =  await postData("/law_regulation/save",data_all);  // gui truc tiep khong can kiem tra
    console.log("data all :",data_all);
 
});


function refreshPanels() {
    panner_adjust_master.querySelectorAll(".tool-content").forEach((panel) => {
        panel.classList.remove("active");
    });
}


async function loadMasterDataOnce(openPanel = false){
    console.log("--------Bạn đã nhấn vào thay đổi master--------");
    write_log_clear(log_regulations, "🔧 Bắt đầu điều chỉnh master...");
    write_log_append(log_regulations, "🔎 Đang xác định sản phẩm hiện tại...");
    if (openPanel) {
        openOptionPanel(panner_adjust_master);
    }
    master_tool_buttons.forEach(button => button.disabled = true);

    write_log_append(log_regulations, "📡 Đang yêu cầu dữ liệu master từ hệ thống...");
    let head_data_master = await fetchGet("/law_regulation");
    console.log("head_data_master",head_data_master);

    if (!head_data_master?.ok || !head_data_master?.data) {
        write_log_append(log_regulations, "❌ Không thể lấy dữ liệu master. Vui lòng kiểm tra sản phẩm đang chọn và kết nối hệ thống.");
        master_tool_buttons.forEach(button => button.disabled = false);
        return;
    }

    let data_point = head_data_master.data.data_point;
    selected.product_id = head_data_master.data.product?._id;
    console.log("ID sản phẩm đang chọn là :",selected.product_id);
    write_log_append(log_regulations, `✅ Đã xác định sản phẩm: ${selected.product_id ?? "chưa có mã"}.`);

    let data_master = head_data_master.data.data_master;
    console.log("Data master",data_master);
    write_log_append(log_regulations, `📸 Đã lấy danh sách master (${Object.keys(data_point || {}).length} frame).`);

    let actual_wid_img = head_data_master.data.wid_img;
    let actual_hei_img = head_data_master.data.hei_img;
    write_log_append(log_regulations, `📐 Kích thước ảnh master: ${actual_wid_img} x ${actual_hei_img}.`);
    write_log_append(log_regulations, "📋 Đang nạp cây luật phán định của master...");
    try {
        create_object_need(head_data_master.data.tree?.data);
    } catch (error) {
        console.error("Lỗi nạp cây luật phán định:", error);
        write_log_append(log_regulations, "⚠️ Không thể nạp cây luật phán định, nhưng vẫn hiển thị ảnh master.");
    }

    scroll_container.querySelectorAll(".box-frame").forEach(frame => frame.remove());
    create_img_items_dimesion_calibration(data_point || {});
    master_tool_buttons.forEach(button => button.disabled = false);
    write_log_append(log_regulations, "✅ Hoàn tất lấy master. Có thể chọn ảnh và điều chỉnh các vùng kiểm tra.");
}

async function loadMasterData(openPanel = false){
    if (master_load_promise) {
        if (openPanel) {
            openOptionPanel(panner_adjust_master);
        }
        return master_load_promise;
    }

    master_load_promise = loadMasterDataOnce(openPanel);
    try {
        return await master_load_promise;
    } finally {
        master_tool_buttons.forEach(button => button.disabled = false);
        master_load_promise = null;
    }
}

header_adjust_master.addEventListener("click", async ()=>{
    await loadMasterData(true);
});

loadMasterData();

function create_object_need(tree){
    // try {
        console.log("tree",tree);
        const product = Product.fromDict(tree);
        console.log("tree ObJect",product);
        // const product_json = JSON.stringify(tree);
        // console.log("product_json",product_json);
        set_obj_product(product);
}


function create_img_items_dimesion_calibration(points_and_box){
        // console.log("Data create_img_items",data?.data);
        // console.log("data đúng của product");
        // console.log("points_and_box",points_and_box);
        let index_frame = 0;
        let build_tree = {};
        for (const boxs in points_and_box){
            // console.log("boxs",boxs);
            // console.log("Số Frame ID hiện tại bằng",count_frame_id);
            let index_items = 0;
            let result_create_box = create_box(boxs,index_frame);
            let div_img_box = result_create_box.div_img_box;
            let div_box_frame = result_create_box.div_box_frame;
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



function create_items_img(id, index ,data_point = null, frame_box =null, frame_id =  null){
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
    if(!frame_box){console.log("Lỗi hoặc không có sản phẩm");return;}
    frame_box.appendChild(img_item);
        img_item.addEventListener("click",()=>{
            canvasManager.clearShapeCanvas();
            canvasManager.clearPreviewCanvas();
            canvasManager.show_img_items(img_img);
            scroll_container.querySelectorAll(".box-frame").forEach(frame => {
                frame.querySelectorAll(".img-item").forEach(items => {
                items.classList.remove("active");
                });
            });  
              
            // let x = getValue(data_point?.x);
            // let y = getValue(data_point?.y);
            // let z = getValue(data_point?.z);
            // coordinate_items_now.x = x;
            // coordinate_items_now.y = y;
            // coordinate_items_now.z = z;

            // console.log("coordinate x",x);
            // console.log("coordinate y",y);
            // console.log("coordinate z",z);
            // console.log("frame_box",frame_box);
           
            img_item.classList.add("active");
            current_frame_box = frame_box;
            selected.items_id = Number(img_item.dataset.id);  
            selected.frame_id = Number(frame_id);
                if (has_clicked_tool && typeof additional_events.onFrameChange === "function") {
                    additional_events.onFrameChange(selected.product_id ,selected.frame_id, selected.items_id,getNameEventActivate());
            }
            console.log(`Point đang click frame: ${selected.frame_id} id: ${selected.items_id}`);
            return;
    });
 }
 
function create_box(box_id,index){
    console.log(`Tạo box ID= ${box_id},Index:${index}`);
    const div_box_frame = document.createElement("div");
    div_box_frame.className = "box-frame";
    div_box_frame.dataset.frameId = box_id; 
    const div_text_box_frame =  document.createElement("div");
    div_text_box_frame.textContent = `Ảnh sản phẩm thứ ${index}`;
    div_text_box_frame.className = "text_inf_frame";
    const div_img_box =  document.createElement("div");
    div_img_box.className = "img-box";
    div_box_frame.addEventListener("click", () => {
        scroll_container.querySelectorAll(".box-frame").forEach(frame => {frame.classList.remove("box-frame-selected");});
        selected.frame_id = div_box_frame.dataset.frameId;
        div_box_frame.classList.add("box-frame-selected");
        console.log("Click vào frame thứ:", selected.frame_id);
        current_frame_box = div_img_box; // lưu frame hiện tại đang click


    });
    div_box_frame.appendChild(div_text_box_frame);
    div_box_frame.appendChild(div_img_box);
    scroll_container.appendChild(div_box_frame);
    return {div_img_box,div_box_frame}
}

