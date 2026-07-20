console.log("Vào File Arm Sensor Tool");
import { ModelRectangle } from '../model/model_rectangel.js'; 
import {scroll_container,canvasManager,WIDTH_IMG_SHAPE}from "../common_value.js"
import {obj_region_arm_sensor_canvas,boxContentArmSensor,get_obj_product,selected,checkSelected,additional_events
} from "./common_value_tool.js"   
import {RectangleDrawer} from "../canvas/rectangel_drawer_canvas.js"
import {ItemsInspector} from "../services/items_inspector.js"
import {ArmSensorItemInspector} from "../services/arm_sensor_item_inspector.js"
import {postData} from "../utills/api.js";
let color_rect_shape = "#0000FF";
let obj_arm_sensor_item_inspector  = null;

additional_events.set("arm_sensor_tool", event_transition_items);
const btn_judment_arm_sensor = document.getElementById("btn-judment-arm-sensor");
const log_arm_sensor = document.getElementById("log-arm-sensor");

 

obj_region_arm_sensor_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT,func_callback_click_on_rect);
obj_region_arm_sensor_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_RIGHT_RECT,func_callback_click_mouse_right_into_line);
obj_region_arm_sensor_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT_HAVE_ALREADY,func_callback_click_on_line_have_aready);

/**
 * Sự kiện click nút Phán định ARM Sensor.
 * Thực hiện gửi tọa độ khung đã vẽ lên Server để nhận diện các đối tượng bên trong vùng chọn,
 * sau đó tự động tính toán tỷ lệ scale và vẽ kết quả trả về lên Canvas.
 * 
 * @async
 * @callback btnJudmentArmSensorClickCallback
 */
btn_judment_arm_sensor.addEventListener("click", async () => {
    console.log("Bạn vừa nhấn vào phán định ARM Sensor");
    // 1. Kiểm tra trạng thái lựa chọn (selected) trước khi thực hiện
    const status_selected = checkSelected(selected);
    if (!status_selected) return;
    write_log_clear("");
    // 2. Lấy thông tin hình chữ nhật ARM Sensor hiện có từ inspector
    const box_detect = obj_arm_sensor_item_inspector.getRectangle();
    if (!box_detect) {
        write_log_clear("Hiện tại chưa vẽ khung ARM Sensor hãy tiến hành vẽ");
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
    write_log_clear("⏳ Đang xử lý phán định ARM Sensor...");
    try {
        // 4. Gọi API gửi yêu cầu phán định
        const result_judment = await postData("/law_regulation/arm_sensor/judment_item", data_send);
        console.log("result_judment nhận được:", result_judment);
        if (result_judment && result_judment.ok) {
            const data_res = result_judment.data;
            const objects = data_res?.objects || [];
            if (objects.length === 0) {
                write_log_clear("⚠️ Không tìm thấy đối tượng ARM Sensor nào trong vùng đã chọn.");
                return;
            }
            write_log_clear(`✅ Phán định thành công! Đã phát hiện ${objects.length} đối tượng.`);
            // Xóa canvas hình vẽ cũ và vẽ lại khung vùng chứa (ARM Sensor) chính trước
            canvasManager.clearShapeCanvas();
            obj_arm_sensor_item_inspector.drawAllRectangles(canvasManager, color_rect_shape);
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
                obj_arm_sensor_item_inspector.appendBoxes(detectData);   // cai nay la mang nhe
                console.log("obj_arm_sensor_item_inspector.boxs",obj_arm_sensor_item_inspector.boxs);
                obj_arm_sensor_item_inspector.drawDetectedObject(canvasManager, detectData);
                write_log_append(`📍 Tìm thấy: ${obj.class_name}`);
                write_log_append(` - Độ tin cậy: ${(obj.confidence * 100).toFixed(2)}%`);
            });
        } else {
            const error_msg = result_judment?.message || "Lỗi không xác định từ Server.";
            write_log_clear(`❌ THẤT BẠI:\n${error_msg}`);
            if (result_judment?.error_code) {
                write_log_append(`Mã lỗi: ${result_judment.error_code} (${result_judment.error_name})`);
            }
        }

    } catch (err) {
        // 6. Xử lý lỗi kết nối mạng, server sập hoặc lỗi logic client
        console.error("Lỗi kết nối / xử lý API:", err);
        write_log_clear(`❌ Lỗi kết nối mạng hoặc lỗi hệ thống client:\n${err.message}`);
    }
});


function func_callback_click_on_rect(data_shape){
    console.log("click vào khung",data_shape);
    console.log("boxContentArmSensor",boxContentArmSensor);
    boxContentArmSensor.appendChild(createMeasureShapeTable(data_shape)); 
}

