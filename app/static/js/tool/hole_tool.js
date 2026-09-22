console.log("Vào File Hole Tool");
import { ModelRectangle } from '../model/model_rectangle.js'; 
import {scroll_container,canvasManager,WIDTH_IMG_SHAPE}from "../common_value.js"
import {obj_region_hole_canvas,boxContentHole,get_obj_product,selected,checkSelected,additional_events,COLOR_RECT_SHAPE_REGION_DETECT,
    write_log_clear,write_log_append,create_obj_cross_item,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE,panner_region_hole,refesh_btn,setNameEventActivate
} from "./common_value_tool.js"   
import {RectangleDrawer} from "../canvas/rectangel_drawer_canvas.js"
import {ItemsInspector} from "../services/items_inspector.js"
import {HoleItemInspector} from "../services/hole_item_inspector.js"
import {postData} from "../utills/api.js";



additional_events.set("hole_tool", event_transition_items);
const btn_judment_hole = document.getElementById("btn-judment-hole");
const log_hole = document.getElementById("log-hole");
const btn_exit_hole = document.getElementById("btn-exit-hole");
 
obj_region_hole_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT,func_callback_click_on_rect);
obj_region_hole_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_RIGHT_RECT,func_callback_click_mouse_right_into_line);
obj_region_hole_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT_HAVE_ALREADY,func_callback_click_on_line_have_aready);

function func_callback_click_on_rect(data_shape){
    console.log("click vào khung",data_shape);
    console.log("boxContentArmSensor",boxContentHole);
    boxContentHole.appendChild(createHoleTable(data_shape)); 
}

      
function func_callback_click_mouse_right_into_line(coordinate){
    boxContentHole.innerHTML = ""; 
    let obj_hole_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_HOLE,HoleItemInspector,"setHoleItems");
    let result_find_line  = obj_hole_item_inspector.isPointOnRoiBorder(coordinate.x,coordinate.y,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE);
    if (result_find_line){
        console.log("Click trúng đường viền");
        obj_hole_item_inspector.removeRectangle();
        get_obj_product().highlightItems(scroll_container,ItemsInspector.TYPE_HOLE,"rectangle"); 
        canvasManager.clearShapeCanvas();
        obj_hole_item_inspector.drawAll(canvasManager);
    }
}

btn_exit_hole.addEventListener("click",()=>{
    console.log("Nhấn vào đóng Frame");
    canvasManager.clearShapeCanvas();
    canvasManager.clearPreviewCanvas();
    canvasManager.setTool(null);//đặt canvas bằng null
    boxContentHole.innerHTML = "";
    panner_region_hole.classList.remove("active");
    refesh_btn();
    get_obj_product().clearHighlight(scroll_container);
    setNameEventActivate(null);
});


btn_judment_hole.addEventListener("click",async ()=>{
        let obj_hole_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_HOLE,HoleItemInspector,"setHoleItems");
        console.log("Bạn vừa nhấn vào phán định Hole");
        const status_selected = checkSelected(selected);
        if (!status_selected) return;
        write_log_clear(log_hole,"");
        const box_detect = obj_hole_item_inspector.getRectangle();
        if (!box_detect) {
            write_log_clear(log_hole,"Hiện tại chưa vẽ khung ARM Sensor hãy tiến hành vẽ");
            return;
        }
        console.log("box_detect gửi đi:", box_detect);
        const data_send = {
            "select": selected,
            "box": box_detect,
            "WidthCanvas": WIDTH_IMG_SHAPE
        };
        console.log("data_send gửi đi:", data_send);
        write_log_clear(log_hole,"⏳ Đang xử lý phán định ARM Sensor...");
        try {
            const result_judment = await postData("/law_regulation/hole/run_model", data_send);
            console.log("result_judment nhận được:", result_judment);
            if (result_judment && result_judment.ok) {
                const data_res = result_judment.data;
                const objects = data_res?.objects || [];
                if (objects.length === 0) {
                    write_log_clear(log_hole,"⚠️ Không tìm thấy đối tượng ARM Sensor nào trong vùng đã chọn.");
                    return;
                }
                write_log_clear(log_hole,`✅ Phán định thành công! Đã phát hiện ${objects.length} đối tượng.`);
                obj_hole_item_inspector.removeBoxs();
                canvasManager.clearShapeCanvas();
                obj_hole_item_inspector.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
                objects.forEach((obj) => {
                    const imgWidthReal = obj.image_width || data_res.width || 2048;
                    const detectData = {
                        x1: obj.bbox.x1,
                        y1: obj.bbox.y1,
                        x2: obj.bbox.x2,
                        y2: obj.bbox.y2,
                        className: obj.class_name,
                        confidence: obj.confidence,
                        imgWidthReal: imgWidthReal,
                        canvasWidth: WIDTH_IMG_SHAPE,
                        classId: obj.class_id
                    };
                    obj_hole_item_inspector.appendBoxes(detectData);   // cai nay la mang nhe
                    write_log_append(log_hole,`📍 Tìm thấy: ${obj.class_name}`);
                    write_log_append(log_hole,` - Độ tin cậy: ${(obj.confidence * 100).toFixed(2)}%`);
                });
                    obj_hole_item_inspector.drawDetectedObjects(canvasManager);
            } else {
                const error_msg = result_judment?.message || "Lỗi không xác định từ Server.";
                write_log_clear(log_hole,`❌ THẤT BẠI:\n${error_msg}`);
                if (result_judment?.error_code) {
                    write_log_append(log_hole,`Mã lỗi: ${result_judment.error_code} (${result_judment.error_name})`);
                }
            }
        } catch (err) {
            write_log_clear(log_hole,`❌ Lỗi kết nối mạng hoặc lỗi hệ thống client:\n${err.message}`);
        }

});


