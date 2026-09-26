import {fetchGet,postData} from "./utills/api.js"
import {scroll_container,canvasManager,active_sceen_show_video,show_video_product,get_camera_connection,SocketData,SocketLog,HEIGH_IMG_SHAPE,WIDTH_IMG_SHAPE}from "./common_value.js";
import {DimesionalCalibrationCanvas} from "./canvas/dimesional_calibration_canvas.js"
import {}from "./utills/logic.js";
import {openOptionPanel} from "./panel_manager.js";



const btn_calcular_calibration  =  document.getElementById("calcular-calibration-button");
const header_dimetional_calibration = document.getElementById("header-ul-li-dimensional-calibration");
const obj_draw_calibration = new DimesionalCalibrationCanvas()
const paner_draw_calibration = document.getElementById("paner-calibration");
const open_video_calibration = document.getElementById("open-video-calibration");
const run_model_calibration = document.getElementById("run-model-calibration");
const log_calibration       = document.getElementById("log-calibration");
const cancel_calibration_button  = document.getElementById("cancel-calibration-button");
const table_calib_config_and_show         =  document.getElementById("table-calib-config-and-show");
const config_calibration    = document.getElementById("config-calibration"); 
const show_calibration      =  document.getElementById("configuration-data-calibration");

const CALCULATION_PARAMETER = "calculation_parameters";
const RESULT_PARAMETER      = "result_parameters";
const keys_line = ["xStart", "yStart", "xEnd", "yEnd"];
const keys_coordinate = ["coordinateX","coordinateY","coordinateZ"]
const KEY_ID_ITEM = "id_item";

let actual_wid_img = 0;
let actual_hei_img = 0;

let value_line_current_click = {};
value_line_current_click[keys_line[0]] = -1;
value_line_current_click[keys_line[1]]= -1;
value_line_current_click[keys_line[2]] = -1;
value_line_current_click[keys_line[3]] = -1;
let MAX_LIMIT_NUMBER_CAPTURE_CALIBRATION = 20;
let MIN_LIMIT_NUMBER_CAPTURE_CALIBRATION = 5;

let count_frame_id = 0;  //đểm số frame ID đang tồn tại


let coordinate_items_now ={
    x:-1,
    y:-1,
    z:-1,
}

const selected = {
    frame_id: -1,
    items_id: -1
};

window.addEventListener("iai-point-selected", event => {
    const coordinates = event.detail || {};
    const frameId = Number(coordinates.frameId);
    const itemId = Number(coordinates.pointId);
    if (Number.isInteger(frameId) && frameId >= 0) {
        selected.frame_id = frameId;
    }
    if (Number.isInteger(itemId) && itemId >= 0) {
        selected.items_id = itemId;
    }
    if (coordinates.valid) {
        coordinate_items_now = {
            x: coordinates.x,
            y: coordinates.y,
            z: coordinates.z,
        };
        console.log("Tọa độ point đã chọn từ summary:", coordinate_items_now);
        if (paner_draw_calibration.classList.contains("active")) {
            move_to_selected_point(
                coordinate_items_now.x,
                coordinate_items_now.y,
                coordinate_items_now.z
            );
        }
    } else {
        coordinate_items_now = {x: -1, y: -1, z: -1};
        console.warn("Point được chọn không có tọa độ hợp lệ.");
    }
});
let dict_lines_of_frames = {};  //data ALL
let active_calibration_data = null;
let id_product_selecting_now = null; //San pham dang chon
let current_frame_box = null ; // Frame hiện tại đang đc click
let calibration_load_id = 0;
let calibration_move_request = null;
let last_moved_position = null;
let calibration_model_running = false;
let calibration_result_data = null;
const calibration_loading = document.getElementById("loading");
const calibration_loading_status = document.getElementById("loading-status");
const calibration_loading_bar = document.getElementById("loading-bar");
const calibration_loading_percent = document.getElementById("loading-percent");



//đăng kí sự kiện khi click vào line
obj_draw_calibration.on(DimesionalCalibrationCanvas.NAME_EVENT_WHEN_CLICK_ON_LINE,func_callback_click_on_line_drawn);
obj_draw_calibration.on(DimesionalCalibrationCanvas.NAME_EVENT_WHEN_CLICK_RIGHT_MOUSE_BTN,func_callback_click_right_mouse_on_line);
obj_draw_calibration.on(DimesionalCalibrationCanvas.NAME_EVENT_CHECK_LINE_EXIS,func_callback_check_line_exis);

function func_callback_click_right_mouse_on_line() {
    console.log("Trước:", structuredClone(dict_lines_of_frames));
    scroll_container.querySelectorAll(".active_hightlight").forEach(el =>
        el.classList.remove("active_hightlight")
    );
    obj_draw_calibration.cout_click = 0;
    delete dict_lines_of_frames?.[id_product_selecting_now]?.[selected.frame_id];
    if (selected.frame_id >= 0 && id_product_selecting_now !== null) {
        postData("/dimesional_calibration/delete_calibration", {
            product_id: Number(id_product_selecting_now),
            frame_id: Number(selected.frame_id),
        });
    }
    config_calibration.innerHTML = "";
    canvasManager.clearShapeCanvas();
    canvasManager.clearPreviewCanvas();
    obj_draw_calibration.reset();
    scroll_container.querySelectorAll(".active_hightlight").forEach(element => {
        element.classList.remove("active_hightlight");
    });
    write_log_calibration_clear("✅ Đã xóa line và dữ liệu calibration tạm thời.");
    console.log("Sau:", structuredClone(dict_lines_of_frames));
}


