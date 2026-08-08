console.log("Vào Scratched pipe tool");
import { ModelRectangle } from '../model/model_rectangle.js'; 
import {scroll_container,canvasManager,WIDTH_IMG_SHAPE}from "../common_value.js"
import {obj_region_scratched_pipe_canvas,boxContentScratchedPipe,get_obj_product,selected,checkSelected,additional_events,COLOR_RECT_SHAPE_REGION_DETECT,
    write_log_clear,write_log_append,create_obj_cross_item,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE,panner_region_scratched_pipe,refesh_btn,setNameEventActivate
} from "./common_value_tool.js"   
import {RectangleDrawer} from "../canvas/rectangel_drawer_canvas.js"
import {ItemsInspector} from "../services/items_inspector.js"
import {ScratchedPipeItemInspector} from "../services/scratched_pipe_inspector.js"
import {postData} from "../utills/api.js";



additional_events.set("scratched-pipe-tool", event_transition_items);
const btn_judment_scratched_pipe = document.getElementById("btn-judment-scratched-pipe");
const log_scratched_pipe = document.getElementById("log-scratched-pipe");
const btn_exit_scratch = document.getElementById("btn-exit-scratch");



obj_region_scratched_pipe_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT,func_callback_click_on_rect);
obj_region_scratched_pipe_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_RIGHT_RECT,func_callback_click_mouse_right_into_line);
obj_region_scratched_pipe_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT_HAVE_ALREADY,func_callback_click_on_line_have_aready);


btn_exit_scratch.addEventListener("click",()=>{
    console.log("Bạn vừa nhấn vào thoát Frame");
    canvasManager.clearShapeCanvas();
    canvasManager.clearPreviewCanvas();
    canvasManager.setTool(null);//đặt canvas bằng null
    boxContentScratchedPipe.innerHTML = "";
    panner_region_scratched_pipe.classList.remove("active");
    refesh_btn();
    get_obj_product().clearHighlight(scroll_container);
    setNameEventActivate(null);
});

function func_callback_click_on_rect(data_shape){
    console.log("click vào khung",data_shape);
    console.log("boxContentArmSensor",boxContentScratchedPipe);
    boxContentScratchedPipe.appendChild(createScratchedPipeTable(data_shape)); 
}


function func_callback_click_mouse_right_into_line(coordinate){
    boxContentScratchedPipe.innerHTML = ""; 
    let obj_scratched_pipe_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_SCRATCHED_PIPE,ScratchedPipeItemInspector,"setScratchedPipeItems");
    if (!obj_scratched_pipe_item_inspector){
        console.log("Ko tao duoc du lieu");
        return;}
    let result_find_line  = obj_scratched_pipe_item_inspector.isPointOnRoiBorder(coordinate.x,coordinate.y,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE);
    if (result_find_line){
        console.log("Click trúng đường viền");
        obj_scratched_pipe_item_inspector.removeRectangle()
        obj_scratched_pipe_item_inspector.clearBoxes();;
        canvasManager.clearShapeCanvas();
        obj_scratched_pipe_item_inspector.drawRectangle(canvasManager,COLOR_RECT_SHAPE_REGION_DETECT);
        get_obj_product().highlightItems(scroll_container,ItemsInspector.TYPE_SCRATCHED_PIPE,"rectangle");  
            
    }
}



function func_callback_click_on_line_have_aready(coordinate){
        let obj_scratched_pipe_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_SCRATCHED_PIPE,ScratchedPipeItemInspector,"setScratchedPipeItems");
        if (!obj_scratched_pipe_item_inspector) return;
        const rect = obj_scratched_pipe_item_inspector.getRectangle();
        if (!rect) return;
        if (obj_scratched_pipe_item_inspector.isPointOnRoiBorder(coordinate.x, coordinate.y,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE)) {
            boxContentScratchedPipe.innerHTML = "";
            obj_region_scratched_pipe_canvas.have_return =  true; 
            boxContentScratchedPipe.appendChild(createScratchedPipeTable(rect));
        }

}

export function event_transition_items(){
        boxContentScratchedPipe.innerHTML = ""; 
        obj_region_scratched_pipe_canvas.reset();
        get_obj_product().highlightItems(scroll_container,ItemsInspector.TYPE_SCRATCHED_PIPE,"rectangle");  
        canvasManager.clearShapeCanvas();
        let obj_scratched_pipe_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_SCRATCHED_PIPE,ScratchedPipeItemInspector,"setScratchedPipeItems");
        if (obj_scratched_pipe_item_inspector){
            obj_scratched_pipe_item_inspector.drawRectangle(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
            obj_scratched_pipe_item_inspector.drawScratchedItem(canvasManager);
        }
        console.log("Hoàn thành việc chuyển đổi và khôi phục trạng thái hiển thị ARM Sensor.");
}


