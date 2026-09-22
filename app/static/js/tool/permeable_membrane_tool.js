console.log("Vào File permeable membrane Tool");
import { ModelRectangle } from '../model/model_rectangle.js'; 
import {scroll_container,canvasManager,WIDTH_IMG_SHAPE}from "../common_value.js"
import {additional_events,obj_region_permeable_membrane_canvas,boxContentPermeableMembrane,get_obj_product,write_log_clear,write_log_append,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE,
    selected,checkSelected,COLOR_RECT_SHAPE_REGION_DETECT,create_obj_cross_item,refesh_btn,setNameEventActivate,panner_permeable_membrane
} from "./common_value_tool.js"   
import {RectangleDrawer} from "../canvas/rectangel_drawer_canvas.js"
import {ItemsInspector} from "../services/items_inspector.js"
import {PermeableMembraneInspector} from "../services/permeable_membrane_inspector.js"
import {postData} from "../utills/api.js";



additional_events.set("permeable-membrane_tool", event_transition_items);
const btn_judment_permeable_membrane = document.getElementById("btn-judment-permeable-membrane");
const log_permeable_membrane = document.getElementById("log-permeable-membrane");
const btn_exit_permeable_membrane = document.getElementById("btn-exit-permeable-membrane");

obj_region_permeable_membrane_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT,func_callback_click_on_rect);
obj_region_permeable_membrane_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_RIGHT_RECT,func_callback_click_mouse_right_into_line);
obj_region_permeable_membrane_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT_HAVE_ALREADY,func_callback_click_on_line_have_aready);


/**
 * Phán định Permeable Membrane.
 */
btn_judment_permeable_membrane.addEventListener("click", async () => {
    console.log("Bạn vừa nhấn vào phán định Permeable Membrane");
    let obj_permemble_membrane_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_PERMEABLE_MEMBRANE,PermeableMembraneInspector,"setPermeableMembraneItems");
    if (!checkSelected(selected)) return;
    if (!obj_permemble_membrane_item_inspector){console.log("Đối tượng chưa được tạo");return;}
    write_log_clear(log_permeable_membrane,"");
    const membrane = obj_permemble_membrane_item_inspector.getMembrane();
    if (!membrane) {
        write_log_clear(log_permeable_membrane,"Hiện tại chưa vẽ vùng Permeable Membrane.");
        return;
    }
    const dataSend = {
        select: selected,
        box: membrane,
        WidthCanvas: WIDTH_IMG_SHAPE
    };
    console.log("data_send:", dataSend);
    write_log_clear(log_permeable_membrane,"⏳ Đang xử lý phán định Permeable Membrane...");
    try {
        const result = await postData("/law_regulation/permeable_membrane/run_model", dataSend);
        console.log(result);
        if (!result?.ok) {
            write_log_clear(log_permeable_membrane,`❌ ${result?.message || "Lỗi không xác định."}`);
            return;
        }
        obj_permemble_membrane_item_inspector.removePolygons();
        const { width, objects } = result.data;
        const polygonBorder = objects?.polygon_border || [];
        const polygonInner = objects?.polygon_inner || [];

        obj_permemble_membrane_item_inspector.setDetectResult(
            polygonBorder,
            polygonInner,
            width,
            WIDTH_IMG_SHAPE
        );
        canvasManager.clearShapeCanvas();
        obj_permemble_membrane_item_inspector.drawRectangle(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
        obj_permemble_membrane_item_inspector.drawPolygons(canvasManager,COLOR_RECT_SHAPE_REGION_DETECT);
        if (polygonBorder.length) write_log_append(log_permeable_membrane,"✔ Phát hiện Border membrane");
        if (polygonInner.length) write_log_append(log_permeable_membrane,"✔ Phát hiện Inner membrane");
        if (!polygonBorder.length && !polygonInner.length) write_log_append(log_permeable_membrane,"⚠ Không phát hiện membrane.");
        write_log_append(log_permeable_membrane,"✅ Hoàn thành.");
        } catch (err) {
            write_log_clear(log_permeable_membrane,`❌ Lỗi kết nối mạng hoặc lỗi hệ thống client:\n${err.message}`);
        }
});
 

