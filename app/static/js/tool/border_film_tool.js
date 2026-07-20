import {scroll_container,canvasManager,WIDTH_IMG_SHAPE}from "../common_value.js"
import {additional_events,obj_measure_film_border_canvas,boxConetentBorderFilm,get_obj_product,selected,checkSelected
} from "./common_value_tool.js"   
import {LineDrawer} from "../canvas/line_drawer_canvas.js"
import {FilmBorder} from "../model/model_film_border.js"
import {ItemsInspector} from "../services/items_inspector.js"
import {BorderFilmInspector} from "../services/border_film_inspector.js"
import {Line} from "../model/model_line.js"
import {postData} from "../utills/api.js";

let imageWidth = 0;//Cai nay se thay doi khi nhan vao che do tu dong quy uoc  
let obj_film_border_item_inspector = null;
let line = new Line();   // đối tượng line vẽ hiện tại.
additional_events.set("border_film_tool", event_transition_items);
const log_border_film  = document.getElementById("log-border-film");
const btn_judment_border_film =  document.getElementById("btn-judment-border-film");

obj_measure_film_border_canvas.on(LineDrawer.NAME_EVENT_WHEN_CLICK_RIGHT_LINE,func_callback_click_mouse_right);
obj_measure_film_border_canvas.on(LineDrawer.NAME_EVENT_WHEN_CLICK_ON_LINE,func_callback_click_on_line_drawn);
obj_measure_film_border_canvas.on(LineDrawer.NAME_EVENT_WHEN_CLICK_ON_LINE_HAVE_AREALY,func_callback_click_on_line_have_aready);



btn_judment_border_film.addEventListener("click",async()=>{
    console.log("Bạn vừa nhấn vào phán định đường viền");
    let status_selected =  checkSelected(selected);
    if (status_selected){
        write_log_clear("");
        let result_judment = await postData("/law_regulation/boder_film/judment_item",selected);
        console.log("result_judment",result_judment);
        let status_judment =  result_judment?.ok;
        let message_judment =  result_judment?.message;
        if (!status_judment){
                    write_log_clear(message_judment);return;
        }
        let width_judment =  result_judment?.data?.width;
        let polygon_judment =  result_judment?.data?.polygon;
        // console.log("polygon_judment",polygon_judment);
        //  console.log("width_judment",width_judment);
        if (width_judment!= undefined &&  polygon_judment!= undefined){
                obj_film_border_item_inspector.setPolygons(polygon_judment);
                imageWidth = width_judment;// 2 biến chỗ này bằng giá trị của nhau 
                obj_film_border_item_inspector.drawPolygons(canvasManager,polygon_judment,width_judment,WIDTH_IMG_SHAPE);
            }
        }
});


function event_transition_items(){
    if (selected.frame_id  == -1 ||selected.items_id  == -1 || selected.product_id ==  -1){console.log("Lỗi chưa chọn sản phâm");return;};
    boxConetentBorderFilm.innerHTML = ""; 
    obj_film_border_item_inspector = get_obj_product().find_item_object_corresponding(String(selected?.frame_id),String(selected?.items_id),ItemsInspector.TYPE_BORDER_FILM);
    if (!obj_film_border_item_inspector){
            // console.log("da tdsadsdasdsa");
            let obj_items_inspector = get_obj_product().get_item_object(String(selected?.frame_id),String(selected?.items_id));
            obj_film_border_item_inspector =  new BorderFilmInspector();
            obj_items_inspector.setBorderFilmItems(obj_film_border_item_inspector);
    }
    obj_measure_film_border_canvas.reset();
    console.log("đối tượng đang thao tác:",obj_film_border_item_inspector);
    obj_film_border_item_inspector.drawAll(canvasManager);
    let polygons = obj_film_border_item_inspector.getPolygons();
    if (polygons && imageWidth!= 0){obj_film_border_item_inspector.drawPolygons(canvasManager,polygons,imageWidth,WIDTH_IMG_SHAPE);}        
    console.log("đã tạo đối tượng ");
}

function func_callback_click_mouse_right(coordinate){
           boxConetentBorderFilm.innerHTML = ""; 
           let result_find_line  = obj_film_border_item_inspector.findClickedLine(coordinate.x,coordinate.y);
           if (result_find_line||coordinate.status_check_point_in_line_current){
                   obj_measure_film_border_canvas.is_available_one_line = false;  // moi them
                   obj_film_border_item_inspector.removeLine(result_find_line?.id_line);
                   canvasManager.clearShapeCanvas();
                   obj_film_border_item_inspector.drawAll(canvasManager);
             
                   let polygons = obj_film_border_item_inspector.getPolygons();
                  if (polygons && imageWidth!= 0){obj_film_border_item_inspector.drawPolygons(canvasManager,polygons,imageWidth,WIDTH_IMG_SHAPE);}
       
           }
}

