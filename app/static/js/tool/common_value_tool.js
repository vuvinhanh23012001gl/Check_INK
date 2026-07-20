import {LineDrawer} from "../canvas/line_drawer_canvas.js"
import {RectangleDrawer} from "../canvas/rectangel_drawer_canvas.js"

export const panner_measure_weld_width  =  document.getElementById("panner-measure-weld-width");
export const panner_measure_slit_width  =  document.getElementById("panner-measure-slit-width");
export const panner_region_arm_sensor  =  document.getElementById("panner-region-arm-sensor");
export const panner_region_cover_sensor = document.getElementById("panner-region-cover-sensor");
export const panner_measure_border_film =   document.getElementById("panner-measure-border-film");
export const panner_permeable_membrane = document.getElementById("panner-permeable-membrane");




export let obj_measure_weld_width_canvas = new LineDrawer();
export let obj_measure_slit_width_canvas = new LineDrawer();
export let obj_measure_film_border_canvas = new LineDrawer();


export let obj_region_arm_sensor_canvas = new  RectangleDrawer();
export let obj_region_arm_cover_canvas = new  RectangleDrawer();
export let obj_region_permeable_membrane_canvas = new  RectangleDrawer();

export let obj_product = null;  // cau hinh cai nay se su dung chung

export const  boxContentMeasureWeldWidth = document.getElementById("table-cof-tool-content-measure-weld-width");
export const  boxContentMeasureSlitWidth = document.getElementById("table-cof-tool-content-measure-slit-width");
export const  boxContentArmSensor = document.getElementById("table-cof-arm-sensor");
export const  boxContentArmCover = document.getElementById("table-cof-arm-cover");
export const  boxConetentBorderFilm = document.getElementById("table-cof-border-film");
export const  boxContentPermeableMembrane =  document.getElementById("table-cof-permeable-membrane");
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
