console.log("Vào File permeable membrane Tool");
import { ModelRectangle } from '../model/model_rectangel.js'; 
import {scroll_container,canvasManager,WIDTH_IMG_SHAPE}from "../common_value.js"
import {additional_events,obj_region_permeable_membrane_canvas,boxContentPermeableMembrane,get_obj_product,selected,checkSelected
} from "./common_value_tool.js"   
import {RectangleDrawer} from "../canvas/rectangel_drawer_canvas.js"
import {ItemsInspector} from "../services/items_inspector.js"
import {PermeableMembraneInspector} from "../services/permeable_membrane_inspector.js"
import {postData} from "../utills/api.js";



let color_rect_shape = "#0000FF";
additional_events.set("permeable-membrane_tool", event_transition_items);
let obj_permemble_membrane_item_inspector = null;
const btn_judment_permeable_membrane = document.getElementById("btn-judment-permeable-membrane");
const log_permeable_membrane = document.getElementById("log-permeable-membrane");

obj_region_permeable_membrane_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT,func_callback_click_on_rect);
obj_region_permeable_membrane_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_RIGHT_RECT,func_callback_click_mouse_right_into_line);
obj_region_permeable_membrane_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT_HAVE_ALREADY,func_callback_click_on_line_have_aready);


/**
 * Phán định Permeable Membrane.
 */
btn_judment_permeable_membrane.addEventListener("click", async () => {
    console.log("Bạn vừa nhấn vào phán định Permeable Membrane");
    if (!checkSelected(selected)) return;
    write_log_clear("");
    const membrane = obj_permemble_membrane_item_inspector.getMembrane();
    if (!membrane) {
        write_log_clear("Hiện tại chưa vẽ vùng Permeable Membrane.");
        return;
    }
    const dataSend = {
        select: selected,
        box: membrane,
        WidthCanvas: WIDTH_IMG_SHAPE
    };
    console.log("data_send:", dataSend);
    write_log_clear("⏳ Đang xử lý phán định Permeable Membrane...");
    try {
        const result = await postData("/law_regulation/permemble_membrane/judment_item", dataSend);
        console.log(result);
        if (!result?.ok) {
            write_log_clear(`❌ ${result?.message || "Lỗi không xác định."}`);
            return;
        }
        const { width, objects } = result.data;
        const polygonBorder = objects?.polygon_border || [];
        const polygonInner = objects?.polygon_inner || [];
        obj_permemble_membrane_item_inspector.setDetectResult(
            polygonBorder,
            polygonInner,
            width,
            WIDTH_IMG_SHAPE
        );
        obj_permemble_membrane_item_inspector.drawAllMembranes(canvasManager,color_rect_shape);
        if (polygonBorder.length) write_log_append("✔ Phát hiện Border membrane");
        if (polygonInner.length) write_log_append("✔ Phát hiện Inner membrane");
        if (!polygonBorder.length && !polygonInner.length) write_log_append("⚠ Không phát hiện membrane.");
        write_log_append("✅ Hoàn thành.");
    } catch (err) {
        console.error("Lỗi kết nối / xử lý API:", err);
        write_log_clear(`❌ Lỗi kết nối mạng hoặc lỗi hệ thống client:\n${err.message}`);
    }
});


function event_transition_items(){
    console.log("event_transition_items");
    boxContentPermeableMembrane.innerHTML = ""; 
    obj_permemble_membrane_item_inspector = get_obj_product().find_item_object_corresponding(String(selected?.frame_id),String(selected?.items_id),ItemsInspector.TYPE_PERMEABLE_MEMBRANE);
        if (!obj_permemble_membrane_item_inspector){
                let obj_items_inspector = get_obj_product().get_item_object(String(selected?.frame_id),String(selected?.items_id));
                obj_permemble_membrane_item_inspector =  new PermeableMembraneInspector();
                obj_items_inspector.setPermeableMembraneItems(obj_permemble_membrane_item_inspector);
        }
        obj_region_permeable_membrane_canvas.reset();
        canvasManager.clearShapeCanvas();
        obj_permemble_membrane_item_inspector.drawAllMembranes(canvasManager, color_rect_shape);
        const savedBoxs = obj_permemble_membrane_item_inspector.getBoxs(); // Hàm getter trả về mảng this.boxs
        console.log("savedBoxs",savedBoxs);
        if (Array.isArray(savedBoxs) && savedBoxs.length > 0) {
            console.log(`Tiến hành vẽ lại ${savedBoxs.length} đối tượng con đã lưu...`);
            savedBoxs.forEach((detectData) => {
                detectData.canvasWidth = WIDTH_IMG_SHAPE;
                obj_permemble_membrane_item_inspector.drawDetectedObject(canvasManager, detectData);
            });
        } else {
            console.log("Danh sách đối tượng nhận diện trống (chưa thực hiện phán định hoặc đối tượng mới tạo).");
        }
        console.log("Hoàn thành việc chuyển đổi và khôi phục trạng thái hiển thị permemble membrane");
}



