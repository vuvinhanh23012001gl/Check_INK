console.log("Vào File End Chipping Tool");
import { ModelRectangle } from '../model/model_rectangle.js'; 
import {scroll_container,canvasManager,WIDTH_IMG_SHAPE}from "../common_value.js"
import {obj_region_end_chipping_canvas,boxContentEndChipping,get_obj_product,selected,checkSelected,
    additional_events,write_log_clear,write_log_append,COLOR_RECT_SHAPE_REGION_DETECT,create_obj_cross_item,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE,refesh_btn,setNameEventActivate,panner_region_end_chipping
} from "./common_value_tool.js"   
import {RectangleDrawer} from "../canvas/rectangel_drawer_canvas.js"
import {ItemsInspector} from "../services/items_inspector.js"
import {EndChippingInspector} from "../services/end_chipping_item_inspector.js"
import {postData} from "../utills/api.js";


additional_events.set("end-chipping-tool", event_transition_items);
const btn_judment_end_chipping = document.getElementById("btn-judment-end-chipping");
const log_end_chipping = document.getElementById("log-end-chipping");
const btn_exit_end_chipping = document.getElementById("btn-exit-end-chipping");






obj_region_end_chipping_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT,func_callback_click_on_rect);
obj_region_end_chipping_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_RIGHT_RECT,func_callback_click_mouse_right_into_line);
obj_region_end_chipping_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT_HAVE_ALREADY,func_callback_click_on_line_have_aready);

function func_callback_click_on_rect(data_shape){
    console.log("click vào khung",data_shape);
    console.log("boxContentEndChipping",boxContentEndChipping);
    boxContentEndChipping.appendChild(createEndChipping(data_shape)); 

}

btn_exit_end_chipping.addEventListener("click",()=>{
    console.log("Bạn vừa nhấn vào thoát Frame");
    canvasManager.clearShapeCanvas();
    canvasManager.clearPreviewCanvas();
    canvasManager.setTool(null);//đặt canvas bằng null
    boxContentEndChipping.innerHTML = "";
    panner_region_end_chipping.classList.remove("active");
    refesh_btn();
    get_obj_product().clearHighlight(scroll_container);
    setNameEventActivate(null);
})


function func_callback_click_mouse_right_into_line(coordinate){
    boxContentEndChipping.innerHTML = ""; 
    let obj_end_chipping_inspector = create_obj_cross_item(ItemsInspector.TYPE_END_CHIPPING,EndChippingInspector,"setEndChippingItems");
    let result_find_line  = obj_end_chipping_inspector.isPointOnRoiBorder(coordinate.x,coordinate.y,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE);
    if (result_find_line){
        console.log("Click trúng đường viền");
        obj_end_chipping_inspector.removeCropRoi();
        canvasManager.clearShapeCanvas();
        obj_end_chipping_inspector.drawAll(canvasManager);
        get_obj_product().highlightItems(scroll_container, ItemsInspector.TYPE_END_CHIPPING, "cropRoi");  
    }
}




export function event_transition_items(){
    boxContentEndChipping.innerHTML = ""; 
    obj_region_end_chipping_canvas.reset();
     canvasManager.clearShapeCanvas();
     get_obj_product().highlightItems(scroll_container, ItemsInspector.TYPE_END_CHIPPING, "cropRoi");  
    let obj_end_chipping_inspector = create_obj_cross_item(ItemsInspector.TYPE_END_CHIPPING,EndChippingInspector,"setEndChippingItems");
    if (obj_end_chipping_inspector){
        obj_end_chipping_inspector.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
        console.log("Không tạo đc dữ liệu obj_end_chipping_inspector");
        return;
    }
}




function func_callback_click_on_line_have_aready(coordinate) {
    let obj_end_chipping_inspector = create_obj_cross_item(ItemsInspector.TYPE_END_CHIPPING,EndChippingInspector,"setEndChippingItems");
    if (!obj_end_chipping_inspector) return;
    const rect = obj_end_chipping_inspector.getCropRoi();
    if (!rect) return;
    if (obj_end_chipping_inspector.isPointOnRoiBorder(coordinate.x, coordinate.y,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE)) {
        boxContentEndChipping.innerHTML = "";
        obj_region_end_chipping_canvas.have_return = true;
        const currentThreshold = obj_end_chipping_inspector.getThreshold();
        const dataPayload = {
            ...rect,
            thresholdNG: currentThreshold
        };
        boxContentEndChipping.appendChild(createEndChipping(dataPayload));
    }
}