SocketData.on("data_calibration", data =>{
    calibration_result_data = data.data;
    render_selected_calibration_result();
});

SocketLog.on("log_calibration",data=>{
    console.log("Log Calibration",data);
    const message = `${data?.msg || ""}`;
    const progressMatch = message.match(/^CALIB_PROGRESS:(\d+):(.*)$/);
    if (progressMatch) {
        calibration_loading_show();
        calibration_loading_set_progress(
            Number(progressMatch[1]),
            progressMatch[2]
        );
        if (Number(progressMatch[1]) === 0) {
            window.setTimeout(calibration_loading_hide, 500);
        }
        return;
    }
    write_log_calibration_append(message);
    if (message.startsWith("❌")) {
        calibration_loading_set_progress(0, message);
        window.setTimeout(calibration_loading_hide, 500);
        return;
    }
    if (/Tính toán dữ liệu Calibration thành công|Scale thất bại|Camera chỉ chụp được|Không tìm thấy điểm|Nhận không đúng dữ liệu ARM/.test(message)) {
        calibration_loading_set_progress(
            message.includes("thành công") ? 100 : 0,
            message
        );
        if (message.includes("thành công") || message.includes("thất bại") || message.includes("Không tìm thấy") || message.includes("không đúng")) {
            window.setTimeout(calibration_loading_hide, 500);
        }
    }
});

function calibration_loading_show(message = "Đang tính hệ số calibration...") {
    if (!calibration_loading) return;
    calibration_loading.style.display = "flex";
    calibration_loading_status.textContent = message;
    calibration_loading_bar.style.width = "0%";
    calibration_loading_percent.textContent = "0%";
}

function calibration_loading_set_progress(percent, message = null) {
    if (!calibration_loading) return;
    const safePercent = Math.max(0, Math.min(100, percent));
    calibration_loading_bar.style.width = `${safePercent}%`;
    calibration_loading_percent.textContent = `${Math.round(safePercent)}%`;
    if (message !== null) calibration_loading_status.textContent = message;
}

function calibration_loading_hide() {
    if (calibration_loading) calibration_loading.style.display = "none";
}

function render_selected_calibration_result() {
    if (!calibration_result_data || selected.frame_id < 0) {
        show_calibration.innerHTML = "";
        return;
    }
    const productData = calibration_result_data?.[id_product_selecting_now];
    const frameData = productData?.[String(selected.frame_id)];
    if (!frameData?.result_parameters) {
        show_calibration.innerHTML = "";
        write_log_calibration_append(`ℹ️ Frame ${selected.frame_id} chưa có hệ số calibration.`);
        return;
    }
    renderResultTableDiv({
        [selected.frame_id]: frameData,
    }, show_calibration);
}


function func_callback_click_on_line_drawn(line){   // Hàm này hoạt động khi click vào line
    // console.log("[CallBackOnLine]",line);
    value_line_current_click[keys_line[0]] = line?.xStart;
    value_line_current_click[keys_line[1]] = line?.yStart ;
    value_line_current_click[keys_line[2]] = line?.xEnd;
    value_line_current_click[keys_line[3]] = line?.yEnd;
    console.log(`[CallBackOnLine] Xstart,Ystart :(${value_line_current_click[keys_line[0]]},${value_line_current_click[keys_line[1]]}).xEnd,yEnd:(${value_line_current_click[keys_line[2]] },${value_line_current_click[keys_line[3]]})`);
    createCalibrationTable(
        config_calibration,
        selected.frame_id,
        id_product_selecting_now,
        selected.items_id,
        dict_lines_of_frames,
        active_calibration_data,
    );
}

function func_callback_check_line_exis(line){
      const line_exis =  get_data_create_calibrationTable_config(dict_lines_of_frames,id_product_selecting_now, selected.frame_id, CALCULATION_PARAMETER,selected.items_id);  // nếu không có dữ liệu line
      if (line_exis){
             obj_draw_calibration.has_line_of_frame = true;
             return;
      }
     obj_draw_calibration.has_line_of_frame = false;
}

async function move_to_selected_point(x, y, z) {
    if (![x, y, z].every(Number.isFinite) || [x, y, z].some(value => value < 0)) {
        write_log_calibration_clear("❌ Tọa độ item không hợp lệ, không thể di chuyển IAI.");
        return;
    }
    const requestKey = `${x},${y},${z}`;
    if (last_moved_position === requestKey) {
        write_log_calibration_append("ℹ️ IAI đã ở vị trí này, không gửi lại lệnh.");
        return;
    }
    if (calibration_move_request === requestKey) {
        write_log_calibration_append("ℹ️ IAI đang ở hoặc đang di chuyển đến vị trí này.");
        return;
    }
    if (calibration_move_request !== null) {
        write_log_calibration_append("⚠️ IAI đang di chuyển, vui lòng chờ hoàn tất.");
        return;
    }
    calibration_move_request = requestKey;
    write_log_calibration_clear(`⏳ IAI đang di chuyển đến X:${x}, Y:${y}, Z:${z}...`);
    try {
        const result = await postData(
            "/dimesional_calibration/run_point_define_value",
            {x, y, z}
        );
        write_log_calibration_clear(
            result?.message || "❌ Không nhận được phản hồi di chuyển IAI."
        );
        if (result?.ok) last_moved_position = requestKey;
    } catch (error) {
        write_log_calibration_clear(`❌ Không thể di chuyển IAI: ${error}`);
    } finally {
        calibration_move_request = null;
    }
}

