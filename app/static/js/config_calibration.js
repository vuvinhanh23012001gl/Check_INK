// import {scroll_content,wrap_canvas,video_product,HEIGH_IMG_SHAPE,WIDTH_IMG_SHAPE,show_video_product,postData,
//     get_camera_connection,cImg,ctxImg,cShape,ctxShape,cPrev,ctxPrev,
//     drawImageContain,coordinate,getMousePositionInCanvas,CLICK_DELAY
//     ,drawPoint,drawTransparentLine,isPointOnLineSegment,drawTextOnLine,logSocket,logSocketData,fetchGet
// } from "./common_value.js" // them scoll

import {wrap_canvas,video_product,HEIGH_IMG_SHAPE,WIDTH_IMG_SHAPE,show_video_product,postData,
    get_camera_connection,cImg,ctxImg,cShape,ctxShape,cPrev,ctxPrev,
    drawImageContain,coordinate,getMousePositionInCanvas,CLICK_DELAY
    ,drawPoint,drawTransparentLine,isPointOnLineSegment,drawTextOnLine,logSocket,logSocketData,fetchGet
} from "./common_value.js"
console.log("-- Vào cấu hình calibration--");


const paner_draw_calibration = document.getElementById("paner-calibration");
const header_ul_li_draw_calibration = document.getElementById("header-ul-li-draw-calibration");
const open_video = document.getElementById("open-video");
const capture_calibration = document.getElementById("capture-calibration");
const log_calibration = document.getElementById("log-calibration");
const table_calibration = document.getElementById("table_calibration"); 
const calcular_calibration_button = document.getElementById("calcular-calibration-button");
const cancel_calibration_button  = document.getElementById("cancel-calibration-button");

let canvasEventAdded = false;
let start_draw_calibration = false;
let lastMouseDownTime = 0;
let cout_all_point = 0;
let startX = 0;
let startY = 0;
let isDraw = false;
let  NUMBER_OF_POINTS_ON_A_ATRAIGHT_LINE =  2  
let status_enough_points =  false;

let data_calibration = {
    name: "",
    PointStarX: 0,
    PointStarY: 0,
    PointEndX: 0,
    PointEndY: 0,
    reality:0,
    numberCapture:0,
};


logSocket.on("log_calibration", (data) => {
    if (data?.status == undefined){ write_log_calibration_append(`${data?.msg}`);}
});

logSocketData.on("data_calibration", (data) => {
    let img_calibration  = data.data?.data_img;
    let data_table_calibration = data.data?.data_table;
    console.log("data_table_calibration",data_table_calibration);
    console.log("calibration",data);
    if (data_table_calibration){ create_table_inf_calibration(data_table_calibration);}
    if (img_calibration){ CreateDivImg_append(img_calibration); }
});

calcular_calibration_button.addEventListener("click",function(){
    write_log_calibration_clear("✅Bắt đầu tính Calibration.\n");
    console.log(" Dữ liệu trước khi gửi là :",data_calibration);
    let status_validate = validateCalibrationData(data_calibration);
    if (status_validate?.status){
    postData("/calibration/calculator", {"line":data_calibration})
    .then(data => {
            let satus = data?.status;
            if (!satus){
                let message  = data?.msg;
                write_log_calibration_clear(`Server gửi dữ liệu thất bại do : ${message}`);
                return;
            }
            clearAllCanvas();
    });
    }
    else{
        write_log_calibration_clear(`${status_validate?.message}`);
    }
})


header_ul_li_draw_calibration.addEventListener("click",function(){
    write_log_calibration_clear("✅Để setup thông số Calibration.\n✅Nhấn \"Video Stream Camera\" ➡️ \"Chụp ảnh\" ➡️ Click ảnh vừa chụp ➡️ Vẽ và cấu hình ➡️ Nhấn \"Tính Calibration\" để phần mềm tự cấu hình tính toán. ");
    console.log(" Vào đây rồi paner Calibration !");
    paner_draw_calibration.classList.add("active");
    status_head_into();
    initCanvasEvent();
    fetchGet("/calibration/init_data")
        .then(data => {
            create_table_inf_calibration(data);
        });
    
});