function func_callback_click_on_line_have_aready(coordinate){
        let obj_hole_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_HOLE,HoleItemInspector,"setHoleItems");
        if (!obj_hole_item_inspector) return;
        const rect = obj_hole_item_inspector.getRectangle();
        if (!rect) return;
        if (obj_hole_item_inspector.isPointOnRoiBorder(coordinate.x, coordinate.y,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE)) {
            boxContentHole.innerHTML = "";
            obj_region_hole_canvas.have_return =  true; 
            boxContentHole.appendChild(createHoleTable(rect));
        }

    
}

export function event_transition_items(){
        boxContentHole.innerHTML = ""; 
        get_obj_product().highlightItems(scroll_container,ItemsInspector.TYPE_HOLE,"rectangle"); 
        let obj_hole_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_HOLE,HoleItemInspector,"setHoleItems");
        obj_region_hole_canvas.reset();
        canvasManager.clearShapeCanvas();
        if (obj_hole_item_inspector){
            console.log("obj_hole_item_inspector.boxs",obj_hole_item_inspector.boxs);
            obj_hole_item_inspector.drawDetectedObjects(canvasManager);
            obj_hole_item_inspector.drawAll(canvasManager,COLOR_RECT_SHAPE_REGION_DETECT);
            console.log("Hoàn thành việc chuyển đổi và khôi phục trạng thái hiển thị ARM Sensor.");
        }
}




function createHoleTable(data_hole = null) {
    let obj_hole_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_HOLE,HoleItemInspector,"setHoleItems");
    const wrapper = document.createElement("div");
    wrapper.id = "measure-hole-wrapper";

    const table = document.createElement("table");
    table.className = "measure-weld-width-config-table";
    table.id = "measure-hole-table";

    const rows = [
        "Tên hình"
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
        input.id = `measure-hole-input-${index}`;
        input.type = "text";
        input.placeholder = "Nhập tên hình";

        if (data_hole) {
            input.value = data_hole.name ?? "Lỗ thủng";
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
    btnAccept.id = "btn-accept-hole";
    btnAccept.textContent = "Chấp nhận";

    btnAccept.addEventListener("click", () => {
        const nameHole = document.getElementById("measure-hole-input-0")?.value || "";

        const objHoleCropROI = new ModelRectangle(
            0,
            nameHole,
            data_hole.xStart,
            data_hole.yStart,
            data_hole.xEnd,
            data_hole.yEnd
        );

        console.log("objHole", objHoleCropROI);
        const resultValidate = objHoleCropROI.validate();

        if (resultValidate.isValid) {
            if (typeof boxContentHole !== "undefined") {
                boxContentHole.innerHTML = "";
            }

            console.log("obj_hole_item_inspector", obj_hole_item_inspector);

            // Gọi các phương thức đã đổi tên trong HoleItemInspector
            obj_hole_item_inspector.setRectangle(objHoleCropROI);
            write_log_clear(log_hole,"✅ Dữ liệu hợp lệ.");
           
            get_obj_product().highlightItems(scroll_container,ItemsInspector.TYPE_HOLE,"rectangle"); 
            if (typeof obj_region_hole_canvas !== "undefined") {
                obj_region_hole_canvas.is_available_one_line = false;
                obj_region_hole_canvas.reset();
            }

            canvasManager.clearShapeCanvas();
            obj_hole_item_inspector.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
            obj_hole_item_inspector.drawDetectedObjects(canvasManager);
        } else {
            let alertMessage = "❌ THÔNG BÁO LỖI DỮ LIỆU NHẬP VÀO:\n\n";
            write_log_clear(log_hole,alertMessage);
            resultValidate.errors.forEach(err => {
                write_log_append(log_hole,`📍 ${err.rowName}`);
                write_log_append(log_hole,` - Giá trị hiện tại: "${err.currentVal}"`);
                write_log_append(log_hole,` - Yêu cầu: ${err.expected}`);
            });
        }
    });

    const btnClear = document.createElement("button");
    btnClear.className = "btn btn-clear";
    btnClear.id = "btn-clear-hole";
    btnClear.textContent = "Xóa";

    btnClear.addEventListener("click", () => {
        const inp = document.getElementById("measure-hole-input-0");
        if (inp) inp.value = "";
    });

    actions.appendChild(btnAccept);
    actions.appendChild(btnClear);

    wrapper.appendChild(table);
    wrapper.appendChild(actions);

    return wrapper;
}



