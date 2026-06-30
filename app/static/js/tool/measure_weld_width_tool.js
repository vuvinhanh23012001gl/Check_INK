console.log("Vào file measure_weld_width");
import {panner_measure_weld_width,obj_measure_weld_width_canvas,additional_events,
    get_obj_product
} from "./common_value_tool.js"   




import {MeasureWeldWidthCanvas} from "../canvas/measure_weld_width_canvas.js"
import {Line} from "../model/model_line.js"
import {scroll_container,canvasManager,WIDTH_IMG_SHAPE}from "../common_value.js"
import {Measurement} from "../model/model_measurement.js"
import {ItemsInspector} from "../services/items_inspector.js"
import {MeasurementItemsInspector} from "../services/measurement_items_inspector.js"
import {postData} from "../utills/api.js";
 
let DEFAULT_VALUE_OF_LINE_SEGMENT_DISTANCE  = 20;   //Biến khoảng cách các đường line khi nhấn auto
let DEFAULT_VALUE_OF_ADDITIONAL_LENGTH =  20;       //Biến mặc định chiều dai đường line sẽ là 20px
let imageWidth = 0;//Cai nay se thay doi khi nhan vao che do tu dong quy uoc    
let obj_measurement_items_inspector = null;           // đối tượng Item vẽ hiện tại
let selected = {      
    product_id :-1,
    frame_id:-1,
    items_id:-1,
}
let line = new Line();   // đối tượng line vẽ hiện tại.

const btnExitMeasureWeldWidth = document.getElementById("btnExitMeasureWeldWidth");
const btnAutoRule = document.getElementById("btnAutoRule");
const btnClearFrameMeasureWeldWidth =  document.getElementById("btnClearFrameMeasureWeldWidth");
const boxContentMeasureWeldWidth = document.getElementById("table-cof-tool-content-measure-weld-width")
const txtBoxLog = document.getElementById("log-measure-weld-width");
const loading = document.getElementById("loading");
const loadingStatus = document.getElementById("loading-status");
const loadingBar = document.getElementById("loading-bar");
const loadingPercent = document.getElementById("loading-percent");
const bntJudment = document.getElementById("judment-img-item");


additional_events.set("weld_width_tool", event_transition_items);
obj_measure_weld_width_canvas.on(MeasureWeldWidthCanvas.NAME_EVENT_WHEN_CLICK_RIGHT_LINE,func_callback_click_mouse_right);
obj_measure_weld_width_canvas.on(MeasureWeldWidthCanvas.NAME_EVENT_WHEN_CLICK_ON_LINE,func_callback_click_on_line_drawn);
obj_measure_weld_width_canvas.on(MeasureWeldWidthCanvas.NAME_EVENT_WHEN_CLICK_ON_LINE_HAVE_AREALY,func_callback_click_on_line_have_aready);

/**
 * Chuyển sang item được chọn và cập nhật hiển thị trên canvas.
 *
 * Chức năng:
 * - Cập nhật thông tin item đang được chọn.
 * - Lấy hoặc khởi tạo MeasurementItemsInspector của item.
 * - Vẽ lại các đường measurement.
 * - Nếu có polygon thì vẽ polygon lên canvas.Nếu không có thì không cần vẽ
 * - biến data được event truyền vào
 * @param {Object} data - Thông tin item được chọn.
 * @param {string|number} data.product_id - ID của sản phẩm.
 * @param {string|number} data.frame_id - ID của frame.
 * @param {string|number} data.items_id - ID của item. 
 *
 * @returns {void}
 */


function event_transition_items(data){
    console.log("Event_measure_callback",data);
    canvasManager.clearShapeCanvas();
    console.log("data?.frame_id,",data?.frame_id,"data?.items_id",data?.items_id);
    selected.product_id = data?.product_id;
    selected.frame_id = data?.frame_id;
    selected.items_id = data?.items_id;
    obj_measurement_items_inspector = get_obj_product().find_item_object_corresponding(String(data?.frame_id),String(data?.items_id),ItemsInspector.TYPE_MEASUREMENT);
    if (!obj_measurement_items_inspector){
        let obj_items_inspector = get_obj_product().get_item_object(String(data?.frame_id),String(data?.items_id));
        obj_measurement_items_inspector =  new MeasurementItemsInspector();
        obj_items_inspector.setMeasurementItems(obj_measurement_items_inspector);
    }
    obj_measurement_items_inspector.draw_multiple_lines(canvasManager);
    let polygons = obj_measurement_items_inspector.getPolygons();
    if (polygons && imageWidth!= 0){obj_measurement_items_inspector.drawPolygons(canvasManager,polygons,imageWidth,WIDTH_IMG_SHAPE);}                   
}

