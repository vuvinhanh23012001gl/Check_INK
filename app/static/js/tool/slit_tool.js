import {scroll_container,canvasManager,WIDTH_IMG_SHAPE}from "../common_value.js"
import {additional_events,obj_measure_slit_width_canvas,boxContentMeasureSlitWidth,get_obj_product,selected,
    checkSelected,create_obj_cross_item,write_log_clear,write_log_append,setNameEventActivate,refesh_btn,panner_measure_slit_width
} from "./common_value_tool.js"   
import {LineDrawer} from "../canvas/line_drawer_canvas.js"
import {ModelSlit} from "../model/model_slit.js"
import {ItemsInspector} from "../services/items_inspector.js"
import {SlitItemInspector} from "../services/slit_item_inspector.js"
import {Line} from "../model/model_line.js"
import {postData} from "../utills/api.js";




additional_events.set("slit_width_tool", event_transition_items);
const log_slit_measure = document.getElementById("log-slit-measure");
const btn_judment_slit = document.getElementById("btn-judment-slit");
const btn_clear_slit   = document.getElementById("btn-clear-slit");
const btn_exit_slit   = document.getElementById("btn-exit-slit");
let imageWidth = 0;//Cai nay se thay doi khi nhan vao che do tu dong quy uoc    
let line = new Line();   // đối tượng line vẽ hiện tại.



obj_measure_slit_width_canvas.on(LineDrawer.NAME_EVENT_WHEN_CLICK_RIGHT_LINE,func_callback_click_mouse_right_into_line);
obj_measure_slit_width_canvas.on(LineDrawer.NAME_EVENT_WHEN_CLICK_ON_LINE,func_callback_click_mouse_left_into_line);
obj_measure_slit_width_canvas.on(LineDrawer.NAME_EVENT_WHEN_CLICK_ON_LINE_HAVE_AREALY,func_callback_click_on_line_have_aready);


//Hàm này sẽ được gọi khi vừa nhấn nút mở tool hoac chuyen event deu chay ham nay
export function event_transition_items(){
    boxContentMeasureSlitWidth.innerHTML = ""; 
    write_log_clear(log_slit_measure,"");
    get_obj_product().highlightItems( scroll_container,ItemsInspector.TYPE_SLIT,"slits"); //cái này cần đọc log để biết "slits" là gì. 
    if (selected.frame_id  == -1 ||selected.items_id  == -1 || selected.product_id ==  -1){console.log("Lỗi chưa chọn sản phâm");return;};
    let obj_slit_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_SLIT,SlitItemInspector,"setSlitItems");
    if(!obj_slit_item_inspector){return;}
    obj_measure_slit_width_canvas.reset();
    obj_slit_item_inspector.drawAllSlits(canvasManager);
    let polygons = obj_slit_item_inspector.getPolygons();
    if (polygons && imageWidth!= 0){obj_slit_item_inspector.drawPolygons(canvasManager,polygons,imageWidth,WIDTH_IMG_SHAPE);}        
    console.log("đã tạo đối tượng ");
}

// Hàm này sẽ được gọi khi vừa nhấn nút mở tool

btn_clear_slit.addEventListener("click",()=>{
    console.log("Bạn vừa nhấn vào tẩy Frame");
    let obj_slit_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_SLIT,SlitItemInspector,"setSlitItems");
    obj_slit_item_inspector.clearAll();
    canvasManager.clearShapeCanvas();
    boxContentMeasureSlitWidth.innerHTML = ""; // reset html con
    obj_slit_item_inspector.drawAllSlits(canvasManager);
    let polygons = obj_slit_item_inspector.getPolygons();
    get_obj_product().highlightItems( scroll_container,ItemsInspector.TYPE_SLIT,"slits"); 
    if (polygons && imageWidth!= 0){obj_slit_item_inspector.drawPolygons(canvasManager,polygons,imageWidth,WIDTH_IMG_SHAPE);}
});


