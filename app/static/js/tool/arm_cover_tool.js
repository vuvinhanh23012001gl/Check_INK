console.log("Vào File Arm Cover Tool");
import { ModelRectangle } from '../model/model_rectangle.js'; 
import {scroll_container,canvasManager,WIDTH_IMG_SHAPE}from "../common_value.js"
import {additional_events,obj_region_arm_cover_canvas,boxContentArmCover,get_obj_product,selected,checkSelected,
    COLOR_RECT_SHAPE_REGION_DETECT,write_log_clear,write_log_append,create_obj_cross_item,
    ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE,refesh_btn,setNameEventActivate,panner_region_cover_sensor
} from "./common_value_tool.js"   
import {RectangleDrawer} from "../canvas/rectangel_drawer_canvas.js"
import {ItemsInspector} from "../services/items_inspector.js"
import {ArmCoverItemInspector} from "../services/arm_cover_item_inspector.js"
import {postData} from "../utills/api.js";


additional_events.set("arm_cover_tool", event_transition_items);
const btn_judment_arm_sensor = document.getElementById("btn-judment-arm-cover");
const log_arm_cover = document.getElementById("log-arm-cover");
const btn_exit_arm_cover = document.getElementById("btn-exit-arm-cover");

obj_region_arm_cover_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT,func_callback_click_on_rect);
obj_region_arm_cover_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_RIGHT_RECT,func_callback_click_mouse_right_into_line);
obj_region_arm_cover_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT_HAVE_ALREADY,func_callback_click_on_line_have_aready);


btn_exit_arm_cover.addEventListener("click",()=>{
    console.log("Nhấn vào đóng Frame");
    canvasManager.clearShapeCanvas();
    canvasManager.clearPreviewCanvas();
    canvasManager.setTool(null);//đặt canvas bằng null
    boxContentArmCover.innerHTML = "";
    panner_region_cover_sensor.classList.remove("active");
    refesh_btn();
    get_obj_product().clearHighlight(scroll_container);
    setNameEventActivate(null);
});
    

btn_judment_arm_sensor.addEventListener("click",async ()=>{
    console.log("Bạn vừa nhấn vào phán định ARM cover");
    const status_selected = checkSelected(selected);
       if (!status_selected) return;
       write_log_clear(log_arm_cover,"");
       let obj_arm_cover_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_ARM_COVER,ArmCoverItemInspector,"setArmCoverItems");
       // 2. Lấy thông tin hình chữ nhật ARM Sensor hiện có từ inspector
       const box_detect = obj_arm_cover_item_inspector.getRectangle();
       if (!box_detect) {
           write_log_clear(log_arm_cover,"Hiện tại chưa vẽ khung ARM Cover hãy tiến hành vẽ");
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
       write_log_clear(log_arm_cover,"⏳ Đang xử lý phán định ARM Sensor...");
       try {
           const result_judment = await postData("/law_regulation/arm_cover/judment_item", data_send);
           console.log("result_judment nhận được:", result_judment);
           if (result_judment && result_judment.ok) {
               const data_res = result_judment.data;
               const objects = data_res?.objects || [];
               if (objects.length === 0) {
                   write_log_clear(log_arm_cover,"⚠️ Không tìm thấy đối tượng ARM Sensor nào trong vùng đã chọn.");
                   return;
               }
               write_log_clear(log_arm_cover,`✅ Phán định thành công! Đã phát hiện ${objects.length} đối tượng.`);
               obj_arm_cover_item_inspector.removeBoxs();
               // Xóa canvas hình vẽ cũ và vẽ lại khung vùng chứa (ARM Sensor) chính trước
               canvasManager.clearShapeCanvas();
               obj_arm_cover_item_inspector.drawAllRectangles(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
               // Duyệt qua từng đối tượng được phát hiện từ API và vẽ lên canvas
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
                   obj_arm_cover_item_inspector.appendBoxes(detectData);   // cai nay la mang nhe
                   console.log("obj_arm_sensor_item_inspector.boxs",obj_arm_cover_item_inspector.boxs);
                   write_log_append(log_arm_cover,`📍 Tìm thấy: ${obj.class_name}`);
                   write_log_append(log_arm_cover,` - Độ tin cậy: ${(obj.confidence * 100).toFixed(2)}%`);
               });
                 obj_arm_cover_item_inspector.drawDetectedObjects(canvasManager);
           } else {
               const error_msg = result_judment?.message || "Lỗi không xác định từ Server.";
               write_log_clear(log_arm_cover,`❌ THẤT BẠI:\n${error_msg}`);
               if (result_judment?.error_code) {
                   write_log_append(log_arm_cover,`Mã lỗi: ${result_judment.error_code} (${result_judment.error_name})`);
               }
           }
   
       } catch (err) {
           // 6. Xử lý lỗi kết nối mạng, server sập hoặc lỗi logic client
           console.error("Lỗi kết nối / xử lý API:", err);
           write_log_clear(log_arm_cover,`❌ Lỗi kết nối mạng hoặc lỗi hệ thống client:\n${err.message}`);
       }
});