cancel_calibration_button.addEventListener("click",function(){
    console.log("Bạn vừa nhấn vào cancel caiibration");
        fetch('/calibration/exit')
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

function create_table_inf_calibration(data){
    if(!data){console.log("Dữ liệu bảng hiện tại trống"); return;}
    let deafault = data?.default;
    if (deafault){
        console.log("Bạn chưa cài đặt thông số calibration hãy chụp ảnh và cài đặt lại");
        return;
    }
    const KEY_MAP = {
        "calibration": "Tỷ số Calibration (mm/px)",
        "scale_error_mm_per_pixel": "Sai số scale (mm/pixel)",
        "numberCapture":"Tổng số ảnh xử lý",
        "picture_ok": "Số ảnh hợp lệ",
        "picture_ng":"Số ảnh không hợp lệ",
        "reality":"Chiều dài thực tế(mm)",
        "pixel_mean": "Giá trị trung bình(pixel)",
        "pixel_std": "Độ lệch chuẩn(%)",
        "cv": "Hệ số biến thiên",
    };
    let tbody = document.getElementById("table_calibration");
    tbody.innerHTML = "";
    let tr_head = document.createElement("tr");
    ["Tiêu chí", "Giá trị"].forEach(text => {
        let td = document.createElement("td");
        td.textContent = text;
        tr_head.appendChild(td);
    });
    tbody.appendChild(tr_head);
    for (let key in data) {
        let tr = document.createElement("tr");
        let td_key = document.createElement("td");
        td_key.textContent = KEY_MAP[key] || key;
        if (td_key.textContent == "default"){continue;}
        if (td_key.textContent == "name"){continue;}
        let td_value = document.createElement("td");
        td_value.textContent = data[key];
        tr.appendChild(td_key);
        tr.appendChild(td_value);
        tbody.appendChild(tr);
    }
}


function handleMouseMove(event){
    const { x, y } = getMousePositionInCanvas(cPrev,event);
    if ((startX != x || startY != y ) && isDraw){
        previewLine(cPrev,ctxPrev,x,y);
    } 
    coordinate.innerHTML = `Pixel: ${x.toFixed(0)}, ${y.toFixed(0)}.`;
}


function previewLine(canvas, ctx, currentX, currentY) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.beginPath();
    ctx.strokeStyle = "rgba(255, 0, 0, 0.6)"; 
    ctx.lineWidth = 1.5; 
    ctx.setLineDash([4, 2]); 
    ctx.moveTo(startX, startY);
    ctx.lineTo(currentX, currentY);
    ctx.stroke();
    ctx.setLineDash([]);
}



function initCanvasEvent(){
    if (!canvasEventAdded){
        cPrev.addEventListener("click", handleCanvasClick);
        cPrev.addEventListener("dblclick", handleCanvasDoubleClick);
        cPrev.addEventListener("mousemove", handleMouseMove);
        cPrev.addEventListener("mousedown",handleMouseDown);
        canvasEventAdded = true;
    }
}

function handleMouseDown(event){
    if (start_draw_calibration){
        const { x, y } = getMousePositionInCanvas(cPrev,event);
        if (event.button == 0){
                    if (!status_enough_points){
                    const now = Date.now();
                    const diff = now - lastMouseDownTime;
                    if (diff < CLICK_DELAY){
                        console.log("Click quá nhanh → bỏ qua");
                        return;
                    }
                    lastMouseDownTime = now;
                    console.log("Ban vua click chuot trai");
                    cout_all_point++;
                    if (cout_all_point === 1 ) {
                        startX = x;
                        startY = y;
                        isDraw = true;
                        drawPoint(ctxShape,x,y,2);
                    }
                    else if (cout_all_point === NUMBER_OF_POINTS_ON_A_ATRAIGHT_LINE) {
                        drawPoint(ctxShape,x,y,NUMBER_OF_POINTS_ON_A_ATRAIGHT_LINE);
                        ctxPrev.clearRect(0, 0, cPrev.width, cPrev.height);
                        drawTransparentLine(ctxShape,startX,startY,x,y);
                        data_calibration.PointStarX = startX;
                        data_calibration.PointStarY  = startY;
                        data_calibration.PointEndX = x;
                        data_calibration.PointEndY = y;
                        isDraw = false;
                        cout_all_point = 0;
                        status_enough_points = true;
                    }
                    }else{
                     
                    }
           }
 
     else if (event.button == 2){
                table_calibration.innerHTML = "";
                let x1 = data_calibration?.PointStarX;
                let y1 =  data_calibration?.PointStarY;
                let x2 = data_calibration?.PointEndX;
                let y2 = data_calibration?.PointEndY;
                if (isPointOnLineSegment(x1,y1,x2,y2,x,y)){
                    status_enough_points =  false;
                    data_calibration = {
                        name: "",
                        PointStarX: 0,
                        PointStarY: 0,
                        PointEndX: 0,
                        PointEndY: 0
                    };
                    ctxShape.clearRect(0, 0, cPrev.width, cPrev.height); //xóa các hình
                    write_log_calibration_clear("Hãy vẽ đường line mới");
                }
               
        }
    }
}

function  handleCanvasClick(event){
     const { x, y } = getMousePositionInCanvas(cPrev,event);
     console.log(`Click vào tọa độ: ${x},${y}.`);
}

capture_calibration.addEventListener("click",function(){
    table_calibration.innerHTML = "";
    console.log("Bạn vừa nhấn vào chụp ảnh");
    postData("/calibration/capture")
    .then(data => {
        if (data?.status == "ok"){
            write_log_calibration_clear("✔️ Chụp ảnh thành công.\n✅ Hãy vẽ dữ liệu quy định giống với bước vẽ master quy định. Sau đó nhấn \"Tính Calibration\" để tính tham số Calibration");
            CreateDivImg(data?.img);
        }
        else if (data?.error == "error"){
            write_log_calibration_clear(`${data?.message}`)
        }
    });
});


function handleCanvasDoubleClick(event){
    const { x, y } = getMousePositionInCanvas(cPrev,event);
    // let name =  data_calibration?.name;
    let x1 = data_calibration?.PointStarX;
    let y1 =  data_calibration?.PointStarY;
    let x2 = data_calibration?.PointEndX;
    let y2 = data_calibration?.PointEndY;
    if (isPointOnLineSegment(x1,y1,x2,y2,x,y)){
        write_log_calibration_clear("✔️ Nhập thông tin vào ô tương ứng.")
        console.log("Double vào đúng đường thẳng cần tạo bảng");
        create_table_regulation(data_calibration);
    }

}


open_video.addEventListener("click",function(){
    // if (get_camera_connection()){
    //     show_video_product();
    // }
    // else{
    // }
    
    clearAllCanvas();
    data_calibration = {
        name: "",
        PointStarX: 0,
        PointStarY: 0,
        PointEndX: 0,
        PointEndY: 0,
        reality:0,
        numberCapture:0,
    };
    show_video_product();
    wrap_canvas.style.display = "none";
    write_log_calibration_clear("⚙️Cần vẽ 1 đường Line để cấu hình Calibration.\n📷Trong quá trình chụp hãy giữ nguyên vị trí camera, đồ gá, vật để giữ đúng tỷ lệ.\n➡️ Nhấn \"Chụp ảnh\" ➡️ Click ảnh vừa chụp ➡️ Vẽ và cấu hình ➡️ Nhấn \"Tính Calibration\" để phần mềm tự cấu hình tính toán.");
});    
function status_head_into() {
    // scroll_content.innerHTML =  "";
    video_product.style.height = `${HEIGH_IMG_SHAPE}px`;
    video_product.style.width =  `${WIDTH_IMG_SHAPE}px`;
    wrap_canvas.style.display =  "none";
    video_product.style.display =  "flex";
}


function write_log_calibration_clear(text){
    log_calibration.textContent = text;
}

function write_log_calibration_append(text){
    log_calibration.textContent += text;
}



function CreateDivImg(data_base64){
    if (!data_base64){
        write_log_calibration_clear("Dữ liệu ảnh rỗng.");
        return;
    }
    // container
    const div_create = document.createElement("div");
    div_create.className = "div-index-img-mater";
    // title
    const h_create = document.createElement("p");
    h_create.innerText = "Ảnh Calibration";
    h_create.className = "p-index-img-master";
    // scroll_content.innerHTML = "";
    // image preview nhỏ
    const img = new Image();
    img.src = "data:image/jpeg;base64," + data_base64;
    img.alt = "Ảnh sản phẩm";
    img.style.width = "200px";
    img.style.margin = "10px";

    // append DOM
    div_create.appendChild(img);
    div_create.appendChild(h_create);
   // scroll_content.appendChild(div_create);

    // click ảnh
    div_create.addEventListener("click", function(){
          // reset trạng thái vẽ
        cout_all_point = 0;
        startX = 0;
        startY = 0;
        isDraw = false;
        status_enough_points = false;
        start_draw_calibration = true;
        document.querySelectorAll(".div-index-img-mater")
        .forEach(el => el.classList.remove("div_click"));

        div_create.classList.add("div_click");

        // ẩn video
        video_product.style.display = "none";

        // hiện canvas
        wrap_canvas.style.display = "block";
        wrap_canvas.style.width = WIDTH_IMG_SHAPE + "px";
        wrap_canvas.style.height = HEIGH_IMG_SHAPE + "px";

        setupCanvasSize();
        drawImageContain(ctxImg, cImg, img);

    });

}

function clearAllCanvas() {
    ctxImg.clearRect(0, 0, cImg.width, cImg.height);
    ctxPrev.clearRect(0, 0, cPrev.width, cPrev.height);
    ctxShape.clearRect(0, 0, cShape.width, cShape.height);
    cout_all_point = 0;
    startX = 0;
    startY = 0;
    isDraw = false;
    status_enough_points = false;
    // scroll_content.innerHTML = "";
    data_calibration = {
    name: "",
    PointStarX: 0,
    PointStarY: 0,
    PointEndX: 0,
    PointEndY: 0,
    reality:0,
    numberCapture:0,
};
}


function CreateDivImg_append(data_base64){
    if (!data_base64){
        write_log_calibration_clear("Dữ liệu ảnh rỗng.");
        return;
    }
    // container
    const div_create = document.createElement("div");
    div_create.className = "div-index-img-mater";
    // title
    const h_create = document.createElement("p");
    h_create.innerText = "Ảnh Calibration";
    h_create.className = "p-index-img-master";
    // image preview nhỏ
    const img = new Image();
    img.src = "data:image/jpeg;base64," + data_base64;
    img.alt = "Ảnh sản phẩm";
    img.style.width = "200px";
    img.style.margin = "10px";
    // append DOM
    div_create.appendChild(img);
    div_create.appendChild(h_create);
    // scroll_content.appendChild(div_create);
    // click ảnh
    div_create.addEventListener("click", function(){
          // reset trạng thái vẽ
     
        document.querySelectorAll(".div-index-img-mater")
        .forEach(el => el.classList.remove("div_click"));

        div_create.classList.add("div_click");

        // ẩn video
        video_product.style.display = "none";

        // hiện canvas
        wrap_canvas.style.display = "block";
        wrap_canvas.style.width = WIDTH_IMG_SHAPE + "px";
        wrap_canvas.style.height = HEIGH_IMG_SHAPE + "px";

        setupCanvasSize();
        drawImageContain(ctxImg, cImg, img);

    });

}





function setupCanvasSize(){
    cImg.width = WIDTH_IMG_SHAPE;
    cImg.height = HEIGH_IMG_SHAPE;

    cPrev.width = WIDTH_IMG_SHAPE;
    cPrev.height = HEIGH_IMG_SHAPE;

    cShape.width = WIDTH_IMG_SHAPE;
    cShape.height = HEIGH_IMG_SHAPE;

}



function create_table_regulation(status_or_data_check = {}) {
    let name =  status_or_data_check?.name;
    let reality = status_or_data_check?.reality;
    let numberCapture = status_or_data_check?.numberCapture;
    table_calibration.innerHTML = "";
    table_calibration.style.display = "block";
    const labelToKey = {
        "Tên":"name",
        "Số lần chụp ảnh": "numberCapture",
        "Chiều dài thực tế": "reality"};

    const labels = ["Tên","Số lần chụp ảnh","Chiều dài thực tế"];
    // ====== TẠO TABLE ======
    labels.forEach(label => {
        const tr = document.createElement("tr");
        tr.className = "calibration-row"; // Thêm lớp cho hàng
        const th = document.createElement("th");
        th.textContent = label;
        const td = document.createElement("td");
        th.className = "calibration-label"; // Thêm lớp cho cột tiêu đề (nhãn
        const input = document.createElement("input");
        input.required = true;
        input.className = "input-field";
        td.className = "calibration-content"; // Thêm lớp cho cột nội dung
        const key = labelToKey[label];
        input.dataset.key = key;
        // ====== XÁC ĐỊNH TYPE ======
        if (key === "name") {
            input.type = "text";
            input.placeholder = "Nhập tên";
            if (name){input.value = name;}
        }
        else {
            input.type = "number";
            input.step = "any"; // hỗ trợ float
            // console.log("input.dataset.key",input.dataset.key);
            if (input.dataset.key == "numberCapture"){
                input.placeholder = "Nhập số lần chụp";
                if (numberCapture){input.value = numberCapture;}
            }
            else{
                 input.placeholder = "Nhập số mm thực tế";
                 if (reality){input.value = reality;}
            }
        }

        td.appendChild(input);
        tr.appendChild(th);
        tr.appendChild(td);

        table_calibration.appendChild(tr);
    });

    // ====== TẠO BUTTON ======
    const btn_container = document.createElement("div");
    btn_container.className = "btn-container";
    btn_container.style.display = "flex";
    btn_container.style.justifyContent = "center";
    btn_container.style.gap = "10px";

    const btn_clear = document.createElement("button");
    btn_clear.innerText = "Xóa hết";
    btn_clear.className = "btn";

    const btn_accept = document.createElement("button");
    btn_accept.innerText = "Chấp nhận";
    btn_accept.className = "btn";

    btn_container.appendChild(btn_clear);
    btn_container.appendChild(btn_accept);

    table_calibration.appendChild(btn_container);

    // ====== EVENT CLEAR ======
    btn_clear.addEventListener("click", () => {
        const inputs = table_calibration.querySelectorAll("input");
        inputs.forEach(input => {input.value = ""; }); });
      
        

    // // ====== EVENT ACCEPT ======
    btn_accept.addEventListener("click", () => {
       
        const inputs = table_calibration.querySelectorAll("input");
        const  status_validate = validateCalibration(table_calibration);
        if (status_validate){
            write_log_calibration_clear("✔️ Check dữ liệu đúng định dạng.\n✅ Nhấn \"Tính Calibration\" để cài đặt thông số Calibration tự động")
        let isValid = true;
        for (const input of inputs) {
            const key = input.dataset.key;
            if (!key) continue;

            let value = input.value.trim();

            // convert number
            if (input.type === "number") {
                value = Number(value);
            }
    
            if (key === "numberCapture") {
                if (value <= 2) {
                    alert("Bạn cần chụp ít nhất 3 hình");
                    input.value = "";   // ✅ fix đúng
                    input.focus();
                    isValid = false;
                    break; // ✅ dừng toàn bộ loop
                }
            }
            data_calibration[key] = value;
        }
        if (!isValid) return;
        table_calibration.innerHTML = "";
        ctxShape.clearRect(0, 0, cPrev.width, cPrev.height); //xóa các hình
        drawCalibration(ctxShape,data_calibration);
        }
    });
}

function validateCalibration(table) {
    const inputs = table.querySelectorAll("input");
    for (const input of inputs) {
        const key = input.dataset.key;
        const value = input.value.trim();

        // ===== kiểm tra rỗng =====
        if (value === "") {
               
        // ===== kiểm tra theo từng field =====
            if (key === "name") {
                alert("Tên phải có ít nhất 1 ký tự");
                input.focus();
                return false; }
            if (key === "numberCapture") {
                alert("Số lần chụp không  được bỏ trống");
                input.focus();
                return false; }
            if (key === "reality") {
                alert("Chiều dài không được bỏ trống");
                input.focus();
                return false;}
            
        }
        if (key === "numberCapture") {
            const num = Number(value);
            if (!Number.isInteger(num) || num <= 0) {
                alert("Số lần chụp phải là số nguyên > 0");
                input.focus();
                return false;
            }
            if (num >= 101){
                alert("Số lần chụp không được quá 100 lần ");
                input.focus();
                return false;
            }
        }
        if (key === "reality") {
            const num = Number(value);
            if (isNaN(num) || num <= 0) {
                alert("Chiều dài thực tế phải > 0");
                input.focus();
                return false;
            }
        }
    }
    return true;
}


function drawCalibration(ctx, data, color = "yellow", width = 2, alpha = 0.3) {
    if (!data) return;

    const x1 = data.PointStarX;
    const y1 = data.PointStarY;
    const x2 = data.PointEndX;
    const y2 = data.PointEndY;

    const finalColor = data.color || color;
    const finalText = data.name || "";

    drawTextOnLine(ctx, x1, y1, x2, y2, finalText, "#FFFFFF");
    drawTransparentLine(ctx, x1, y1, x2, y2, alpha, finalColor);

    drawPoint(ctx, x1, y1, 2, finalColor);
    drawPoint(ctx, x2, y2, NUMBER_OF_POINTS_ON_A_ATRAIGHT_LINE, finalColor);
}


function validateCalibrationData(data) {

    if (!data) {
        return { status:false, message:"Dữ liệu calibration rỗng" };
    }

    // ===== name =====
    if (!data.name || data.name.trim() === "") {
        return { status:false, message:"Tên calibration không được để trống" };
    }

    // ===== numberCapture =====
    if (!Number.isInteger(data.numberCapture) || data.numberCapture <= 0) {
        return { status:false, message:"Số lần chụp phải là số nguyên > 0" };
    }

    if (data.numberCapture > 100) {
        return { status:false, message:"Số lần chụp không được vượt quá 100" };
    }

    // ===== reality =====
    if (typeof data.reality !== "number" || data.reality <= 0) {
        return { status:false, message:"Chiều dài thực tế phải > 0" };
    }

    // ===== tọa độ =====
    const coords = [
        data.PointStarX,
        data.PointStarY,
        data.PointEndX,
        data.PointEndY
    ];

    for (const v of coords) {
        if (typeof v !== "number" || isNaN(v)) {
            return { status:false, message:"Tọa độ không hợp lệ" };
        }
    }

    // ===== kiểm tra trùng điểm =====
    if (
        data.PointStarX === data.PointEndX &&
        data.PointStarY === data.PointEndY
    ) {
        return { status:false, message:"Hai điểm calibration không được trùng nhau" };
    }

    return { status:true };
}