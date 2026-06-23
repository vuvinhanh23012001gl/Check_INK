import {MeasureWeldWidthCanvas} from "../canvas/measure_weld_width_canvas.js"

export const panner_measure_weld_width  =  document.getElementById("panner-measure-weld-width");
export let obj_measure_weld_width_canvas = new MeasureWeldWidthCanvas();

export let obj_product = null;  // cau hinh cai nay se su dung chung


export function set_obj_product(value) {
    obj_product = value;
}

export function get_obj_product() {
    return obj_product;
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
            targetCallback({ product_id, frame_id, items_id });
        } else {
            console.warn(`[Cảnh báo] File chính gọi kênh [${target_key}], nhưng file nhỏ chưa SET hàm cho kênh này!`);
        }
    }
};