function draw_model_polygons(polygons, sourceWidth, sourceHeight = null) {
    canvasManager.clearPreviewCanvas();
    if (!Array.isArray(polygons) || !polygons.length || !sourceWidth) return;
    const canvas = canvasManager.cPrev;
    const height = Number(sourceHeight) || sourceWidth * canvas.height / canvas.width;
    const scale = Math.min(canvas.width / sourceWidth, canvas.height / height);
    const offsetX = (canvas.width - sourceWidth * scale) / 2;
    const offsetY = (canvas.height - height * scale) / 2;
    const context = canvasManager.ctxPrev;
    context.save();
    context.strokeStyle = "#00e5ff";
    context.lineWidth = 3;
    context.fillStyle = "rgba(0, 229, 255, 0.12)";
    polygons.forEach(polygon => {
        if (!Array.isArray(polygon) || polygon.length < 2) return;
        context.beginPath();
        polygon.forEach((point, index) => {
            const x = offsetX + Number(point[0]) * scale;
            const y = offsetY + Number(point[1]) * scale;
            if (index === 0) context.moveTo(x, y);
            else context.lineTo(x, y);
        });
        context.closePath();
        context.fill();
        context.stroke();
    });
    context.restore();
}


function createCalibrationTable(
    container,
    frame_id,
    product_id,
    item_id,
    data = null,
    selectedCalibrationData = null,
) {
    container.innerHTML = "";
    const table = document.createElement("table");
    table.classList.add("calibration-table");
    const fields = [
        { title: "Tên line", key: "lineName", placeholder: "Nhập tên Line",type:"text"},
        { title: "Kích thước thực tế (mm)", key: "realityMM", placeholder: "Độ dài khoảng cách thật line", type:"number"},
        { title: "Số lần chụp", key: "captureCount", placeholder: "Số lần chụp 100> x >5",type:"number"}
    ];
    //  console.log("-------------------------------");
    //  console.log("dict_lines_of_frames",dict_lines_of_frames);

    const calibrationData_box = selectedCalibrationData
        || get_data_create_calibrationTable_config(
            data,
            product_id,
            frame_id,
            CALCULATION_PARAMETER,
            item_id,
        );
    fields.forEach(field => {
        const tr = document.createElement("tr");
        const th = document.createElement("th");
        th.textContent = field.title;

        const td = document.createElement("td");
        const input = document.createElement("input");
        input.type = field.type;
        input.dataset.key = field.key;
        if (calibrationData_box){
            selection_data_input(input,calibrationData_box?.[field.key],  field.placeholder);}
        else {
            selection_data_input(input,null,field.placeholder);
        }

        td.appendChild(input);
        tr.appendChild(th);
        tr.appendChild(td);
        table.appendChild(tr);
    });
    container.appendChild(table);
    const div_btn = document.createElement("div");
    const btn_erase  = createButton(`btn-clear-${product_id}-${frame_id}`,"Xóa dữ liệu","btn-clear",fields);
    const btn_accept  = createButton(`btn-accept-${product_id}-${frame_id}`,"Chấp nhận","btn-accept",fields);
    div_btn.className = "btn-accept-clean-line-calibration";
    div_btn.appendChild(btn_erase);
    div_btn.appendChild(btn_accept);
    container.appendChild(div_btn);
    btn_erase.addEventListener("click", () => {
    const inputs = table.querySelectorAll("input");
        inputs.forEach(input => {
                    input.value = "";
                });
    });

    btn_accept.addEventListener("click", () => {
        const inputs = table.querySelectorAll("input");
        const data = {};
        let name_line =  null;
        inputs.forEach(input => {
            data[input.dataset.key] = input.value;
            if (input.dataset.key == "lineName"){name_line = input.value};
        });
        // console.log("data",data);
        // console.log("fields",fields);
        let result_validate = validateCalibrationData(data,fields);
        let status = result_validate?.valid;
        // console.log("result_validate",result_validate);
        if(status){
            let result_check_line = validateLineData(value_line_current_click);
            console.log("Dict Frame chưa thêm Line and Coordinate:",dict_lines_of_frames);
            if (result_check_line?.valid){
                let msg = "✅Kiểm tra dữ liệu hợp lệ";
                console.log(msg);
                write_log_calibration_clear(msg);
                high_light_item(selected.frame_id,selected.items_id);  // Cai nay khi nao chay gui ve ok hang xanhc
                data[keys_line[0]]  = value_line_current_click[keys_line[0]] ;
                data[keys_line[1]]  = value_line_current_click[keys_line[1]] ;
                data[keys_line[2]]  = value_line_current_click[keys_line[2]] ;
                data[keys_line[3]]  = value_line_current_click[keys_line[3]] ;
                data[keys_coordinate[0]] = coordinate_items_now.x;
                data[keys_coordinate[1]] = coordinate_items_now.y;
                data[keys_coordinate[2]] = coordinate_items_now.z;
                data[KEY_ID_ITEM] = selected.items_id;
                dict_lines_of_frames[id_product_selecting_now] ??= {};
                dict_lines_of_frames[id_product_selecting_now][selected.frame_id] ??= {};
                dict_lines_of_frames[id_product_selecting_now][selected.frame_id][CALCULATION_PARAMETER]=  data;
                console.log("Dict Frame đã thêm Line and Coordinate:",dict_lines_of_frames);
                obj_draw_calibration.redraw_the_line_with_the_text(canvasManager,name_line,"#FFFACD");
                container.innerHTML = "";
            }
            else{
                console.log("Dữ liệu line không hợp lệ");
                writeValidationErrors(result_check_line?.errors);
            }
        }
        else{
            writeValidationErrors(result_validate?.errors);
        }
    
    });

}