function func_callback_click_on_rect(data_shape){
    console.log("click vào khung",data_shape);
    console.log("boxContentPermeableMembrane",boxContentPermeableMembrane);
    boxContentPermeableMembrane.appendChild(createPermeableMembraneTable(data_shape)); 
}

function func_callback_click_mouse_right_into_line(coordinate){
        boxContentPermeableMembrane.innerHTML = ""; 
        let result_find_line  = obj_permemble_membrane_item_inspector.isPointOnMembraneBorder(coordinate.x,coordinate.y);
        if (result_find_line){
                console.log("Click trúng đường viền");
                obj_permemble_membrane_item_inspector.removeMembrane();
                obj_permemble_membrane_item_inspector.removeBoxs();
                canvasManager.clearShapeCanvas();
                obj_permemble_membrane_item_inspector.drawAllMembranes(canvasManager);
        }
}

function func_callback_click_on_line_have_aready(coordinate){
        if (!obj_permemble_membrane_item_inspector) return;
                const rect = obj_permemble_membrane_item_inspector.getMembrane();
            if (!rect) return;
            if (obj_permemble_membrane_item_inspector.isPointOnMembraneBorder(coordinate.x, coordinate.y)) {
                console.log("da vao line");
                boxContentPermeableMembrane.innerHTML = "";
                obj_region_permeable_membrane_canvas.have_return =  true; 
                boxContentPermeableMembrane.appendChild(createPermeableMembraneTable(rect));
            }
}


function createPermeableMembraneTable(data_shape = null) {
    const wrapper = document.createElement("div");
    wrapper.id = "permeable-membrane-shape-wrapper";
    
    const table = document.createElement("table");
    table.className = "measure-weld-width-config-table";
    table.id = "permeable-membrane-table";
    
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
        input.id = `permeable-membrane-input-${index}`;
        input.type = "text";
        input.placeholder = "Nhập tên hình màng thấm";
        
        if (data_shape) {
            input.value = data_shape.name ?? "Màng bám thấm";
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
    btnAccept.id = "btn-accept-membrane-shape";
    btnAccept.textContent = "Chấp nhận";
    btnAccept.addEventListener("click", () => {

        const nameShape = document.getElementById("permeable-membrane-input-0")?.value || "";
        const objRectangle = new ModelRectangle(
            0,
            nameShape,
            data_shape.xStart,
            data_shape.yStart,
            data_shape.xEnd,
            data_shape.yEnd
        );
        
        console.log("objRectangle", objRectangle);
        const resultValidate = objRectangle.validate();
        
        if (resultValidate.isValid) {
            boxContentPermeableMembrane.innerHTML = "";
            console.log("Màng bám thấm", obj_permemble_membrane_item_inspector);
            
            // Sử dụng logic hàm đã đổi tên tương ứng với màng bán thấm
            obj_permemble_membrane_item_inspector.setMembrane(objRectangle);
            write_log_clear("✅ Dữ liệu hợp lệ.");
            
            obj_region_permeable_membrane_canvas.is_available_one_line = false;
            obj_region_permeable_membrane_canvas.reset();
            canvasManager.clearShapeCanvas();
            obj_permemble_membrane_item_inspector.drawAllMembranes(canvasManager, color_rect_shape);

        } else {
            let alertMessage = "❌ THÔNG BÁO LỖI DỮ LIỆU NHẬP VÀO:\n\n";
            write_log_clear(alertMessage);
            resultValidate.errors.forEach(err => {
                write_log_append(`📍 ${err.rowName}`);
                write_log_append(` - Giá trị hiện tại: "${err.currentVal}"`);
                write_log_append(` - Yêu cầu: ${err.expected}`);
            });
        }
    });
    
    const btnClear = document.createElement("button");
    btnClear.className = "btn btn-clear";
    btnClear.id = "btn-clear-membrane-shape";
    btnClear.textContent = "Xóa";
    btnClear.addEventListener("click", () => {
        const inp = document.getElementById("permeable-membrane-input-0");
        if (inp) inp.value = "";
    });
    
    actions.appendChild(btnAccept);
    actions.appendChild(btnClear);
    wrapper.appendChild(table);
    wrapper.appendChild(actions);
    
    return wrapper;
}
function write_log_clear(text){
    log_permeable_membrane.textContent = text;
}

function write_log_append(text){
    log_permeable_membrane.style.whiteSpace = "pre-line"; 
    log_permeable_membrane.textContent += text + "\n";
}