/**
 * Đóng panel đo Weld Width.
 */
btnExitMeasureWeldWidth.addEventListener("click",()=>{
    panner_measure_weld_width.classList.remove("active");
});  


/**
 * Gửi yêu cầu judgment cho item đang chọn.
 * Chức năng:
 * - Vẽ polygon lên canvas nếu dữ liệu hợp lệ.và lưu vào đối tượng vẽ hiện tại measure item inspector hiện tại.
 */

bntJudment.addEventListener("click",async ()=>{
    let status_selected =  checkSelected(selected);
    if (status_selected){
        write_log_clear("");
        let result_judment = await postData("/law_regulation/judment_item",selected);
        console.log("result_judment",result_judment);
        let status_judment =  result_judment?.ok;
        let message_judment =  result_judment?.message;
        if (!status_judment){
            write_log_clear(message_judment);return;
        }
        let width_judment =  result_judment?.data?.width;
        let polygon_judment =  result_judment?.data?.polygon;
        if (width_judment!= undefined &&  polygon_judment!=undefined){
            obj_measurement_items_inspector.setPolygons(polygon_judment);
            imageWidth = width_judment;// 2 biến chỗ này bằng giá trị của nhau 
            console.log("imageWidth",imageWidth);
            obj_measurement_items_inspector.drawPolygons(canvasManager,polygon_judment,width_judment,WIDTH_IMG_SHAPE);
        }
    }
})




/**
 * Hàm chuyển đổi dữ liệu cấu trúc API thành mảng các đối tượng Measurement
 * @param {Object} apiResponse - Đối tượng JSON tổng trả về từ API
 * @returns {Measurement[]} Mảng các đối tượng thuộc lớp Measurement
 */
function parseApiToMeasurements(
    apiResponse,
    usedIds = [],
    width = 2048
) {
    if (!apiResponse || !apiResponse.ok || !apiResponse.data) {
        console.error("Dữ liệu API không hợp lệ.");
        return [];
    }

    const {
        level = [],
        lines = [],
        width: srcWidth = 2048
    } = apiResponse.data;

    const [l1 = 0, l2 = 0, l3 = 0, l4 = 0, l5 = 0] = level;

    // Chỉ scale theo chiều rộng
    const scale = width / srcWidth;

    const maxId = usedIds.length > 0
        ? Math.max(...usedIds.map(Number))
        : -1;

    let nextId = maxId + 1;

    return lines.map((line) => {

        const lineId = nextId++;

        const nameLine =
            line.nameLine ??
            line.name_line ??
            line.name ??
            `Line ${lineId}`;

        return new Measurement(
            lineId,
            nameLine,
            l1,
            l2,
            l3,
            l4,
            l5,
            Math.round((line.p1?.[0] ?? 0) * scale),
            Math.round((line.p1?.[1] ?? 0) * scale),
            Math.round((line.p2?.[0] ?? 0) * scale),
            Math.round((line.p2?.[1] ?? 0) * scale)
        );
    });
}

/**
 * Xử lý khi người dùng click vào một đường measurement đã tồn tại.
 *
 * Chức năng:
 * - Xác định đường được click theo tọa độ chuột.
 * - Nếu tìm thấy line này đã tồn tại thì return.
 * - Gọi hàm để hiển thị khung nhập giá trị line.
 * coordinate_now là giá trị được truyền từ event
 * @param {Object} coordinate_now - Tọa độ chuột trên canvas.
 * @param {number} coordinate_now.x - Tọa độ X.
 * @param {number} coordinate_now.y - Tọa độ Y.
 *
 * @returns {void}
 */

function func_callback_click_on_line_have_aready(coordinate_now){
  let coordinate_now_x = coordinate_now?.x;
  let coordinate_now_y = coordinate_now?.y;
  let result_find_line  = obj_measurement_items_inspector.findClickedLine(coordinate_now_x,coordinate_now_y);
  if (!result_find_line){return;}
  obj_measure_weld_width_canvas.have_return =  true; 
  func_callback_click_on_line_drawn(result_find_line);
}