btn_calcular_calibration.addEventListener("click",()=>{
    let msg = "Bạn vừa nhấn vào tính hệ số chính xác Calibration";
    console.log(msg);
    let result_check = validateData(dict_lines_of_frames);
    console.log("Check dữ liệu",result_check);
    if (result_check.valid){
        write_log_calibration_clear("Đang gửi dữ liệu đến Server.");
        calibration_loading_show("Đang chờ tính hệ số calibration...");
        console.log("Data Send",dict_lines_of_frames);
        postData("/dimesional_calibration/calculater_calibration",{"data":dict_lines_of_frames})
            .then(result => {
                if (!result?.ok) {
                    calibration_loading_set_progress(0, result?.message || "❌ Không thể bắt đầu calibration.");
                    window.setTimeout(calibration_loading_hide, 500);
                }
            })
            .catch(error => {
                calibration_loading_set_progress(0, `❌ Lỗi gửi calibration: ${error}`);
                window.setTimeout(calibration_loading_hide, 500);
            });
        return;
    }
    write_log_calibration_clear(`❌${result_check.error}`);

    
});

function get_data_create_calibrationTable_config(data, product_id, frame_id, key,item_id) {   // Nếu Product id,frame id,items_id trung thi return gia tri. neu khac 1 trong 3 thi khong return
    const params = data?.[product_id]?.[frame_id]?.[key];
    if (!params) return null;
    const storedItemId = params[KEY_ID_ITEM];
    const hasNoValidItemId = storedItemId === undefined
        || storedItemId === null
        || storedItemId === ""
        || Number(storedItemId) < 0;
    return String(storedItemId) === String(item_id) || hasNoValidItemId
        ? params
        : null;
}


function high_light_item(frame_id_active, items_id_active) {
    scroll_container.querySelectorAll(".box-frame").forEach(frame => {
        const frame_id = frame.dataset.frameId;
        if (frame_id == frame_id_active){
            frame.querySelectorAll(".img-item").forEach(item => {
                const item_id = item.dataset.id;
                item.classList.remove("active_hightlight");
                const text = item.querySelector(".img-text");
                text.classList.remove("active_hightlight");
                if (item_id == items_id_active) {
                    item.classList.add("active_hightlight");
                    text.classList.add("active_hightlight");
                }
            });
        };
    });
}
// function high_light_item(frame_id_active, items_id_active) {
//     // 1. Tìm đúng frame đang hoạt động
//     const activeFrame = scroll_container.querySelector(`.box-frame[data-frame-id="${frame_id_active}"]`);
//     if (!activeFrame) return;
//     // 2. Xóa highlight của tất cả item đang có trong frame đó
//     activeFrame.querySelectorAll(".active_hightlight").forEach(el => {
//         el.classList.remove("active_hightlight");
//     });
//     // 3. Tìm item cần highlight và thêm class
//     const targetItem = activeFrame.querySelector(`.img-item[data-id="${items_id_active}"]`);
//     if (targetItem) {
//         targetItem.classList.add("active_hightlight");
//         const text = targetItem.querySelector(".img-text");
//         if (text) text.classList.add("active_hightlight");
//     }
// }


function createButton(id, text ,class_name,fields) {
    const btn = document.createElement("button");
    btn.id = id;
    btn.className =  class_name;
    btn.textContent = text;
    return btn;
}

function selection_data_input(element, data, placeholder = "default") {

    if (data !== null && data !== undefined && data !== "") {
        element.value = data;
        element.removeAttribute("placeholder");
    } else {
        element.value = "";
        element.placeholder = placeholder;
    }
}

header_dimetional_calibration.addEventListener("click",async ()=>{
    const loadId = ++calibration_load_id;
    openOptionPanel(paner_draw_calibration);
    scroll_container.innerHTML = "";
    canvasManager.setTool(obj_draw_calibration); 
    console.log("Bạn vừa click vào hiệu chuẩn kích thước");
    let head_data = await  fetchGet("/dimesional_calibration");
    if (loadId !== calibration_load_id) {
        return;
    }
    console.log("Bạn nhấn vào hiệu chỉnh kích thước.");
    console.log("Data header dimesion calibration",head_data);
    let data_point =  head_data?.data?.data_point;
    let id_product_choose_now = head_data?.data?.product?._id;
    id_product_selecting_now =  id_product_choose_now;
    show_calibration.innerHTML = "";
    console.log("ID sản phẩm đang chọn là :",id_product_choose_now);
    let data_dimesion = head_data?.data?.data_dimesion;
    actual_wid_img = head_data?.data?.wid_img;
    actual_hei_img = head_data?.data?.hei_img;
        calibration_result_data = data_dimesion; // Keep the initial calibration response available for frame-specific result rendering
        create_calibration_table_show(data_dimesion, actual_wid_img, actual_hei_img);
    scroll_container.innerHTML = "";
    create_img_items_dimesion_calibration(data_point);
    create_hight_light_items_for_frame(dict_lines_of_frames);


});