function func_callback_click_on_line_have_aready(coordinate_now){
    let obj_slit_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_SLIT,SlitItemInspector,"setSlitItems");
     boxContentMeasureSlitWidth.innerHTML = ""; 
     let coordinate_now_x = coordinate_now?.x;
     let coordinate_now_y = coordinate_now?.y;

     console.log("coordinate_now",coordinate_now);
     let result_find_line  = obj_slit_item_inspector.findClickedLine(coordinate_now_x,coordinate_now_y);
     if (!result_find_line){return;}
     obj_measure_slit_width_canvas.have_return =  true; 
      func_callback_click_on_line_drawn(result_find_line);
}

function func_callback_click_on_line_drawn(line_current){
    let obj_slit_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_SLIT,SlitItemInspector,"setSlitItems");
    boxContentMeasureSlitWidth.innerHTML = ""; 
    if (!line_current) return;
    line.xEnd =   Number(line_current?.xEnd);
    line.yEnd =   Number(line_current?.yEnd);
    line.xStart = Number(line_current?.xStart);
    line.yStart = Number(line_current?.yStart);   
    let target_id = line_current?.id_line;
    if (target_id !== undefined && target_id !== null && target_id !== "undefined") {
        console.log("Line đã tồn tại với ID:", target_id);
        const measurementClone = { ...line_current, id_line: String(target_id) };
        boxContentMeasureSlitWidth.appendChild(createMeasureSlitWidthTable(measurementClone.id_line, measurementClone));
        return;
    }

    let result_create_line_id_new = obj_slit_item_inspector.findLineByCoordinate(
        line.xStart, 
        line.yStart, 
        line.xEnd,
        line.yEnd
    );
    console.log("Kết quả tìm kiếm line:", result_create_line_id_new);
    if (!result_create_line_id_new || !result_create_line_id_new.status){
        let id_new = result_create_line_id_new?.data ?? obj_slit_item_inspector.generateNextId();
        if (id_new === "undefined" || id_new === undefined) id_new = "0";
        console.log("Line chưa tồn tại trong inspector. Tạo mới với ID:", id_new);
        boxContentMeasureSlitWidth.appendChild(createMeasureSlitWidthTable(String(id_new), line));
    }
    else {
        console.log("Line đã tồn tại trong inspector. Đang nạp dữ liệu cũ...");
        const measurementClone = { ...result_create_line_id_new.data };
        let valid_id = measurementClone.id_line ?? "0";
        if (valid_id === "undefined") valid_id = "0";
        measurementClone.id_line = String(valid_id);
        boxContentMeasureSlitWidth.appendChild(createMeasureSlitWidthTable(measurementClone.id_line, measurementClone));
    }
}


function func_callback_click_mouse_right_into_line(coordinate){
        let obj_slit_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_SLIT,SlitItemInspector,"setSlitItems");
        boxContentMeasureSlitWidth.innerHTML = ""; 
        let result_find_line  = obj_slit_item_inspector.findClickedLine(coordinate.x,coordinate.y);
        if (result_find_line){
                obj_measure_slit_width_canvas.is_available_one_line = false;  // moi them
                obj_slit_item_inspector.removeSlit(result_find_line?.id_line);
                canvasManager.clearShapeCanvas();
                get_obj_product().highlightItems( scroll_container,ItemsInspector.TYPE_SLIT,"slits"); 
                obj_slit_item_inspector.drawAllSlits(canvasManager);
                let polygons = obj_slit_item_inspector.getPolygons();
                if (polygons && imageWidth!= 0){obj_slit_item_inspector.drawPolygons(canvasManager,polygons,imageWidth,WIDTH_IMG_SHAPE);}
        }
}

function func_callback_click_mouse_left_into_line(data){
    let obj_slit_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_SLIT,SlitItemInspector,"setSlitItems");
    console.log("đã click chuột trái vào line",data);
    line.xEnd =  Number(data?.xEnd);
    line.yEnd =  Number(data?.yEnd);
    line.xStart =  Number(data?.xStart);
    line.yStart =  Number(data?.yStart);   // setup cho line hiện tại
    let id_new  = obj_slit_item_inspector.generateNextId();
    boxContentMeasureSlitWidth.appendChild(createMeasureSlitWidthTable(id_new,line)); 
}