/**
 * Xử lý sự kiện click chuột phải trên canvas.
 *
 * Chức năng:
 * - Xác định line được click hoặc line hiện tại.
 * - Xóa line measurement tương ứng.
 * - Vẽ lại danh sách measurement. danh sách điểm
 * - Vẽ lại polygon (nếu có).đối tượng đó đã có
 *
 * @param {Object} data - Thông tin sự kiện chuột.
 * @param {number} data.x - Tọa độ X.
 * @param {number} data.y - Tọa độ Y.
 * @param {boolean} data.status_check_point_in_line_current - Trạng thái con trỏ đang nằm trên line hiện tại.
 *
 * @returns {void}
 */

function func_callback_click_mouse_right(data){
    let result_find_line  = obj_measurement_items_inspector.findClickedLine(data.x,data.y);
    if (result_find_line||data.status_check_point_in_line_current){
            obj_measure_weld_width_canvas.is_available_one_line = false;  // moi them
            boxContentMeasureWeldWidth.innerHTML = ""; // reset html con
            obj_measurement_items_inspector.deleteLineByCoordinateAdvance(result_find_line?.xStart, result_find_line?.yStart, result_find_line?.xEnd, result_find_line?.yEnd);
            canvasManager.clearShapeCanvas();
            obj_measurement_items_inspector.draw_multiple_lines(canvasManager);
            console.log("Danh sách sau khi xóa:",obj_measurement_items_inspector.toDict());  
             
            let polygons = obj_measurement_items_inspector.getPolygons();
           if (polygons && imageWidth!= 0){obj_measurement_items_inspector.drawPolygons(canvasManager,polygons,imageWidth,WIDTH_IMG_SHAPE);}

    }
}


btnAutoRule.addEventListener("click", async () => {
     boxContentMeasureWeldWidth.innerHTML = "";
     boxContentMeasureWeldWidth.appendChild(createMeasureWeldWidthTableNoName()); //result_create_line_id_new.data la id khi tao moi
});