function create_calibration_table_show(data,actual_wid_img,actual_hei_img){
    console.log("Data để tạo bảng hiển thị thông số calibration",data);
    if (!data){
        console.log("Dữ liệu calibration chưa được cấu hình");
        return;
    }
    set_calculation(data,actual_wid_img,actual_hei_img,WIDTH_IMG_SHAPE,HEIGH_IMG_SHAPE);
    let data_show_table = extractResultParameters(data);
    renderResultTableDiv(data_show_table,show_calibration);
    // console.log("data_show_table",data_show_table);
}


function extractResultParameters(originalData) {
    let extractedData = {};
    if (!originalData) return extractedData;
    let targetData = originalData;
    let firstKey = Object.keys(originalData)[0];
    if (firstKey && originalData[firstKey] && typeof originalData[firstKey] === 'object' && !originalData[firstKey].result_parameters) {
        // Nếu có id_product_selecting_now thì lấy thẳng, không thì lấy key đầu tiên tìm thấy
        let activeKey = typeof id_product_selecting_now !== 'undefined' ? id_product_selecting_now : firstKey;
        targetData = originalData[activeKey] || originalData[firstKey];
    }
    // console.log("Dữ liệu mục tiêu sau khi bóc tách lớp bọc:", targetData);
    for (let lineId in targetData) {
        if (Object.prototype.hasOwnProperty.call(targetData, lineId)) {
            let item = targetData[lineId];
            if (item && item.result_parameters) {
                extractedData[lineId] = {
                    "result_parameters": item.result_parameters
                };
            }
        }
    }
    return extractedData;
}

function renderResultTableDiv(dataInput, containerElement) {
    containerElement.innerHTML = "";
    // console.log("dataInput nhận vào:", dataInput);
    if (!dataInput || !containerElement) return;

    // 1. Tạo thẻ bọc chính (.div-table)
    const tableContainer = document.createElement('div');
    tableContainer.classList.add('div-table');

    // 2. Tạo thanh tiêu đề (.div-table-header)
    const tableHeader = document.createElement('div');
    tableHeader.classList.add('div-table-header');

    // Danh sách các cột tiêu đề (Đã thêm lại PX trung bình)
    const headers = [
        "Frame",
        "Pixel trung bình (px)",
        "Độ lệch chuẩn",
        "Tỷ số (mm/pixel)",
        "Độ tin cậy",
        "Số lần chụp"
    ];

    headers.forEach(headerText => {
        const col = document.createElement('div');
        col.classList.add('div-table-col');
        col.textContent = headerText;
        tableHeader.appendChild(col);
    });
    tableContainer.appendChild(tableHeader);

    // 3. Tạo phần thân chứa dữ liệu (.div-table-body)
    const tableBody = document.createElement('div');
    tableBody.classList.add('div-table-body');

    // Duyệt qua dữ liệu đầu vào
    for (const lineId in dataInput) {
        if (Object.prototype.hasOwnProperty.call(dataInput, lineId)) {
            const item = dataInput[lineId];
            const res = item.result_parameters;

            if (res) {
                // Tạo một hàng dữ liệu (.div-table-row)
                const row = document.createElement('div');
                row.classList.add('div-table-row');

                // Cột 1: Frame ID
                const colId = document.createElement('div');
                colId.classList.add('div-table-col', 'line-id');
                colId.textContent = `${lineId}`;
                row.appendChild(colId);

                // Cột 2: PX trung bình (Khôi phục lại ở đây)
                const colMean = document.createElement('div');
                colMean.classList.add('div-table-col');
                colMean.textContent = `${res.pixel_mean.toFixed(2)}`;
                row.appendChild(colMean);

                // Cột 3: Pixel Std (Độ lệch chuẩn)
                const colStd = document.createElement('div');
                colStd.classList.add('div-table-col');
                colStd.textContent = res.pixel_std.toFixed(2);
                row.appendChild(colStd);

                // Cột 4: Scale (mm/pixel)
                const colScale = document.createElement('div');
                colScale.classList.add('div-table-col');
                colScale.textContent = res.scale_mm_per_pixel.toFixed(6);
                row.appendChild(colScale);

                // Cột 5: Confidence
                const colConf = document.createElement('div');
                colConf.classList.add('div-table-col');
                const badge = document.createElement('span');
                badge.classList.add('badge-confidence');
                badge.textContent = `${(res.confidence * 100).toFixed(0)}%`;
                colConf.appendChild(badge);
                row.appendChild(colConf);

                // Cột 6: Samples Used
                const colSamples = document.createElement('div');
                colSamples.classList.add('div-table-col');
                colSamples.textContent = `${res.samples_used} / ${res.samples_raw}`;
                row.appendChild(colSamples);

                // Đưa hàng vừa tạo vào phần thân bảng
                tableBody.appendChild(row);
            }
        }
    }
    tableContainer.appendChild(tableBody);

    // 4. Xác định vùng target để append bảng vào DOM
    let target = null;
    if (typeof containerElement === 'string') {
        target = document.getElementById(containerElement);
    } else if (containerElement && containerElement.innerHTML !== undefined) {
        target = containerElement;
    }
    if (target) {
        target.innerHTML = ''; 
        target.appendChild(tableContainer);
    }
}
function set_calculation(data, actual_wid_img, actual_hei_img, width_after_adjustment, height_after_adjustment) {
    let frame_calibration = data?.[id_product_selecting_now];
    // console.log("frame_calibration", frame_calibration);
    if (frame_calibration) {
        let result = {};
        let imgScaleX = actual_wid_img ? (width_after_adjustment / actual_wid_img) : 1;
        let imgScaleY = actual_hei_img ? (height_after_adjustment / actual_hei_img) : 1;
        console.log("imgScaleX",imgScaleX);
        console.log("imgScaleY",imgScaleY);
        for (let frameId in data) {
            if (Object.prototype.hasOwnProperty.call(data, frameId)) {
                result[frameId] = {};
                for (let lineId in data[frameId]) {
                    if (Object.prototype.hasOwnProperty.call(data[frameId], lineId)) {
                        let item = data[frameId][lineId];
                        let oldCalc = item.calculation_parameters;
                        let oldResult = item.result_parameters;
                        result[frameId][lineId] = {
                            "calculation_parameters": {
                                "lineName": String(oldCalc.name_item || ""),
                                "realityMM": String(oldCalc.reality_mm || ""),
                                "captureCount": String(oldCalc.number_capture || ""),
                                "xStart": oldCalc.startX * imgScaleX,
                                "yStart": oldCalc.startY * imgScaleY,
                                "xEnd": oldCalc.endX * imgScaleX,
                                "yEnd": oldCalc.endY * imgScaleY,
                                "coordinateX": 0,
                                "coordinateY": 0,
                                "coordinateZ": 0,
                                "id_item": Number(oldCalc.id_tems || 0)
                            }
                        };
                    }
                }
            }
        }
        dict_lines_of_frames = result;
        // console.log("Cập nhật dict_lines_of_frames thành công:", dict_lines_of_frames);
    } else {
        console.log("Có dữ liệu product id nhưng k có dữ liệu frame vô lý");
    }
}