function createMeasureSlitWidthTable(id_line,data_line) {
    if (id_line === undefined || id_line === "undefined" || id_line === null) {
        id_line = data_line?.id_line ?? "0";
        if (id_line === "undefined") id_line = "0";
    }
    id_line = String(id_line);
    let obj_slit_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_SLIT,SlitItemInspector,"setSlitItems");
    const existed = document.getElementById(
        `measure-slit-width-wrapper-${id_line}`
    );
    const wrapper = document.createElement("div");
    wrapper.id = `measure-slit-width-wrapper-${id_line}`;
    
    const table = document.createElement("table");
    // Giữ nguyên class CSS cũ theo yêu cầu của bạn
    table.className = "measure-weld-width-config-table"; 
    table.id = `measure-slit-width-table-${id_line}`;
    
    const rows = [
        "Tên đường",
        "Độ rộng Min",
        "Độ rộng Max"
    ];
    
    rows.forEach((labelText, index) => {
        const tr = document.createElement("tr");
        tr.className = "config-row"; // Giữ nguyên class CSS cũ
        const th = document.createElement("th");
        th.className = "config-label"; // Giữ nguyên class CSS cũ
        th.textContent = labelText;
        const td = document.createElement("td");
        td.className = "config-value"; // Giữ nguyên class CSS cũ
        const input = document.createElement("input");
        input.className = "config-input"; // Giữ nguyên class CSS cũ
        input.id = `measure-slit-width-input-${id_line}-${index}`;
        // Cấu hình riêng cho hàng đầu tiên (Tên đường) và các hàng số (Min/Max)
        if (index === 0) {
            input.type = "text";
            input.placeholder = "Nhập tên đoạn thẳng";
            if (data_line) {
                input.value = data_line.nameLine ?? data_line.name_line ?? "";
            }
        } else {
            input.type = "number";
            input.placeholder = "Nhập độ rộng quy định";
            if (data_line) {
                const propName = index === 1 ? "widthMin" : "widthMax";
                const altPropName = index === 1 ? "min_width" : "max_width";
                input.value = data_line[propName] ?? data_line[altPropName] ?? 0;
            }
        }
        td.appendChild(input);
        tr.appendChild(th);
        tr.appendChild(td);
        table.appendChild(tr);
    });
    // --- Buttons Actions ---
    const actions = document.createElement("div");
    actions.className = "config-actions"; // Giữ nguyên class CSS cũ
    actions.id = `config-actions-${id_line}`;
    const btnAccept = document.createElement("button");
    btnAccept.className = "btn btn-accept"; // Giữ nguyên class CSS cũ
    btnAccept.id = `btn-accept-${id_line}`;
    btnAccept.textContent = "Chấp nhận";
    btnAccept.addEventListener("click", () => {
        const nameLineVal = document.getElementById(`measure-slit-width-input-${id_line}-0`)?.value || "";
        const widthMinVal = Number(document.getElementById(`measure-slit-width-input-${id_line}-1`)?.value || 0);
        const widthMaxVal = Number(document.getElementById(`measure-slit-width-input-${id_line}-2`)?.value || 0);
        let valid_id = id_line;
        if (valid_id === undefined || valid_id === "undefined" || valid_id === null) {
            valid_id = data_line?.id_line ?? "0";
            if (valid_id === "undefined") valid_id = "0";
        }
        valid_id = String(valid_id);
        let obj_probationary = new ModelSlit(
            valid_id,
            nameLineVal,
            widthMinVal,
            widthMaxVal,
            data_line?.xStart ?? line?.xStart ?? 0, 
            data_line?.yStart ?? line?.yStart ?? 0,
            data_line?.xEnd ?? line?.xEnd ?? 0,
            data_line?.yEnd ?? line?.yEnd ?? 0
        );
        console.log("obj_probationary",obj_probationary);
        let result_validate_probationarier = obj_probationary.validateSlitLevelsIncreasing(); 
        console.log("result_validate_probationarier", result_validate_probationarier);
        if (result_validate_probationarier.isValid) {
            console.log("obj_slit_item_inspector",obj_slit_item_inspector);
            console.log("obj_probationary",obj_probationary);
            obj_slit_item_inspector.addSlit(obj_probationary);
            console.log("Kết quả sau khi thêm Line mới:", obj_slit_item_inspector.toDict());
            write_log_clear(log_slit_measure,"✅ Dữ liệu hợp lệ.");
            get_obj_product().highlightItems( scroll_container,ItemsInspector.TYPE_SLIT,"slits"); 
            obj_measure_slit_width_canvas.is_available_one_line = false;
            obj_measure_slit_width_canvas.reset();
            canvasManager.clearShapeCanvas();
            obj_slit_item_inspector.drawAllSlits(canvasManager);
            boxContentMeasureSlitWidth.innerHTML = "";
            let polygon = obj_slit_item_inspector.getPolygons()
            if (polygon){
                    obj_slit_item_inspector.setPolygons(polygon);
                    obj_slit_item_inspector.drawPolygons(canvasManager,polygon,imageWidth,WIDTH_IMG_SHAPE);
                }

        } else {
            let alertMessage = "❌ THÔNG BÁO LỖI DỮ LIỆU NHẬP VÀO:\n\n";
            write_log_clear(log_slit_measure,alertMessage);
            result_validate_probationarier.errors.forEach(err => {
                write_log_append(log_slit_measure,`📍 Dòng lỗi: [${err.rowName}]`);
                write_log_append(log_slit_measure,` - Giá trị hiện tại: ${err.currentVal}`);
                write_log_append(log_slit_measure,` - Yêu cầu nên là: ${err.expected}`);  
            });
        }
    });
    
    const btnClear = document.createElement("button");
    btnClear.className = "btn btn-clear"; // Giữ nguyên class CSS cũ
    btnClear.id = `btn-clear-${id_line}`;
    btnClear.textContent = "Xóa";
    btnClear.addEventListener("click", () => {
        rows.forEach((_, index) => {
            const inp = document.getElementById(`measure-slit-width-input-${id_line}-${index}`);
            if (inp) inp.value = index === 0 ? "" : 0;
        });
    });
    actions.appendChild(btnAccept);
    actions.appendChild(btnClear);
    wrapper.appendChild(table);
    wrapper.appendChild(actions);
    return wrapper; 
}