btnClearFrameMeasureWeldWidth.addEventListener("click",()=>{
    obj_measurement_items_inspector =  new MeasurementItemsInspector();
    let obj_items_inspector = get_obj_product().get_item_object(String(selected?.frame_id),String(selected?.items_id));
    obj_items_inspector.setMeasurementItems(obj_measurement_items_inspector);
    canvasManager.clearShapeCanvas();
    obj_measurement_items_inspector.draw_multiple_lines(canvasManager);
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




function createMeasureWeldWidthTableNoName() {
    const wrapper = document.createElement("div");
    const table = document.createElement("table");
    table.className = "measure-weld-width-config-table";
    const rows = [
        "Độ kéo dài line",
        "Độ dãn nở",
        "Level 1",
        "Level 2",
        "Level 3",
        "Level 4",
        "Level 5",
    ];
    const inputRefs = [];
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
        input.value = 0;
        if (index == 1){ input.value = DEFAULT_VALUE_OF_LINE_SEGMENT_DISTANCE;}//Giá trị mặc định của độ dãn nở line
        if (index == 0){ input.value = DEFAULT_VALUE_OF_ADDITIONAL_LENGTH;}//Giá trị mặc định của độ dãn nở line
        inputRefs.push(input);
        td.appendChild(input);
        tr.appendChild(th);
        tr.appendChild(td);
        table.appendChild(tr);
    });
    const actions = document.createElement("div");
    actions.className = "config-actions";
    const btnAccept = document.createElement("button");
    btnAccept.className = "btn btn-accept";
    btnAccept.textContent = "Chấp nhận";
    btnAccept.addEventListener("click", async () => {
            console.log("Bạn vừa nhấn tự động vẽ line phán định");
            write_log_clear();
            const elements_input  = inputRefs.map(inp => Number(inp.value || 0));
            console.log("Input hiện tại",elements_input[0],elements_input[1],elements_input[2],elements_input[3], elements_input[4],elements_input[5],elements_input[6]);
            console.log("Selected",selected);
            let result_validate = validateWeldLevelsIncreasingNoName(elements_input);
            console.log("Kết quả kiểm tra tự động quy ước", result_validate);
            if (result_validate.isValid) {
                const intKeys = ["product", "frame", "items"];
                const levelKeys = [
                    "lengthen_line",
                    "distance_line",
                    "Level1_auto",
                    "Level2_auto",
                    "Level3_auto",
                    "Level4_auto",
                    "Level5_auto"
                ];
                let data_send = {
                    [intKeys[0]]: selected.product_id,
                    [intKeys[1]]: selected.frame_id,
                    [intKeys[2]]: selected.items_id,
                    [levelKeys[0]]: elements_input[0],
                    [levelKeys[1]]: elements_input[1],
                    [levelKeys[2]]: elements_input[2],
                    [levelKeys[3]]: elements_input[3],
                    [levelKeys[4]]: elements_input[4],
                    [levelKeys[5]]: elements_input[5],
                    [levelKeys[6]]: elements_input[6],
                };                
                if (!checkSelected(selected)){return;}
                loadingShow("Tiến trình tự tạo quy ước");
                loadingSetProgress(10,"Đang thực hiện ...");
                let p = 0;
                const timer = setInterval(()=>{if(p < 98){p += 5;loadingSetProgress(p);}},50);
                let result_send_cmd_auto_regulation = await postData("/law_regulation/auto_create_line",data_send);
                console.log("result_send_cmd_auto_regulation",result_send_cmd_auto_regulation);
                let polygon = result_send_cmd_auto_regulation?.data?.polygon;
                console.log("polygon",polygon);

                clearInterval(timer);
                loadingSetProgress(100,"Hoàn thành");
                loadingHide();
                let arr_id_line = obj_measurement_items_inspector.getAllLineIds();
                console.log("Danh sách ID đang tồn tại:",arr_id_line);
                let arr_data = parseApiToMeasurements(result_send_cmd_auto_regulation,arr_id_line,WIDTH_IMG_SHAPE);
                console.log("Arr Obj measurement đang tồn tại.",arr_data);
                let result_extend = obj_measurement_items_inspector.extendMeasurements(arr_data);
                console.log("Kết quả extend",result_extend);
                let status_extend =  result_extend?.status;
                let message_extend =  result_extend?.message;
                console.log("Trạng thái extend",status_extend,"message:",message_extend);
                canvasManager.clearShapeCanvas();
                obj_measurement_items_inspector.draw_multiple_lines(canvasManager);
                if (polygon){
                    imageWidth =  result_send_cmd_auto_regulation?.data?.width;
                    obj_measurement_items_inspector.setPolygons(polygon);
                    obj_measurement_items_inspector.drawPolygons(canvasManager,polygon,imageWidth,WIDTH_IMG_SHAPE);}
            } else {
                let alertMessage = "❌ THÔNG BÁO LỖI DỮ LIỆU NHẬP VÀO:\n\n";
                write_log_clear(alertMessage);
                result_validate.errors.forEach(err => {
                    write_log_append(`📍 Dòng lỗi: [${err.level}]`);
                    write_log_append(` - Giá trị hiện tại: ${err.currentVal}`);
                    write_log_append(` - Yêu cầu: ${err.message}`);
                });
            }
    });
    const btnClear = document.createElement("button");
    btnClear.className = "btn btn-clear";
    btnClear.textContent = "Xóa";
    btnClear.addEventListener("click", () => {
        inputRefs.forEach(inp => inp.value = 0);

    });
    actions.appendChild(btnAccept);
    actions.appendChild(btnClear);
    wrapper.appendChild(table);
    wrapper.appendChild(actions);
    return wrapper;
}