function create_hight_light_items_for_frame(data){
    const frames = data?.[String(id_product_selecting_now)];
    if (!frames) return;
    for (const [frameId, frameData] of Object.entries(frames)) {
        const calibration = frameData?.[CALCULATION_PARAMETER];
        if (!calibration) continue;
        const frame = [...scroll_container.querySelectorAll(".box-frame")]
            .find(item => item.dataset.frameId === String(frameId));
        const items = [...(frame?.querySelectorAll(".img-item") || [])];
        if (!items.length) continue;
        if (!items.some(item => item.dataset.id === String(calibration.id_item))) {
            calibration.id_item = Number(items[0].dataset.id);
        }
        high_light_item(frameId, calibration.id_item);
        obj_draw_calibration.cout_click = 0;
        obj_draw_calibration.has_line_of_frame = true;
    }
} 

open_video_calibration.addEventListener("click",()=>{
    console.log("Bạn vừa nhấn vào Stream video calibration");
    if(!get_camera_connection()){ write_log_calibration_clear("❌ Camera hiện tại chưa kết nối.\n✅ Hãy kiểm tra kết nối.\n"); return;}
    active_sceen_show_video();
    show_video_product();
});

run_model_calibration.addEventListener("click", async () => {
    if (calibration_model_running) return;
    const target = get_selected_calibration_target();
    if (!target) {
        write_log_calibration_clear("❌ Hãy chọn ảnh item trước khi chạy model.");
        return;
    }
    calibration_model_running = true;
    write_log_calibration_clear("⏳ Đang chạy model tìm đường hàn...");
    try {
        const result = await postData("/law_regulation/measurement/run_model", target);
        if (!result?.ok) {
            write_log_calibration_clear(result?.message || "❌ Chạy model thất bại.");
            return;
        }
        draw_model_polygons(result?.data?.polygon, result?.data?.width, result?.data?.height);
        write_log_calibration_clear(
            result?.data?.polygon?.length
                ? "✅ Model đã phát hiện đường hàn. Hãy vẽ line chính xác trên đường hàn."
                : "⚠️ Model không phát hiện polygon đường hàn."
        );
    } catch (error) {
        write_log_calibration_clear(`❌ Chạy model thất bại: ${error}`);
    } finally {
        calibration_model_running = false;
    }
});













function create_img_items_dimesion_calibration(points_and_box){
        // console.log("Data create_img_items",data?.data);
        // console.log("data đúng của product");
        // console.log("points_and_box",points_and_box);
        let index_frame = 0;
        let build_tree = {};
        for (const boxs in points_and_box){
            // console.log("boxs",boxs);
            // console.log("Số Frame ID hiện tại bằng",count_frame_id);
            let index_items = 0;
            let result_create_box = create_box(boxs,index_frame);
            let div_img_box = result_create_box.div_img_box;
            let div_box_frame = result_create_box.div_box_frame;
            //Kiểm tra xem cái nào đang chọn thì chọn nó.
            if (boxs == selected.frame_id){
                // console.log("Vẫn còn nha");
                div_box_frame.classList.add("box-frame-selected");
            }
            // console.log("frame_current",frame_current);
            
            index_frame++;
            for (const items in points_and_box[boxs]){
                // console.log("data nhan dc la",points_and_box[boxs][items]);
                // console.log("dsaddsdsadsds123",items,points_and_box[boxs][items]);
                let data_point =  points_and_box[boxs][items];
                create_items_img(items,index_items,data_point,div_img_box,boxs);
                index_items++;
            }
        }
}