btn_exit_slit.addEventListener("click",()=>{
    console.log("Bạn vừa exit đo khe hàn");
    canvasManager.clearShapeCanvas();
    canvasManager.clearPreviewCanvas();
    canvasManager.setTool(null);//đặt canvas bằng null
    boxContentMeasureSlitWidth.innerHTML = "";
    panner_measure_slit_width.classList.remove("active");
    refesh_btn();
    get_obj_product().clearHighlight(scroll_container);
    setNameEventActivate(null);
});

btn_judment_slit.addEventListener("click",async()=>{
    let obj_slit_item_inspector = create_obj_cross_item(ItemsInspector.TYPE_SLIT,SlitItemInspector,"setSlitItems");
    console.log("Bạn vừa nhấn vào phán định khe hàn");
    let status_selected =  checkSelected(selected);
    if (status_selected){
        write_log_clear(log_slit_measure,"");
        let result_judment = await postData("/law_regulation/slit/run_model",selected);
        console.log("result_judment",result_judment);
        let status_judment =  result_judment?.ok;
        let message_judment =  result_judment?.message;
        if (!status_judment){
                write_log_clear(log_slit_measure,message_judment);return;
        }
        let width_judment =  result_judment?.data?.width;
        let polygon_judment =  result_judment?.data?.polygon;
        if (width_judment!= undefined &&  polygon_judment!= undefined){
                obj_slit_item_inspector.setPolygons(polygon_judment);
                imageWidth = width_judment;// 2 biến chỗ này bằng giá trị của nhau 
                obj_slit_item_inspector.drawPolygons(canvasManager,polygon_judment,width_judment,WIDTH_IMG_SHAPE);
            }
        }

})