function createEndChipping(data_end_chipping = null) {
    let obj_end_chipping_inspector = create_obj_cross_item(ItemsInspector.TYPE_END_CHIPPING,EndChippingInspector,"setEndChippingItems");
    const wrapper = document.createElement("div");
    wrapper.id = "measure-end-chipping-wrapper";

    const table = document.createElement("table");
    table.className = "measure-weld-width-config-table";
    table.id = "measure-end-chipping-table";
    const rows = [
        "Tên hình",
        "Ngưỡng mẻ ống"
    ];
    rows.forEach((labelText, index) => {
        const tr = document.createElement("tr");
        tr.className = "config-row";

        const th = document.createElement("th");
        th.className = "config-label";
        th.textContent = labelText;

        const td = document.createElement("td");
        td.className = "config-value";

        const input = document.createElement("input");
        input.className = "config-input";
        input.id = `measure-end-chipping-input-${index}`;
        
        if (index === 0) {
            input.type = "text";
            input.placeholder = "Nhập tên hình";
            if (data_end_chipping) {
                input.value = data_end_chipping.name ?? "Lỗi mẻ cạnh";
            }
        } else if (index === 1) {
            input.type = "number";
            input.placeholder = "Nhập ngưỡng NG";
            input.step = "any";
            console.log(" obj_end_chipping_inspector.threshold", obj_end_chipping_inspector.threshold);
            input.value = obj_end_chipping_inspector.threshold ?? 0;
        }

        td.appendChild(input);
        tr.appendChild(th);
        tr.appendChild(td);
        table.appendChild(tr);
    });

    // ===== Buttons =====
    const actions = document.createElement("div");
    actions.className = "config-actions";

    const btnAccept = document.createElement("button");
    btnAccept.className = "btn btn-accept";
    btnAccept.id = "btn-accept-end-chipping";
    btnAccept.textContent = "Chấp nhận";
    btnAccept.addEventListener("click", () => {
            const nameEndChipping = document.getElementById("measure-end-chipping-input-0")?.value || "";
            const thresholdNG = parseFloat(document.getElementById("measure-end-chipping-input-1")?.value) || 0;
            const objEndChippingCropROI = new ModelRectangle(
                0,
                nameEndChipping,
                data_end_chipping?.xStart,
                data_end_chipping?.yStart,
                data_end_chipping?.xEnd,
                data_end_chipping?.yEnd
            );
            const resultValidate = objEndChippingCropROI.validate();
            if (resultValidate.isValid) {
                if (typeof boxContentEndChipping !== "undefined") {
                    boxContentEndChipping.innerHTML = "";
                }
                obj_end_chipping_inspector.setCropRoi(objEndChippingCropROI);
                obj_end_chipping_inspector.threshold = thresholdNG;
                write_log_clear(log_end_chipping, "✅ Dữ liệu hợp lệ.");
                if (typeof obj_region_end_chipping_canvas !== "undefined") {
                    obj_region_end_chipping_canvas.is_available_one_line = false;
                    obj_region_end_chipping_canvas.reset();
                }
                canvasManager.clearShapeCanvas();
                obj_end_chipping_inspector.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
                get_obj_product().highlightItems(scroll_container, ItemsInspector.TYPE_END_CHIPPING, "cropRoi");  
            } else {
                let alertMessage = "❌ THÔNG BÁO LỖI DỮ LIỆU NHẬP VÀO:\n\n";
                write_log_clear(log_end_chipping, alertMessage);
                resultValidate.errors.forEach(err => {
                    write_log_append(log_end_chipping, `📍 ${err.rowName}`);
                    write_log_append(log_end_chipping, ` - Giá trị hiện tại: "${err.currentVal}"`);
                    write_log_append(log_end_chipping, ` - Yêu cầu: ${err.expected}`);
                });
            }
        });

    const btnClear = document.createElement("button");
    btnClear.className = "btn btn-clear";
    btnClear.id = "btn-clear-end-chipping";
    btnClear.textContent = "Xóa";

    btnClear.addEventListener("click", () => {
        const inpName = document.getElementById("measure-end-chipping-input-0");
        const inpThreshold = document.getElementById("measure-end-chipping-input-1");
        if (inpName) inpName.value = "";
        if (inpThreshold) inpThreshold.value = "";
    });

    actions.appendChild(btnAccept);
    actions.appendChild(btnClear);

    wrapper.appendChild(table);
    wrapper.appendChild(actions);

    return wrapper;
}