function checkSelected(selected) {
    const checks = [
        {
            value: selected.product_id,
            message: "❌Bạn chưa chọn sản phẩm\n"
        },
        {
            value: selected.frame_id,
            message: "❌Bạn chưa chọn Frame tương ứng\n"
        },
        {
            value: selected.items_id,
            message: "❌Bạn chưa chọn điểm tương ứng\n"
        }
    ];
    for (const check of checks) {
        if (check.value === -1) {
            write_log_clear(check.message);
            return false;
        }
    }
    return true;
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
          //Lấy danh sách ID hiện tại đang lưu;
        if (result_validate_probationarier.isValid){
            obj_measurement_items_inspector.addMeasurementAdvance(obj_probationary);
            console.log("[MeasurementItemsInspector Measurement] Kết quả sau khi thêm Line mới:",obj_measurement_items_inspector.toDict());
            write_log_clear("✅Dữ liệu hợp lệ.");
            wrapper.innerHTML = "";
            obj_measure_weld_width_canvas.is_available_one_line  = false;
            obj_measure_weld_width_canvas.reset();
            canvasManager.clearShapeCanvas();
            obj_measurement_items_inspector.draw_multiple_lines(canvasManager);
            let polygons = obj_measurement_items_inspector.getPolygons();
            if (polygons && imageWidth!= 0){obj_measurement_items_inspector.drawPolygons(canvasManager,polygons,imageWidth,WIDTH_IMG_SHAPE);}
        }
        else{
            let alertMessage = "❌ THÔNG BÁO LỖI DỮ LIỆU NHẬP VÀO:\n\n";
            write_log_clear(alertMessage);
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

function validateAutoCreateLine(data,intKeys,levelKeys) {
    
    for (const key of intKeys) {
        if (!(key in data)) {
            return { ok: false, message: `${key} is required` };
        }
        const value = Number(data[key]);
        if (!Number.isInteger(value)) {
            return { ok: false, message: `${key} must be an integer` };
        }
        data[key] = value; // Ép kiểu luôn
    }
   
    const levels = [];
    for (const key of levelKeys) {
        if (!(key in data)) {
            return { ok: false, message: `${key} is required` };
        }
        const value = Number(data[key]);
        if (Number.isNaN(value)) {
            return { ok: false, message: `${key} must be a number` };
        }
        levels.push(value);
        data[key] = value; // Ép kiểu
    }
    for (let i = 0; i < levels.length - 1; i++) {
        if (levels[i] >= levels[i + 1]) {
            return {
                ok: false,
                message: "Level1_auto < Level2_auto < Level3_auto < Level4_auto < Level5_auto"
            };
        }
    }
    return {
        ok: true,
        data
    };
}

function loadingShow(message = "Đang xử lý...") {
    loading.style.display = "flex";
    loadingStatus.textContent = message;
    loadingBar.style.width = "0%";
    loadingPercent.textContent = "0%";
}

function loadingHide() {
    loading.style.display = "none";
}
function loadingSetStatus(message) {
    loadingStatus.textContent = message;
}
function loadingSetProgress(percent, message = null) {
    percent = Math.max(0, Math.min(100, percent));
    loadingBar.style.width = `${percent}%`;
    loadingPercent.textContent = `${Math.round(percent)}%`;

    if (message !== null) {
        loadingStatus.textContent = message;
    }
}


function validateWeldLevelsIncreasingNoName(data) {
    if (!Array.isArray(data) || data.length !== 7) {
        return {
            isValid: false,
            errors: [{
                field: "data",
                currentVal: data,
                message: "Phải có đúng 7 phần tử"
            }]
        };
    }
    const errors = [];
    // lengthen, distance_line
    ["lengthen", "distance_line"].forEach((field, i) => {
        const v = data[i];
        const n = Number(v);
        const invalid =
            v === "" || v == null ? "Không được để trống" :
            Number.isNaN(n) ? "Phải là số" :
            !Number.isInteger(n) ? "Phải là số nguyên" :
            n < 0 ? "Phải >= 0" :
            "";
        if (invalid)
            errors.push({ field, currentVal: v, message: invalid });
    });
    // Level1 -> Level5
    const levels = data.slice(2, 7).map((v, i) => {
        const n = Number(v);
        const invalid =
            v === "" || v == null ? "Không được để trống" :
            Number.isNaN(n) ? "Phải là số" :
            n <= 0 ? "Phải > 0" :
            "";
        if (invalid) {
            errors.push({
                field: `Level${i + 1}_auto`,
                currentVal: v,
                message: invalid
            });
            return null;
        }
        return n;
    });
    for (let i = 0; i < 4; i++) {
        if (levels[i] != null &&
            levels[i + 1] != null &&
            levels[i] >= levels[i + 1]) {
            errors.push({
                field: `Level${i + 1}_auto -> Level${i + 2}_auto`,
                currentVal: `${levels[i]} >= ${levels[i + 1]}`,
                message: "Level sau phải lớn hơn level trước"
            });
        }
    }
    return { isValid: errors.length === 0, errors };
}