function create_items_img(id, index ,data_point=null, frame_box =null, frame_id =  null){
    const img_text = document.createElement("div");
    img_text.className = "img-text";
    img_text.textContent = `Ảnh ${index}`;
    const img_img = document.createElement("img");
    img_img.className = "img_show_point";
    const img_item = document.createElement("div");
    if (data_point==null) {img_img.src = "../static/img/plus.png";img_item.dataset.has_icon_add_new = true;} else {img_img.src = `${data_point.path_img_point}?v=${Math.random()}`;}
    img_item.className = "img-item";
    img_item.dataset.id = id;
    img_item.appendChild(img_img);
    img_item.appendChild(img_text);
    if (frame_box){
            frame_box.appendChild(img_item);
            img_item.addEventListener("click",()=>{
                    config_calibration.innerHTML = "";
                    obj_draw_calibration.reset();
                    canvasManager.clearShapeCanvas();
                    // Cập nhật các biến    global
                    scroll_container.querySelectorAll(".box-frame").forEach(frame => {
                            frame.querySelectorAll(".img-item").forEach(items => {
                        items.classList.remove("active");
                    });
                    });  //CALCULATION_PARAMETER   RESULT_PARAMETER
                    let calibration_frame =  dict_lines_of_frames?.[id_product_selecting_now]?.[frame_id]?.[CALCULATION_PARAMETER];
                    active_calibration_data = null;
                    // console.log("Dữ liệu 323232323232",dict_lines_of_frames);
                    // console.log("ahihih",calibration_frame);
                    canvasManager.show_img_items(img_img);
                    if (calibration_frame){
                        // console.log("ID Item đang click",img_item.dataset.id);
                        // console.log("ID Item đã có line",calibration_frame?.[KEY_ID_ITEM]);
                        if (img_item.dataset.id == calibration_frame?.[KEY_ID_ITEM]){
                            console.log("Hiển thị Line đã vẽ");
                            create_line(calibration_frame,img_item.dataset.id);}
                        }

                    const coordinates = loadPointCoordinates(data_point);
                    coordinate_items_now = coordinates;
                    console.log("Tọa độ point đã chọn:", coordinate_items_now);
                    
                    img_item.classList.add("active");
                    current_frame_box = frame_box; //đối tượng dom
                    selected.items_id = Number(img_item.dataset.id);  
                    selected.frame_id = Number(frame_id);
                    const storedItemId = Number(calibration_frame?.[KEY_ID_ITEM]);
                    if (calibration_frame && (
                        !Number.isFinite(storedItemId)
                        || storedItemId < 0
                        || storedItemId === selected.items_id
                    )) {
                        calibration_frame[KEY_ID_ITEM] = selected.items_id;
                        active_calibration_data = calibration_frame;
                    }
                    render_selected_calibration_result();
                    console.log(`Point đang click frame: ${selected.frame_id} id: ${selected.items_id}`);
                    move_to_selected_point(
                        coordinate_items_now.x,
                        coordinate_items_now.y,
                        coordinate_items_now.z
                    );
                    // write_log_capture_clear("✍️ Nhập vị trí cần chụp ảnh.")
                    // console.log("ID thật:", img_item.dataset.id);
                    // console.log("Tên hiển thị:", img_text.textContent);


                    return;
        });
    }
    else{
        console.log("Lỗi hoặc không có sản phẩm");
    }
}



function create_line(data, items_id_select_now){
    if (!data) return;
    let name_line =   data?.lineName;  // nếu không tồn tại thì không được vẽ
    obj_draw_calibration.defined_line_segment.xStart = data?.xStart;
    obj_draw_calibration.defined_line_segment.yStart = data?.yStart;
    obj_draw_calibration.defined_line_segment.xEnd = data?.xEnd;
    obj_draw_calibration.defined_line_segment.yEnd = data?.yEnd;
    obj_draw_calibration.draw_defined_line_segment(canvasManager,name_line);
}


function create_box(box_id,index){
    console.log(`Tạo box ID= ${box_id},Index:${index}`);
    const div_box_frame = document.createElement("div");
    div_box_frame.className = "box-frame";
    div_box_frame.dataset.frameId = box_id; // gán id cho frame
    const div_text_box_frame =  document.createElement("div");
    div_text_box_frame.textContent = `Ảnh sản phẩm thứ ${index}`;
    div_text_box_frame.className = "text_inf_frame";
    const div_img_box =  document.createElement("div");
    div_img_box.className = "img-box";
    div_box_frame.addEventListener("click", () => {
        scroll_container.querySelectorAll(".box-frame").forEach(frame => {frame.classList.remove("box-frame-selected");});
        const id = div_box_frame.dataset.frameId;
        div_box_frame.classList.add("box-frame-selected");
        console.log("Click vào frame thứ:", id);
        selected.frame_id = id;
        selected.items_id = -1;
        render_selected_calibration_result();
        current_frame_box = div_img_box; // lưu frame hiện tại
    })
    ;
    div_box_frame.appendChild(div_text_box_frame);
    div_box_frame.appendChild(div_img_box);
    scroll_container.appendChild(div_box_frame);
    return {div_img_box,div_box_frame}
}