function func_callback_click_on_line_drawn(line_current){
    console.log("line_current",line_current);
    boxConetentBorderFilm.innerHTML = ""; // reset html con
    // console.log("dict sau khi chuyen thanh de ve",obj_measurement_items_inspector.getAllDictLine());
    // console.log("line_current",line_current);
    line.xEnd =  Number(line_current?.xEnd);
    line.yEnd =  Number(line_current?.yEnd);
    line.xStart =  Number(line_current?.xStart);
    line.yStart =  Number(line_current?.yStart);   // setup cho line hiện tại
    let result_create_line_id_new = obj_film_border_item_inspector.findLineByCoordinate(line.xStart, line.yStart, line.xEnd,line.yEnd);
    // console.log("result_create_line_id_new",result_create_line_id_new);
   // let result_create_line_id_new = obj_measurement_items_inspector.findLineByCoordinate(5001, 520, 30, 40); //ham test
    // console.log(result_create_line_id_new.status ? `Line đã tồn tại: ${JSON.stringify(result_create_line_id_new, null, 2)}` : `Line mới, ID mới là ${result_create_line_id_new.data}`);
     if (!result_create_line_id_new || !result_create_line_id_new.status){
         let id_new = result_create_line_id_new?.data || obj_film_border_item_inspector.generateNextId();
         console.log("Line chưa tồn tại trong inspector. Tạo mới với ID:", id_new);
         boxConetentBorderFilm.appendChild(createMeasureBorderFilmTable(id_new, line));
     }
     else {
         console.log("Line đã tồn tại trong inspector. Đang nạp dữ liệu cũ...");
         const borderfilmClone = { ...result_create_line_id_new.data };
         boxConetentBorderFilm.appendChild(createMeasureBorderFilmTable(borderfilmClone.lineId, borderfilmClone));
     }
        
}
function func_callback_click_on_line_have_aready(coordinate_now){
    console.log("Click vao line da ton tai");
         boxConetentBorderFilm.innerHTML = ""; 
         let coordinate_now_x = coordinate_now?.x;
         let coordinate_now_y = coordinate_now?.y;
    
         console.log("coordinate_now",coordinate_now);
         let result_find_line  = obj_film_border_item_inspector.findClickedLine(coordinate_now_x,coordinate_now_y);
         if (!result_find_line){return;}
         obj_measure_film_border_canvas.have_return =  true; 
          func_callback_click_on_line_drawn(result_find_line);
}




function createMeasureBorderFilmTable(id_line, data_line) {
    const existed = document.getElementById(
        `measure-border-film-wrapper-${id_line}`
    );

    const wrapper = document.createElement("div");
    wrapper.id = `measure-border-film-wrapper-${id_line}`;

    const table = document.createElement("table");
    table.className = "measure-weld-width-config-table";
    table.id = `measure-border-film-table-${id_line}`;

    const rows = [
        "Tên đường",
        "Độ rộng Min",
        "Độ rộng Max"
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
        input.id = `measure-border-film-input-${id_line}-${index}`;

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

    const actions = document.createElement("div");
    actions.className = "config-actions";
    actions.id = `measure-border-film-actions-${id_line}`;

    const btnAccept = document.createElement("button");
    btnAccept.className = "btn btn-accept";
    btnAccept.id = `measure-border-film-btn-accept-${id_line}`;
    btnAccept.textContent = "Chấp nhận";

    btnAccept.addEventListener("click", () => {
        const nameLineVal =
            document.getElementById(`measure-border-film-input-${id_line}-0`)?.value || "";

        const widthMinVal = Number(
            document.getElementById(`measure-border-film-input-${id_line}-1`)?.value || 0
        );

        const widthMaxVal = Number(
            document.getElementById(`measure-border-film-input-${id_line}-2`)?.value || 0
        );

        const objFilmBorder = new FilmBorder(
            id_line,
            nameLineVal,
            widthMinVal,
            widthMaxVal,
            line?.xStart ?? 0,
            line?.yStart ?? 0,
            line?.xEnd ?? 0,
            line?.yEnd ?? 0
        );

        console.log("objProbationary", objFilmBorder);

        const resultValidate = objFilmBorder.validateSlitLevelsIncreasing();

        console.log("resultValidate", resultValidate);

        if (resultValidate.isValid) {
            console.log("obj_film_border_item_inspector", obj_film_border_item_inspector);

            obj_film_border_item_inspector.addLine(objFilmBorder);

            console.log(
                "Kết quả sau khi thêm FilmBorder:",
                obj_film_border_item_inspector.toDict()
            );

            write_log_clear("✅ Dữ liệu hợp lệ.");

            obj_measure_film_border_canvas.is_available_one_line = false;
            obj_measure_film_border_canvas.reset();


            obj_film_border_item_inspector.drawAll(canvasManager);

            boxConetentBorderFilm.innerHTML = "";

            const polygon = obj_film_border_item_inspector.getPolygons();
            if (polygon) {
                obj_film_border_item_inspector.setPolygons(polygon);
                obj_film_border_item_inspector.drawPolygons(
                    canvasManager,
                    polygon,
                    imageWidth,
                    WIDTH_IMG_SHAPE
                );
            }
        } else {
            write_log_clear("❌ THÔNG BÁO LỖI DỮ LIỆU NHẬP VÀO:\n");

            resultValidate.errors.forEach(err => {
                write_log_append(`📍 Dòng lỗi: [${err.rowName}]`);
                write_log_append(` - Giá trị hiện tại: ${err.currentVal}`);
                write_log_append(` - Yêu cầu: ${err.expected}`);
            });
        }
    });

    const btnClear = document.createElement("button");
    btnClear.className = "btn btn-clear";
    btnClear.id = `measure-border-film-btn-clear-${id_line}`;
    btnClear.textContent = "Xóa";

    btnClear.addEventListener("click", () => {
        rows.forEach((_, index) => {
            const inp = document.getElementById(
                `measure-border-film-input-${id_line}-${index}`
            );
            if (inp) inp.value = index === 0 ? "" : 0;
        });
    });

    actions.appendChild(btnAccept);
    actions.appendChild(btnClear);

    wrapper.appendChild(table);
    wrapper.appendChild(actions);

    return wrapper;
}

function write_log_clear(text){
    log_border_film.textContent = text;
}

function write_log_append(text){
    log_border_film.style.whiteSpace = "pre-line"; 
    log_border_film.textContent += text + "\n";
}
