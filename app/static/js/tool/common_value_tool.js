import {LineDrawer} from "../canvas/line_drawer_canvas.js"
import {RectangleDrawer} from "../canvas/rectangel_drawer_canvas.js"

export const panner_measure_weld_width  =  document.getElementById("panner-measure-weld-width");
export const panner_measure_slit_width  =  document.getElementById("panner-measure-slit-width");
export const panner_region_arm_sensor  =  document.getElementById("panner-region-arm-sensor");





export let obj_measure_weld_width_canvas = new LineDrawer();
export let obj_measure_slit_width_canvas = new LineDrawer();
export let obj_region_arm_sensor_canvas = new  RectangleDrawer();

export let obj_product = null;  // cau hinh cai nay se su dung chung

export const  boxContentMeasureWeldWidth = document.getElementById("table-cof-tool-content-measure-weld-width")
export const  boxContentMeasureSlitWidth = document.getElementById("table-cof-tool-content-measure-slit-width")

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