function write_log_calibration_clear(text){
    log_calibration.textContent = text;
}

function write_log_calibration_append(text){
    log_calibration.textContent += text+"\n";
}


function loadPointCoordinates(dataPoint) {
    if (!dataPoint || [dataPoint.x, dataPoint.y, dataPoint.z].some(value => value === null || value === undefined || value === "")) {
        return {x: -1, y: -1, z: -1};
    }
    const coordinates = {
        x: Number(dataPoint?.x),
        y: Number(dataPoint?.y),
        z: Number(dataPoint?.z),
    };
    return coordinates;
}


cancel_calibration_button.addEventListener("click",()=>{
    console.log("Tến hành thoát dimesionnal calibration");
    calibration_load_id += 1;
    scroll_container.innerHTML = "";
      fetch('/dimesional_calibration/exit')
      .then(response => {
          console.log("responsd")
          if (response.redirected) {
              window.location.href = response.url;
          } else {
              response.json().then(data => {
                  window.location.href = data.redirect_url;
              });
          }
      });
});


function validateLineData(line) {
    const errors = [];
    for (const value of Object.values(line)) {
        if (typeof value !== "number") {
            errors.push("❌ Giá trị phải là kiểu number");
            continue;
        }
        if (!Number.isInteger(value)) {
            errors.push("❌ Giá trị phải là số nguyên");
            continue;
        }
        if (value !== -1 && value < 0) {
            errors.push("❌ Giá trị phải bằng -1 hoặc >= 0");
        }
    }
    return {
        valid: errors.length === 0,
        errors
    };
}


function validateCalibrationData(data, fields) {
    const errors = [];
    for (const field of fields) {
        const value = data[field.key];
        if (
            value === undefined ||
            value === null ||
            value.toString().trim() === ""
        ) {
            errors.push(`❌ ${field.title} không được để trống`);
            continue;
        }
        switch (field.key) {
            case "realityMM": {
                const realityMM = parseFloat(value);
                if (isNaN(realityMM) || realityMM <= 0) {
                    errors.push(
                        `❌ ${field.title} phải là số thực lớn hơn 0`
                    );
                }
                break;
            }
            case "captureCount": {
                const captureCount = Number(value);
                if (
                    !Number.isInteger(captureCount) ||
                    captureCount < MIN_LIMIT_NUMBER_CAPTURE_CALIBRATION ||
                    captureCount > MAX_LIMIT_NUMBER_CAPTURE_CALIBRATION
                ) {
                    errors.push(
                        `❌ ${field.title} phải là số nguyên từ ${MIN_LIMIT_NUMBER_CAPTURE_CALIBRATION} đến ${MAX_LIMIT_NUMBER_CAPTURE_CALIBRATION}`
                    );
                }
                break;
            }
        }
    }
    return {
        valid: errors.length === 0,
        errors
    };
}



function writeValidationErrors(errors) {
     write_log_calibration_clear("");
    for (const error of errors) {
        write_log_calibration_append(error);
    }
}
function validateData(data) {
    const requiredFields = {
        lineName: "string",
        realityMM: "string",
        captureCount: "string",
        xStart: "number",
        yStart: "number",
        xEnd: "number",
        yEnd: "number",
        coordinateX: "number",
        coordinateY: "number",
        coordinateZ: "number",
        id_item: "number"
    };

    // ❗ CHECK DATA RỖNG
    if (!data || Object.keys(data).length === 0) {
        return {
            valid: false,
            error: "Data rỗng. Hãy Chỉnh sửa Data"
        };
    }

    for (const frameId in data) {
        const frame = data[frameId];

        if (!frame || Object.keys(frame).length === 0) {
            return {
                valid: false,
                error: `Frame ${frameId} rỗng`
            };
        }

        for (const lineId in frame) {
            const params = frame[lineId]?.calculation_parameters;

            if (!params) {
                return {
                    valid: false,
                    error: `Thiếu calculation_parameters tại frame=${frameId}, line=${lineId}`
                };
            }

            for (const [field, type] of Object.entries(requiredFields)) {
                if (!(field in params)) {
                    return {
                        valid: false,
                        error: `Thiếu field '${field}' tại frame=${frameId}, line=${lineId}`
                    };
                }

                if (typeof params[field] !== type) {
                    return {
                        valid: false,
                        error: `Sai kiểu '${field}' tại frame=${frameId}, line=${lineId}. Mong ${type}, nhận ${typeof params[field]}`
                    };
                }
            }
        }
    }

    return {
        valid: true,
        error: null
    };
}

function get_selected_calibration_target() {
    let frameId = Number(selected.frame_id);
    let itemId = Number(selected.items_id);
    const activeItem = scroll_container.querySelector(".img-item.active");
    if (activeItem) {
        const activeFrame = activeItem.closest(".box-frame");
        if (activeFrame) frameId = Number(activeFrame.dataset.frameId);
        itemId = Number(activeItem.dataset.id);
    }
    if (!Number.isInteger(frameId) || frameId < 0 ||
        !Number.isInteger(itemId) || itemId < 0 ||
        id_product_selecting_now === null || id_product_selecting_now === undefined) {
        return null;
    }
    selected.frame_id = frameId;
    selected.items_id = itemId;
    return {
        product_id: Number(id_product_selecting_now),
        frame_id: frameId,
        items_id: itemId,
    };
}