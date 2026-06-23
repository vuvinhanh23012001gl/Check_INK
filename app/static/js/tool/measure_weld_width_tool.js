console.log("Vào file measure_weld_width");
import {panner_measure_weld_width,obj_measure_weld_width_canvas,additional_events,
    get_obj_product
} from "./common_value_tool.js"   
import {MeasureWeldWidthCanvas} from "../canvas/measure_weld_width_canvas.js"
import {Line} from "../model/model_line.js"
import {scroll_container,canvasManager}from "../common_value.js"
import {Measurement} from "../model/model_measurement.js"
import {ItemsInspector} from "../services/items_inspector.js"
import {MeasurementItemsInspector} from "../services/measurement_items_inspector.js"

let obj_measurement_items_inspector = null;
let selected = {    
    product_id :-1,
    frame_id:-1,
    items_id:-1,
}
let line = new Line();

const btnExitMeasureWeldWidth = document.getElementById("btnExitMeasureWeldWidth");
const btnSaveFrameMeasureWeldWidth = document.getElementById("btnSaveFrameMeasureWeldWidth");
const btnClearFrameMeasureWeldWidth =  document.getElementById("btnClearFrameMeasureWeldWidth");
const boxContentMeasureWeldWidth = document.getElementById("table-cof-tool-content-measure-weld-width")
const txtBoxLog = document.getElementById("log-measure-weld-width");


additional_events.set("weld_width_tool", event_transition_items);
obj_measure_weld_width_canvas.on(MeasureWeldWidthCanvas.NAME_EVENT_WHEN_CLICK_RIGHT_LINE,func_callback_click_mouse_right);
obj_measure_weld_width_canvas.on(MeasureWeldWidthCanvas.NAME_EVENT_WHEN_CLICK_ON_LINE,func_callback_click_on_line_drawn);
obj_measure_weld_width_canvas.on(MeasureWeldWidthCanvas.NAME_EVENT_WHEN_CLICK_ON_LINE_HAVE_AREALY,func_callback_click_on_line_have_aready);


function event_transition_items(data){
    console.log("Event_measure_callback",data);
    canvasManager.clearShapeCanvas();
    console.log("data?.frame_id,",data?.frame_id,"data?.items_id",data?.items_id);
    obj_measurement_items_inspector = get_obj_product().find_item_object_corresponding(String(data?.frame_id),String(data?.items_id),ItemsInspector.TYPE_MEASUREMENT);
    if (!obj_measurement_items_inspector){
        let obj_items_inspector = get_obj_product().get_item_object(String(data?.frame_id),String(data?.items_id));
        obj_measurement_items_inspector =  new MeasurementItemsInspector();
        obj_items_inspector.setMeasurementItems(obj_measurement_items_inspector);
    }
    obj_measurement_items_inspector.draw_multiple_lines(canvasManager);
}


btnExitMeasureWeldWidth.addEventListener("click",()=>{
    panner_measure_weld_width.classList.remove("active");
});  



function func_callback_click_on_line_have_aready(coordinate_now){
  let coordinate_now_x = coordinate_now?.x;
  let coordinate_now_y = coordinate_now?.y;
  let result_find_line  = obj_measurement_items_inspector.findClickedLine(coordinate_now_x,coordinate_now_y);
  if (!result_find_line){return;}
  obj_measure_weld_width_canvas.have_return =  true; 
  func_callback_click_on_line_drawn(result_find_line);
}



function func_callback_click_mouse_right(data){
    let result_find_line  = obj_measurement_items_inspector.findClickedLine(data.x,data.y);
    if (result_find_line||data.status_check_point_in_line_current){
            boxContentMeasureWeldWidth.innerHTML = ""; // reset html con
            obj_measurement_items_inspector.deleteLineByCoordinateAdvance(result_find_line?.xStart, result_find_line?.yStart, result_find_line?.xEnd, result_find_line?.yEnd);
            canvasManager.clearShapeCanvas();
            obj_measurement_items_inspector.draw_multiple_lines(canvasManager);
            console.log("Danh sách sau khi xóa:",obj_measurement_items_inspector.toDict());  
    }
}