function func_callback_click_mouse_right_into_line(coordinate){
        boxContentArmSensor.innerHTML = ""; 
        let result_find_line  = obj_arm_sensor_item_inspector.isPointOnRectangleBorder(coordinate.x,coordinate.y);
        if (result_find_line){
                console.log("Click trúng đường viền");
                obj_arm_sensor_item_inspector.removeRectangle();
                obj_arm_sensor_item_inspector.removeBoxs();
                canvasManager.clearShapeCanvas();
                obj_arm_sensor_item_inspector.drawAllRectangles(canvasManager);
            
                //     let polygons = obj_slit_item_inspector.getPolygons();
                //    if (polygons && imageWidth!= 0){obj_slit_item_inspector.drawPolygons(canvasManager,polygons,imageWidth,WIDTH_IMG_SHAPE);}
        
        }
     
}

function func_callback_click_on_line_have_aready(coordinate) {
    if (!obj_arm_sensor_item_inspector) return;
    const rect = obj_arm_sensor_item_inspector.getRectangle();
    if (!rect) return;
    if (obj_arm_sensor_item_inspector.isPointOnRectangleBorder(coordinate.x, coordinate.y)) {
        boxContentArmSensor.innerHTML = "";
        obj_region_arm_sensor_canvas.have_return =  true; 
        boxContentArmSensor.appendChild(createMeasureShapeTable(rect));
    }
}
function event_transition_items(){
        boxContentArmSensor.innerHTML = ""; 
        obj_arm_sensor_item_inspector = get_obj_product().find_item_object_corresponding(String(selected?.frame_id),String(selected?.items_id),ItemsInspector.TYPE_ARM_SENSOR);
        if (!obj_arm_sensor_item_inspector){
                let obj_items_inspector = get_obj_product().get_item_object(String(selected?.frame_id),String(selected?.items_id));
                obj_arm_sensor_item_inspector =  new ArmSensorItemInspector();
                obj_items_inspector.setArmSensorItems(obj_arm_sensor_item_inspector);
        }
        obj_region_arm_sensor_canvas.reset();
        canvasManager.clearShapeCanvas();
        obj_arm_sensor_item_inspector.drawAllRectangles(canvasManager, color_rect_shape);
        const savedBoxs = obj_arm_sensor_item_inspector.getBoxs(); // Hàm getter trả về mảng this.boxs
        console.log("savedBoxs",savedBoxs);
        if (Array.isArray(savedBoxs) && savedBoxs.length > 0) {
            console.log(`Tiến hành vẽ lại ${savedBoxs.length} đối tượng con đã lưu...`);
            savedBoxs.forEach((detectData) => {
                detectData.canvasWidth = WIDTH_IMG_SHAPE;
                obj_arm_sensor_item_inspector.drawDetectedObject(canvasManager, detectData);
            });
        } else {
            console.log("Danh sách đối tượng nhận diện trống (chưa thực hiện phán định hoặc đối tượng mới tạo).");
        }
        console.log("Hoàn thành việc chuyển đổi và khôi phục trạng thái hiển thị ARM Sensor.");
}

function createMeasureShapeTable(data_shape = null) {
    const wrapper = document.createElement("div");
    wrapper.id = "measure-shape-wrapper";
    const table = document.createElement("table");
    table.className = "measure-weld-width-config-table";
    table.id = "measure-shape-table";
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
        input.id = `measure-shape-input-${index}`;
        input.type = "text";
        input.placeholder = "Nhập tên hình";
        if (data_shape) {
            input.value =
                data_shape.name ??
                data_shape.name ??
                "ARM Sensor";
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
            document.getElementById("measure-shape-input-0")?.value || "";
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
            boxContentArmSensor.innerHTML = "";
            console.log("obj_arm_sensor_item_inspector",obj_arm_sensor_item_inspector);
            obj_arm_sensor_item_inspector.setRectangle(objRectangle);
            write_log_clear("✅ Dữ liệu hợp lệ.");
            obj_region_arm_sensor_canvas.is_available_one_line = false;
            obj_region_arm_sensor_canvas.reset();
            canvasManager.clearShapeCanvas();
            obj_arm_sensor_item_inspector.drawAllRectangles(canvasManager,color_rect_shape);
            
            // let polygon = obj_arm_sensor_item_inspector.getPolygons()
            // if (polygon){
            //         obj_arm_sensor_item_inspector.setPolygons(polygon);
            //         imageWidth = 323;
            //         obj_arm_sensor_item_inspector.drawPolygons(canvasManager,polygon,imageWidth,WIDTH_IMG_SHAPE);
            // }

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
    btnClear.id = "btn-clear-shape";
    btnClear.textContent = "Xóa";
    btnClear.addEventListener("click", () => {
        const inp = document.getElementById("measure-shape-input-0");
        if (inp) inp.value = "";
    });
    actions.appendChild(btnAccept);
    actions.appendChild(btnClear);
    wrapper.appendChild(table);
    wrapper.appendChild(actions);
    return wrapper;
}

function write_log_clear(text){
    log_arm_sensor.textContent = text;
}

function write_log_append(text){
    log_arm_sensor.style.whiteSpace = "pre-line"; 
    log_arm_sensor.textContent += text + "\n";
}