export function event_transition_items(){
    // console.log("event_transition_items");
    // if (selected.frame_id  == -1 ||selected.items_id  == -1 || selected.product_id ==  -1){console.log("Lỗi chưa chọn sản phâm");return;};
    let obj_arm_cover_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_ARM_COVER,ArmCoverItemInspector,"setArmCoverItems");
    boxContentArmCover.innerHTML = ""; 
    obj_arm_cover_item_inspector = get_obj_product().find_item_object_corresponding(String(selected?.frame_id),String(selected?.items_id),ItemsInspector.TYPE_ARM_COVER);
    obj_region_arm_cover_canvas.reset();
    canvasManager.clearShapeCanvas();
    get_obj_product().highlightItems(scroll_container,ItemsInspector.TYPE_ARM_COVER,"rectangle");
    if (obj_arm_cover_item_inspector){
        obj_arm_cover_item_inspector.drawAllRectangles(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
        const rectangle = obj_arm_cover_item_inspector.getRectangle(); // Hàm getter trả về mảng this.boxs
        if (rectangle){obj_arm_cover_item_inspector.drawDetectedObjects(canvasManager);}
    }
}


  


function func_callback_click_on_rect(data_shape){
    console.log("click vào khung",data_shape);
    console.log("boxContentArmCover",boxContentArmCover);
    boxContentArmCover.appendChild(createMeasureShapeTable(data_shape)); 
};


function func_callback_click_mouse_right_into_line(coordinate){
    let obj_arm_cover_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_ARM_COVER,ArmCoverItemInspector,"setArmCoverItems");
    boxContentArmCover.innerHTML = ""; 
    let result_find_line  = obj_arm_cover_item_inspector.isPointOnRectangleBorder(coordinate.x,coordinate.y,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE);
    if (result_find_line){
            console.log("Click trúng đường viền");
            obj_arm_cover_item_inspector.removeRectangle();
            obj_arm_cover_item_inspector.removeBoxs();
            canvasManager.clearShapeCanvas();
            obj_arm_cover_item_inspector.drawAllRectangles(canvasManager);
            get_obj_product().highlightItems(scroll_container,ItemsInspector.TYPE_ARM_COVER,"rectangle");
    }
};


function func_callback_click_on_line_have_aready(coordinate){
        let obj_arm_cover_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_ARM_COVER,ArmCoverItemInspector,"setArmCoverItems");
        if (!obj_arm_cover_item_inspector) return;
        const rect = obj_arm_cover_item_inspector.getRectangle();
        if (!rect) return;
        console.log("click o day 1");
        if (obj_arm_cover_item_inspector.isPointOnRectangleBorder(coordinate.x, coordinate.y,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE)) {
            console.log("da vao line");
            boxContentArmCover.innerHTML = "";
            obj_region_arm_cover_canvas.have_return =  true; 
            boxContentArmCover.appendChild(createMeasureShapeTable(rect));
        }
}


function createMeasureShapeTable(data_shape = null) {
    let obj_arm_cover_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_ARM_COVER,ArmCoverItemInspector,"setArmCoverItems");
    const wrapper = document.createElement("div");
    wrapper.id = "arm-cover-shape-wrapper";
    const table = document.createElement("table");
    table.className = "measure-weld-width-config-table";
    table.id = "arm-cover-table";
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
        input.id = `arm-cover-input-${index}`;
        input.type = "text";
        input.placeholder = "Nhập tên hình";
        if (data_shape) {
            input.value =
                data_shape.name ??
                data_shape.name ??
                "ARM Cover";
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
    btnAccept.id = "btn-accept-shape";
    btnAccept.textContent = "Chấp nhận";
    btnAccept.addEventListener("click", () => {
        const nameShape =
            document.getElementById("arm-cover-input-0")?.value || "";
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
            boxContentArmCover.innerHTML = "";
            console.log("obj_arm_cover_item_inspector",obj_arm_cover_item_inspector);
            if (!obj_arm_cover_item_inspector){
                 const status_selected = checkSelected(selected);
                 if (!status_selected){
                    write_log_clear(log_arm_cover,"Hiện tại bạn chưa chọn sản phẩm")
                    return;
                 };

            }
            obj_arm_cover_item_inspector.setRectangle(objRectangle);
            write_log_clear(log_arm_cover,"✅ Dữ liệu hợp lệ.");
            obj_region_arm_cover_canvas.is_available_one_line = false;
            obj_region_arm_cover_canvas.reset();
            canvasManager.clearShapeCanvas();
            obj_arm_cover_item_inspector.drawAllRectangles(canvasManager,COLOR_RECT_SHAPE_REGION_DETECT);
            get_obj_product().highlightItems(scroll_container,ItemsInspector.TYPE_ARM_COVER,"rectangle");
            const rectangle = obj_arm_cover_item_inspector.getRectangle() //ve lai
            if (rectangle){obj_arm_cover_item_inspector.drawDetectedObjects(canvasManager);}
        } else {
            let alertMessage = "❌ THÔNG BÁO LỖI DỮ LIỆU NHẬP VÀO:\n\n";
            write_log_clear(log_arm_cover,alertMessage);
            resultValidate.errors.forEach(err => {
                write_log_append(log_arm_cover,`📍 ${err.rowName}`);
                write_log_append(log_arm_cover,` - Giá trị hiện tại: "${err.currentVal}"`);
                write_log_append(log_arm_cover,` - Yêu cầu: ${err.expected}`);
            });
        }
    });
    const btnClear = document.createElement("button");
    btnClear.className = "btn btn-clear";
    btnClear.id = "btn-clear-shape";
    btnClear.textContent = "Xóa";
    btnClear.addEventListener("click", () => {
        const inp = document.getElementById("arm-cover-input-0");
        if (inp) inp.value = "";
    });
    actions.appendChild(btnAccept);
    actions.appendChild(btnClear);
    wrapper.appendChild(table);
    wrapper.appendChild(actions);
    return wrapper;
}