btnSaveFrameMeasureWeldWidth.addEventListener("click",()=>{
    console.log("Bạn vừa nhấn vào Save Frame measure Wel Width")
});   


btnClearFrameMeasureWeldWidth.addEventListener("click",()=>{
    console.log("Bạn vừa nhấn vào Clearn Frame measure wel width");
});


function func_callback_click_on_line_drawn(line_current){
    boxContentMeasureWeldWidth.innerHTML = ""; // reset html con
    // console.log("dict sau khi chuyen thanh de ve",obj_measurement_items_inspector.getAllDictLine());
    console.log("line_current",line_current);
    line.xEnd =  Number(line_current?.xEnd);
    line.yEnd =  Number(line_current?.yEnd);
    line.xStart =  Number(line_current?.xStart);
    line.yStart =  Number(line_current?.yStart);   // setup cho line hiện tại
    let result_create_line_id_new = obj_measurement_items_inspector.findLineByCoordinate(line.xStart, line.yStart, line.xEnd,line.yEnd);
   // let result_create_line_id_new = obj_measurement_items_inspector.findLineByCoordinate(5001, 520, 30, 40); //ham test
    // console.log(result_create_line_id_new.status ? `Line đã tồn tại: ${JSON.stringify(result_create_line_id_new, null, 2)}` : `Line mới, ID mới là ${result_create_line_id_new.data}`);
    if (!result_create_line_id_new.status){
        boxContentMeasureWeldWidth.appendChild(createMeasureWeldWidthTable(result_create_line_id_new.data)); //result_create_line_id_new.data la id khi tao moi

    }
    else{
        //result_create_line_id_new.data? cai nay la doi tuong
        const measurementClone = { ...result_create_line_id_new.data };// TẠO BẢN SAO Ở ĐÂY
        boxContentMeasureWeldWidth.appendChild(createMeasureWeldWidthTable(measurementClone.lineId,measurementClone));//result_create_line_id_new.data la id khi da co
    }
        
}