export function event_transition_items(){
    console.log("event_transition_items");
    boxContentPermeableMembrane.innerHTML = ""; 
    canvasManager.clearShapeCanvas();
    obj_region_permeable_membrane_canvas.reset();
    get_obj_product().highlightItems(scroll_container,ItemsInspector.TYPE_PERMEABLE_MEMBRANE,"rectangle");  
    let obj_permemble_membrane_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_PERMEABLE_MEMBRANE,PermeableMembraneInspector,"setPermeableMembraneItems");
    if (obj_permemble_membrane_item_inspector){
        obj_permemble_membrane_item_inspector.drawRectangle(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
        obj_permemble_membrane_item_inspector.drawPolygons(canvasManager, WIDTH_IMG_SHAPE);
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
        let obj_permemble_membrane_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_PERMEABLE_MEMBRANE,PermeableMembraneInspector,"setPermeableMembraneItems");
        let result_find_line  = obj_permemble_membrane_item_inspector.isPointOnMembraneBorder(coordinate.x,coordinate.y,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE);
        if (result_find_line){
                console.log("Click trúng đường viền");
                obj_permemble_membrane_item_inspector.removeMembrane();
                canvasManager.clearShapeCanvas();
                obj_permemble_membrane_item_inspector.drawRectangle(canvasManager);
                get_obj_product().highlightItems(scroll_container,ItemsInspector.TYPE_PERMEABLE_MEMBRANE,"rectangle");  
        }
}

function func_callback_click_on_line_have_aready(coordinate){
        let obj_permemble_membrane_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_PERMEABLE_MEMBRANE,PermeableMembraneInspector,"setPermeableMembraneItems");
        if (!obj_permemble_membrane_item_inspector) return;
                const rect = obj_permemble_membrane_item_inspector.getMembrane();
            if (!rect) return;
            if (obj_permemble_membrane_item_inspector.isPointOnMembraneBorder(coordinate.x, coordinate.y,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE)) {
                console.log("da vao line");
                boxContentPermeableMembrane.innerHTML = "";
                obj_region_permeable_membrane_canvas.have_return =  true; 
                boxContentPermeableMembrane.appendChild(createPermeableMembraneTable(rect));
            }
}

btn_exit_permeable_membrane.addEventListener("click",()=>{
    console.log("Nhấn vào đóng Frame");
    canvasManager.clearShapeCanvas();
    canvasManager.clearPreviewCanvas();
    canvasManager.setTool(null);//đặt canvas bằng null
    boxContentPermeableMembrane.innerHTML = "";
    panner_permeable_membrane.classList.remove("active");
    refesh_btn();
    get_obj_product().clearHighlight(scroll_container);
    setNameEventActivate(null);
});

function createPermeableMembraneTable(data_shape = null) {
    let obj_permemble_membrane_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_PERMEABLE_MEMBRANE,PermeableMembraneInspector,"setPermeableMembraneItems");
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
            write_log_clear(log_permeable_membrane,"✅ Dữ liệu hợp lệ.");
            obj_region_permeable_membrane_canvas.is_available_one_line = false;
            obj_region_permeable_membrane_canvas.reset();
            canvasManager.clearShapeCanvas();
            obj_permemble_membrane_item_inspector.drawRectangle(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
            obj_permemble_membrane_item_inspector.drawPolygons(canvasManager,COLOR_RECT_SHAPE_REGION_DETECT);
            get_obj_product().highlightItems(scroll_container,ItemsInspector.TYPE_PERMEABLE_MEMBRANE,"rectangle");  

        } else {
            let alertMessage = "❌ THÔNG BÁO LỖI DỮ LIỆU NHẬP VÀO:\n\n";
            write_log_clear(log_permeable_membrane,alertMessage);
            resultValidate.errors.forEach(err => {
                write_log_append(log_permeable_membrane,`📍 ${err.rowName}`);
                write_log_append(log_permeable_membrane,` - Giá trị hiện tại: "${err.currentVal}"`);
                write_log_append(log_permeable_membrane,` - Yêu cầu: ${err.expected}`);
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