function createScratchedPipeTable(data_item = null) {
    let obj_scratched_pipe_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_SCRATCHED_PIPE,ScratchedPipeItemInspector,"setScratchedPipeItems");
    const wrapper = document.createElement("div");
    wrapper.id = "measure-scratched-item-wrapper";

    const table = document.createElement("table");
    table.className = "measure-weld-width-config-table";
    table.id = "measure-scratched-item-table";

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
        input.id = `measure-scratched-item-input-${index}`;
        input.type = "text";
        input.placeholder = "Nhập tên hình";

        if (data_item) {
            input.value = data_item.name ?? "Vết trầy xước";
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
    btnAccept.id = "btn-accept-scratched-item";
    btnAccept.textContent = "Chấp nhận";

    btnAccept.addEventListener("click", () => {
        const nameItem = document.getElementById("measure-scratched-item-input-0")?.value || "";

        const objItemCropROI = new ModelRectangle(
            0,
            nameItem,
            data_item.xStart,
            data_item.yStart,
            data_item.xEnd,
            data_item.yEnd
        );

        console.log("objScratchedItem", objItemCropROI);
        const resultValidate = objItemCropROI.validate();

        if (resultValidate.isValid) {
            if (typeof boxContentScratchedPipe !== "undefined") {
                boxContentScratchedPipe.innerHTML = "";
            }
            console.log("obj_scratched_pipe_item_inspector", obj_scratched_pipe_item_inspector);
            // Gọi các phương thức từ ScratchedItemInspector
            obj_scratched_pipe_item_inspector.setRectangle(objItemCropROI);
            write_log_clear(log_scratched_pipe,"✅ Dữ liệu hợp lệ.");

            if (typeof obj_region_scratched_pipe_canvas !== "undefined") {
                obj_region_scratched_pipe_canvas.is_available_one_line = false;
                obj_region_scratched_pipe_canvas.reset();
            }

            canvasManager.clearShapeCanvas();
            obj_scratched_pipe_item_inspector.drawRectangle(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
            obj_scratched_pipe_item_inspector.drawScratchedItem(canvasManager);
            get_obj_product().highlightItems(scroll_container,ItemsInspector.TYPE_SCRATCHED_PIPE,"rectangle");  

        } else {
            let alertMessage = "❌ THÔNG BÁO LỖI DỮ LIỆU NHẬP VÀO:\n\n";
            write_log_clear(log_scratched_pipe,alertMessage);
            resultValidate.errors.forEach(err => {
                write_log_append(log_scratched_pipe,`📍 ${err.rowName}`);
                write_log_append(log_scratched_pipe,` - Giá trị hiện tại: "${err.currentVal}"`);
                write_log_append(log_scratched_pipe,` - Yêu cầu: ${err.expected}`);
            });
        }
    });

    const btnClear = document.createElement("button");
    btnClear.className = "btn btn-clear";
    btnClear.id = "btn-clear-scratched-item";
    btnClear.textContent = "Xóa";

    btnClear.addEventListener("click", () => {
        const inp = document.getElementById("measure-scratched-item-input-0");
        if (inp) inp.value = "";
    });

    actions.appendChild(btnAccept);
    actions.appendChild(btnClear);

    wrapper.appendChild(table);
    wrapper.appendChild(actions);

    return wrapper;
}
btn_judment_scratched_pipe.addEventListener("click",async ()=>{
        let obj_scratched_pipe_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_SCRATCHED_PIPE,ScratchedPipeItemInspector,"setScratchedPipeItems");
        console.log("Phán định vết xước ống");
        const status_selected = checkSelected(selected);
        if (!status_selected) return;
        write_log_clear(log_scratched_pipe,"");
        const box_detect = obj_scratched_pipe_item_inspector.getRectangle();
        if (!box_detect) {
            write_log_clear(log_scratched_pipe,"Hiện tại chưa vẽ khung ARM Sensor hãy tiến hành vẽ");
            return;
        }
        console.log("box_detect gửi đi:", box_detect);
        // 3. Chuẩn bị dữ liệu để gửi lên API
        const data_send = {
            "select": selected,
            "box": box_detect,
            "WidthCanvas": WIDTH_IMG_SHAPE
        };
        console.log("data_send gửi đi:", data_send);
        write_log_clear(log_scratched_pipe,"⏳ Đang xử lý phán định ARM Sensor...");
        try {
            // 4. Gọi API gửi yêu cầu phán định
            const result_judment = await postData("/law_regulation/scratched_pipe/judment_item", data_send);
            console.log("result_judment nhận được:", result_judment);
            if (result_judment && result_judment.ok) {
                const data_res = result_judment.data;
                const objects = data_res?.objects || [];
                if (objects.length === 0) {
                    write_log_clear(log_scratched_pipe,"⚠️ Không tìm thấy đối tượng ARM Sensor nào trong vùng đã chọn.");
                    return;
                }
                write_log_clear(log_scratched_pipe,`✅ Phán định thành công! Đã phát hiện ${objects.length} đối tượng.`);
                // Xóa canvas hình vẽ cũ và vẽ lại khung vùng chứa (ARM Sensor) chính trước
                canvasManager.clearShapeCanvas();
                obj_scratched_pipe_item_inspector.clearBoxes();
                obj_scratched_pipe_item_inspector.drawRectangle(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
                objects.forEach((obj) => {
                    const imgWidthReal = obj.image_width || data_res.width || 2048;
                    // Gọi hàm vẽ lẻ của Inspector (đã tự xử lý scale tọa độ bên trong)
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
                    obj_scratched_pipe_item_inspector.addBox(detectData);   // cai nay la mang nhe
                    write_log_append(log_scratched_pipe,`📍 Tìm thấy: ${obj.class_name}`);
                    write_log_append(log_scratched_pipe,` - Độ tin cậy: ${(obj.confidence * 100).toFixed(2)}%`);
                });
                obj_scratched_pipe_item_inspector.drawScratchedItem(canvasManager);
                   
            } else {
                const error_msg = result_judment?.message || "Lỗi không xác định từ Server.";
                write_log_clear(log_scratched_pipe,`❌ THẤT BẠI:\n${error_msg}`);
                if (result_judment?.error_code) {
                    write_log_append(log_scratched_pipe,`Mã lỗi: ${result_judment.error_code} (${result_judment.error_name})`);
                }
            }
    
        } catch (err) {
            // 6. Xử lý lỗi kết nối mạng, server sập hoặc lỗi logic client
            console.error("Lỗi kết nối / xử lý API:", err);
            write_log_clear(log_scratched_pipe,`❌ Lỗi kết nối mạng hoặc lỗi hệ thống client:\n${err.message}`);
        }

});

