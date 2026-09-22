import {LineDrawer} from "../canvas/line_drawer_canvas.js"
import {RectangleDrawer} from "../canvas/rectangel_drawer_canvas.js"

export const panner_measure_weld_width  =  document.getElementById("panner-measure-weld-width");
export const panner_measure_slit_width  =  document.getElementById("panner-measure-slit-width");
export const panner_region_arm_sensor  =  document.getElementById("panner-region-arm-sensor");
export const panner_region_cover_sensor = document.getElementById("panner-region-cover-sensor");
export const panner_measure_border_film =   document.getElementById("panner-measure-border-film");
export const panner_permeable_membrane = document.getElementById("panner-permeable-membrane");
export const panner_region_hole = document.getElementById("panner-region-hole");
export const panner_region_scratched_pipe = document.getElementById("panner-region-scratched-pipe");
export const panner_region_end_chipping = document.getElementById("panner-region-end-chipping");
export const panner_region_foreign_object = document.getElementById("panner-region-foreign-object");
export const panner_region_air_bubbles = document.getElementById("panner-region-air-bubbles");


export const COLOR_RECT_SHAPE_REGION_DETECT = "#0000FF";
export const ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE = 10;

export let obj_measure_weld_width_canvas = new LineDrawer();
export let obj_measure_slit_width_canvas = new LineDrawer();
export let obj_measure_film_border_canvas = new LineDrawer();


export let obj_region_arm_sensor_canvas = new  RectangleDrawer();
export let obj_region_arm_cover_canvas = new  RectangleDrawer();
export let obj_region_permeable_membrane_canvas = new  RectangleDrawer();
export let obj_region_hole_canvas = new RectangleDrawer();
export let obj_region_scratched_pipe_canvas = new RectangleDrawer();
export let obj_region_end_chipping_canvas = new RectangleDrawer();
export let obj_region_foreign_object_canvas = new RectangleDrawer();
export let obj_region_air_bubbles_canvas = new RectangleDrawer();

let name_event_activate = null; //event khi nhấn vào các Items set thành loại tương
export let obj_product = null;  // cau hinh cai nay se su dung chung

export const  boxContentMeasureWeldWidth = document.getElementById("table-cof-tool-content-measure-weld-width");
export const  boxContentMeasureSlitWidth = document.getElementById("table-cof-tool-content-measure-slit-width");
export const  boxContentArmSensor = document.getElementById("table-cof-arm-sensor");
export const  boxContentArmCover = document.getElementById("table-cof-arm-cover");
export const  boxConetentBorderFilm = document.getElementById("table-cof-border-film");
export const  boxContentPermeableMembrane =  document.getElementById("table-cof-permeable-membrane");
export const  boxContentHole = document.getElementById("table-cof-hole");
export const  boxContentScratchedPipe = document.getElementById("table-cof-scratched-pipe");
export const  boxContentEndChipping  = document.getElementById("table-cof-end-chipping");
export const boxContentForeignObject = document.getElementById("table-cof-foreign-object");
export const boxContentAirBubbles = document.getElementById("table-cof-air-bubbles");


export const getNameEventActivate = () => {
    return name_event_activate;
};

export const setNameEventActivate = (value) => {
    name_event_activate = value;
};

export function set_obj_product(value) {
    obj_product = value;
}

export function get_obj_product() {
    return obj_product;
}

export let selected = {      
    product_id :-1,
    frame_id:-1,
    items_id:-1,
}

let dict_callbacks = {};
export const additional_events = {
    set: function(name_key, callbackFunc) {
        if (typeof callbackFunc === "function") {
            dict_callbacks[name_key] = callbackFunc;
            console.log(`[Hệ thống] File nhỏ [${name_key}] đã SET hàm thành công!`);
        } else {
            console.error(`[Lỗi] Giá trị set cho [${name_key}] phải là một hàm (function)!`);
        }
    },
    onFrameChange: function(product_id, frame_id, items_id, target_key) {
        const targetCallback = dict_callbacks[target_key];
        if (typeof targetCallback === "function") {
            selected.product_id = product_id;
            selected.frame_id = frame_id;
            selected.items_id = items_id;
            targetCallback();
        } else {
            console.warn(`[Cảnh báo] File chính gọi kênh [${target_key}], nhưng file nhỏ chưa SET hàm cho kênh này!`);
        }
    }
};

//Ham nay kiem tra selected co hop le khong
export function checkSelected(selected) {
    const checks = [
        {
            value: selected.product_id,
            message: "❌Bạn chưa chọn sản phẩm\n"
        },
        {
            value: selected.frame_id,
            message: "❌Bạn chưa chọn Frame tương ứng\n"
        },
        {
            value: selected.items_id,
            message: "❌Bạn chưa chọn điểm tương ứng\n"
        }
    ];
    for (const check of checks) {
        if (check.value === -1) {
            console.log(check.message);
            return false;
        }
    }
    return true;
}




export function write_log_clear(logElement, text = "") {
    if (!logElement) return;
    logElement.textContent = text;
}

export function write_log_append(logElement, text = "") {
    if (!logElement) return;
    logElement.style.whiteSpace = "pre-line"; 
    logElement.textContent += text + "\n";
}

export function create_obj_cross_item(typeInspector, InspectorClass, setterMethodName) {
    if (!typeInspector || !InspectorClass || !setterMethodName) {
        console.error("Thiếu tham số bắt buộc!");
        return null;
    }
    
    const frameId = String(selected?.frame_id);
    const itemsId = String(selected?.items_id);

    let inspectorObj = get_obj_product().find_item_object_corresponding(frameId, itemsId, typeInspector);
    if (!inspectorObj) {
        const obj_items_inspector = get_obj_product().get_item_object(frameId, itemsId);
        
        if (obj_items_inspector) {
            // Kiểm tra xem phương thức có tồn tại trên object không
            if (typeof obj_items_inspector[setterMethodName] === 'function') {
                inspectorObj = new InspectorClass();
                // Gọi phương thức bằng toán tử ngoặc vuông []
                obj_items_inspector[setterMethodName](inspectorObj);
                console.log(`Tạo thành công đối tượng cho type: ${typeInspector}`);
            } else {
                console.error(`Phương thức ${setterMethodName} không tồn tại trên obj_items_inspector!`);
            }
        } else {
            console.warn("Không tìm thấy obj_items_inspector tương ứng!");
        }
    }
    return inspectorObj;
}

export function refesh_btn(){
    const buttons = document.querySelectorAll("#choose-tool button");
    buttons.forEach((btn,index)=>{
        // console.log("btn",btn);
        btn.classList.remove("active");
    });
}