function createMeasureWeldWidthTable(id_line,data_line) {
    const existed = document.getElementById(
        `measure-weld-width-wrapper-${id_line}`
    );
    const wrapper = document.createElement("div");
    wrapper.id = `measure-weld-width-wrapper-${id_line}`;

    const table = document.createElement("table");
    table.className = "measure-weld-width-config-table";
    table.id = `measure-weld-width-table-${id_line}`;

    const rows = [
        "Tên Line",
        "Level 1",
        "Level 2",
        "Level 3",
        "Level 4",
        "Level 5"
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
        input.type = "number";
        input.placeholder = "Nhập level quy định";
        if (labelText == rows[0]){
            input.type = "text";
            input.placeholder = "Nhập tên đoạn thẳng";
        }

        input.id = `measure-weld-width-input-${id_line}-${index}`;
        if (data_line) {
            if (index === 0) {
                input.value = data_line.nameLine ?? data_line.name_line ?? "";
            } else {
                input.value = data_line[`level${index}`] ?? 0;
            }
        } 
        //else if (index !== 0) {
        //     input.value = 0;
        // }

        td.appendChild(input);
        tr.appendChild(th);
        tr.appendChild(td);

        table.appendChild(tr);
    });

    // Checkbox
    const trCheckbox = document.createElement("tr");
    trCheckbox.className = "config-row";
    const thCheckbox = document.createElement("th");
    thCheckbox.className = "config-label";
    thCheckbox.textContent = "Kiểm tra bọt khí đường hàn";
    const tdCheckbox = document.createElement("td");
    tdCheckbox.className = "config-value";
    const label = document.createElement("label");
    label.classList.add("switch", "check-for-air-bubbles");
    label.id = `check-for-air-bubbles-${id_line}`;
    // Buttons
    const actions = document.createElement("div");
    actions.className = "config-actions";
    actions.id = `config-actions-${id_line}`;
    const btnAccept = document.createElement("button");
    btnAccept.className = "btn btn-accept";
    btnAccept.id = `btn-accept-${id_line}`;
    btnAccept.textContent = "Chấp nhận";
    btnAccept.addEventListener("click", () => {
        const nameLineVal = document.getElementById(`measure-weld-width-input-${id_line}-0`)?.value || "";
        const level1Val = Number(document.getElementById(`measure-weld-width-input-${id_line}-1`)?.value || 0);
        const level2Val = Number(document.getElementById(`measure-weld-width-input-${id_line}-2`)?.value || 0);
        const level3Val = Number(document.getElementById(`measure-weld-width-input-${id_line}-3`)?.value || 0);
        const level4Val = Number(document.getElementById(`measure-weld-width-input-${id_line}-4`)?.value || 0);
        const level5Val = Number(document.getElementById(`measure-weld-width-input-${id_line}-5`)?.value || 0);
        let obj_probationary = new Measurement(
                id_line,
                nameLineVal,
                level1Val,
                level2Val,
                level3Val,
                level4Val,
                level5Val,
                line?.xStart ?? 0, // Giữ lại tọa độ cũ từ data_line truyền vào bảng
                line?.yStart ?? 0,
                line?.xEnd ?? 0,
                line?.yEnd ?? 0
            );
        let result_validate_probationarier = obj_probationary.validateWeldLevelsIncreasing();
        console.log("result_validate_probationarier",result_validate_probationarier);
        if (result_validate_probationarier.isValid){
            obj_measurement_items_inspector.addMeasurementAdvance(obj_probationary);
            console.log("[MeasurementItemsInspector Measurement] Kết quả sau khi thêm Line mới:",obj_measurement_items_inspector.toDict());
            write_log_clear("✅Dữ liệu hợp lệ.");
            wrapper.innerHTML = "";
            obj_measure_weld_width_canvas.is_available_one_line  = false;
            obj_measure_weld_width_canvas.reset();
            canvasManager.clearShapeCanvas();
            obj_measurement_items_inspector.draw_multiple_lines(canvasManager);
        }
        else{
            let alertMessage = "❌ THÔNG BÁO LỖI DỮ LIỆU NHẬP VÀO:\n\n";
            result_validate_probationarier.errors.forEach(err => {
                write_log_append (`📍 Dòng lỗi: [${err.rowName}]`);
                write_log_append (` - Giá trị hiện tại: ${err.currentVal}`);
                write_log_append (` - Yêu cầu nên là: ${err.expected}`);  
            });
             
        }
    });
    const btnClear = document.createElement("button");
    btnClear.className = "btn btn-clear";
    btnClear.id = `btn-clear-${id_line}`;
    btnClear.textContent = "Xóa";
    
    btnClear.addEventListener("click", () => {
        rows.forEach((_, index) => {
            const inp = document.getElementById(`measure-weld-width-input-${id_line}-${index}`);
            if (inp) inp.value = index === 0 ? "" : 0;
        });
      
    });
    actions.appendChild(btnAccept);
    actions.appendChild(btnClear);
    wrapper.appendChild(table);
    wrapper.appendChild(actions);
    return wrapper;
}

function validateWeldLevelsIncreasing(id_line) {
    const errors = [];
    const levels = [];
    for (let i = 1; i < inputs.length; i++) {
        const raw = inputs[i].value.trim();
        const labelIndex = i; // Level 1 = inputs[1]
        if (raw === "") {
            errors.push(`Level ${labelIndex} không được để trống\n`);
            levels.push(null);
            continue;
        }
        const num = Number(raw);
        if (isNaN(num)) {
            errors.push(`Level ${labelIndex} phải là số\n`);
            levels.push(null);
            continue;
        }
        levels.push(num);
    }
    for (let i = 0; i < levels.length - 1; i++) {
        const current = levels[i];
        const next = levels[i + 1];

        // bỏ qua nếu có null
        if (current === null || next === null) continue;
        if (current >= next) {
            errors.push(
                `Level ${i + 1} phải nhỏ hơn Level ${i + 2}\n`
            );
        }
    }
    return {
        isValid: errors.length === 0,
        errors
    };
}

function write_log_clear(text){
    txtBoxLog.textContent = text;
}

function write_log_append(text){
    txtBoxLog.style.whiteSpace = "pre-line"; 
    txtBoxLog.textContent += text + "\n";
}