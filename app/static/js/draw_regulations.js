// import {postData,scroll_content,clearn_div,video_product,wrap_canvas,
//     WIDTH_IMG_SHAPE,HEIGH_IMG_SHAPE,cImg,ctxImg,cShape,ctxShape,cPrev,ctxPrev,drawImageContain,
//     getMousePositionInCanvas,CLICK_DELAY,drawPoint,checkPointClickInline,drawTransparentLine,isPointOnLineSegment,drawTextOnLine} from "./common_value.js"
import {postData,clearn_div,video_product,wrap_canvas,
    WIDTH_IMG_SHAPE,HEIGH_IMG_SHAPE,cImg,ctxImg,cShape,ctxShape,cPrev,ctxPrev,drawImageContain,
    getMousePositionInCanvas,CLICK_DELAY,drawPoint,checkPointClickInline,drawTransparentLine,isPointOnLineSegment,drawTextOnLine} from "./common_value.js"

const paner_draw_regulations  = document.getElementById("paner-draw-regulations");
const header_ul_li_draw_regulations = document.getElementById("header-ul-li-draw-regulations");
const btn_close_draw = document.getElementById("btn-close-draw-regualations");
const log_regulations =  document.getElementById("log-regulations");
const table_regulations = document.getElementById("table"); 
const btn_accept_and_send_server = document.getElementById("btn-accept-and-send-server");
const btn_all_erase = document.getElementById("btn-all-erase");
const btn_data_one_erase = document.getElementById("btn-erase");

const labelToKey = {
        "Tên":"name",
        "Màu": "color",
        "Level 1 (NG)": "level1",
        "Level 2 (NG)": "level2",
        "Level 3 (NG)": "level3",
        "Level 4 (OK)": "level4"
};


let lastMouseDownTime = 0;


let divCreateList = [];    //Lu danh sach cac diem  master the
let data_regulation_draw = {};
let arr_line = [];            // Lưu danh sách các line [[]]
let current_index_img = -1;  //index ảnh hiện tại đang click
let start_draw = false




let startX = 0;
let startY = 0;
let isDraw = false;
let  NUMBER_OF_POINTS_ON_A_ATRAIGHT_LINE =  2  // Lần click thứ 2
let cout_all_point =  0
let old_name = ""; // Tên của đối tượng đang chỉnh sửa để khi sửa không bị trùng tên
// cPrev.addEventListener("mouseup", onUp);

data_regulation_draw["width"] = WIDTH_IMG_SHAPE
data_regulation_draw["heigh"] = HEIGH_IMG_SHAPE

cPrev.addEventListener("click", handleCanvasClick);
cPrev.addEventListener("dblclick", handleCanvasDoubleClick);
cPrev.addEventListener("mousemove", handleMouseMove);
cPrev.addEventListener("mousedown",handleMouseDown);
// cPrev.addEventListener("mouseup",handleMouseUp);
// function handleMouseUp(event){}

wrap_canvas.addEventListener("contextmenu", function(e){
    e.preventDefault();
});


btn_accept_and_send_server.addEventListener("click",()=>{
    //Thiếu bước kiểm tra dữ liệu
    // if (validateFullData_Regulation(data_regulation_draw)){
    postData("/draw-regulations/accept_data", { "data_regulation": data_regulation_draw}).then(data => {
        RenderDataRegulation(data) 
        console.log(data);
    });
    // }
});

function handleMouseDown(event){
    if (start_draw){
        const { x, y } = getMousePositionInCanvas(cPrev,event);
        if (event.button == 0){
            const now = Date.now();
            const diff = now - lastMouseDownTime;

            // ❗ nếu click quá nhanh thì bỏ qua
            if (diff < CLICK_DELAY){
                console.log("Click quá nhanh → bỏ qua");
                return;
            }

            lastMouseDownTime = now;

            console.log("Ban vua click chuot trai");

            cout_all_point++;

            if (cout_all_point === 1 ) {

                if (checkPointClickInline(arr_line,x,y)){
                    cout_all_point--;
                    return;
                }

                // Lần click đầu
                startX = x;
                startY = y;
                isDraw = true;

                drawPoint(ctxShape,x,y,2);
            }

            else if (cout_all_point === NUMBER_OF_POINTS_ON_A_ATRAIGHT_LINE) {

                drawPoint(ctxShape,x,y,NUMBER_OF_POINTS_ON_A_ATRAIGHT_LINE);

                ctxPrev.clearRect(0, 0, cPrev.width, cPrev.height);

                drawTransparentLine(ctxShape,startX,startY,x,y);

                let line = {
                    "PointStarX":startX,
                    "PointStarY":startY,
                    "PointEndX":x,
                    "PointEndY":y
                };

                arr_line.push(line);

                isDraw = false;
                cout_all_point = 0;

                console.log(arr_line);
            }
        }
        else if (event.button == 2){
            let arr_new_line = []
            console.log("Bạn vừa click chuột phải !");
            delete_table_regulation();   // xóa bảng đang chọn ghi kết quả đi trước.
            if (arr_line.length == 0 ){console.log("Hiện tại chưa vẽ đường thẳng nào !");}
            for(let line of arr_line){
            let x1 = line?.PointStarX;
            let y1 =  line?.PointStarY;
            let x2 = line?.PointEndX;
            let y2 = line?.PointEndY;
            console.log("x1",x1,"x2",x2,"y1",y1,"y2",y2,"x",x,"y",y);
            if (isPointOnLineSegment(x1,y1,x2,y2,x,y)){
                continue;
            }
            else{
                    arr_new_line.push(line);
            }
            }
            arr_line = arr_new_line;
            // Cap nhat lai du lieu tong sau khi xoa
            if (current_index_img == -1){
                console.log("Hien tai chua chon duoc index nao ca");
            }
            else{
                    data_regulation_draw[`${current_index_img}`] = arr_line;
            }
            ctxShape.clearRect(0, 0, cPrev.width, cPrev.height); //xóa các hình
            drawAllLines(ctxShape,arr_line);  // Vẽ lại cac hình sau khi xóa.

        }
    }
}







 


header_ul_li_draw_regulations.addEventListener("click",function(){
    console.log("Bạn vừa nhấn vào vẽ sản phẩm");
    write_log_regulation_clear("🖌 Tiến hành vẽ đường thẳng quy định.\n🌟 Để bắt đầu click vào \"Ảnh master\" muốn vẽ.");
    paner_draw_regulations.classList.add("active");
    postData("/draw-regulations", { "status": "UI_Draw" }).then(data => {
        RenderDataRegulation(data) 
    });
});


const buttons = document.querySelectorAll(".part-controler button");
buttons.forEach((btn,index) =>{
    btn.addEventListener("click",()=>{
        // console.log("index :",index);
        buttons.forEach(b => b.classList.remove("border-effect"));
        btn.classList.add("border-effect");
    });
});
    

btn_close_draw.addEventListener("click",function(){
      fetch('/draw-regulations/exit')
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




function handleCanvasDoubleClick(event){
     const { x, y } = getMousePositionInCanvas(cPrev,event);
     console.log(x,y);
     console.log("Ban vừa nhấn double click");
     const status_or_data_check =  checkPointClickInline(arr_line,x,y);
     if (status_or_data_check){
        console.log("doublelick cua ban da click trung vao co day");
        console.log("Object line",status_or_data_check);  //status_or_data_check truyen nay vao ham . gia tri co the thay doi
        create_table_regulation(status_or_data_check); 
     }
     else{
         console.log("doublelick cua ban da click sai ");
     }
}





function  handleCanvasClick(event){
     const { x, y } = getMousePositionInCanvas(cPrev,event);
     console.log(`Click vào tọa độ: ${x},${y}.`);
}
function handleMouseMove(event){
    const { x, y } = getMousePositionInCanvas(cPrev,event);
    if ((startX != x || startY != y ) && isDraw){
        previewLine(cPrev,ctxPrev,x,y);
    } 
    coordinate.innerHTML = `Pixel: ${x.toFixed(0)}, ${y.toFixed(0)}.`;
    
}


function delete_table_regulation() {
    table_regulations.innerHTML = "";
    table_regulations.style.display = "none";
}


function create_table_regulation(status_or_data_check = {}) {

    table_regulations.style.display = "block";
    table_regulations.innerHTML = "";

    const labels = ["Tên","Màu","Level 1 (NG)","Level 2 (NG)","Level 3 (NG)","Level 4 (OK)"];
    old_name = status_or_data_check.name || "";  //tim ten cu cua no truoc
    console.log("oldname",old_name);


    // ====== TẠO TABLE ======
    labels.forEach(label => {

        const tr = document.createElement("tr");
       
        const th = document.createElement("th");
        th.textContent = label;

        const td = document.createElement("td");

        const input = document.createElement("input");
        input.className = "input-field";

        const key = labelToKey[label];
        input.dataset.key = key;

        // ====== XÁC ĐỊNH TYPE ======
        if (key === "name") {
            
            
            input.type = "text";
            input.placeholder = "Nhập tên";
        }
        else if (key === "color") {
            input.type = "color";
           input.value = "#ffff00";
        }
        else {
            input.type = "number";
            input.placeholder = "Nhập giá trị (mm)";
            input.step = "any"; // hỗ trợ float
        }

        // ====== AUTO FILL NẾU CÓ DATA ======
        if (key in status_or_data_check) {
            input.value = status_or_data_check[key];
        }

        td.appendChild(input);
        tr.appendChild(th);
        tr.appendChild(td);

        table_regulations.appendChild(tr);
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

    table_regulations.appendChild(btn_container);

    // ====== EVENT CLEAR ======
    btn_clear.addEventListener("click", () => {

        write_log_regulation_clear("Nhập lại dữ liệu hợp lệ");

        const inputs = table_regulations.querySelectorAll("input");

        inputs.forEach(input => {
            if (input.type === "color") {
                input.value = "#ff0000";
            } else {
                input.value = "";
            }
        });
    });

    // ====== EVENT ACCEPT ======
    btn_accept.addEventListener("click", () => {
        const inputs = table_regulations.querySelectorAll("input");
        if (validateData_level(labelToKey,inputs,old_name)) {
            inputs.forEach(input => {
                    const key = input.dataset.key;
                    const value = input.value.trim();
                    if (key.startsWith("level")) {
                        status_or_data_check[key] = Number(value);  // ✅ level là number
                    } else {
                        status_or_data_check[key] = value;          // ✅ ten, color giữ string
                    }
            });
            console.log("Dữ liệu sau khi lưu:", status_or_data_check);
            console.log("Lưu dữ liệu vào tổng hình ảnh");
            if (current_index_img == -1){
                console.log("Hien tại chưa click vào sản phẩm nào");
            }else{
                data_regulation_draw[`${current_index_img}`] = arr_line;
                console.log("du lieu tong data_regulation_draw :",data_regulation_draw);
            }
            delete_table_regulation();   // xóa bảng đang chọn ghi kết quả đi trước.
            //Cap nhat lai mau ve
            ctxShape.clearRect(0, 0, cPrev.width, cPrev.height); //xóa các hình
             drawAllLines(ctxShape,arr_line);  // Vẽ lại cac hình sau khi xóa.
        }
    });
}




function validateData_level(labelToKey, inputs, oldName = null) {
    let data = {};

    // ✅ 1. Gom dữ liệu từ các input
    inputs.forEach(input => {
        const key = input.dataset.key;
        if (key) {
            data[key] = input.value.trim();
        }
    });

    // ✅ 2. Kiểm tra tên không được để trống
    if (!data.name) {
        const msg = "👊 Tên line không được để trống.";
        console.log(msg);
        write_log_regulation_clear(msg);
        return false;
    }

    // ✅ 3. KIỂM TRA TRÙNG TÊN (Có xử lý trường hợp ĐANG SỬA)
    if (arr_line && arr_line.length > 0) {
        for (const item of arr_line) {
            // Nếu tên nhập vào trùng với một tên đã có trong danh sách
            // VÀ tên đó KHÔNG PHẢI là tên cũ của chính nó (oldName)
            if (item?.name === data.name && data.name !== oldName) {
                const msg = `👊 Tên "${data.name}" đã tồn tại, vui lòng chọn tên khác.`;
                console.log(msg);
                write_log_regulation_clear(msg);
                return false; 
            }
        }
    }

    // ✅ 4. Kiểm tra định dạng màu (HEX Color)
    const colorRegex = /^#[0-9A-Fa-f]{6}$/;
    if (!colorRegex.test(data.color)) {
        const msg = "👊Mã màu không hợp lệ (Ví dụ: #FF0000).";
        console.log(msg);
        write_log_regulation_clear(msg);
        return false;
    }

    // ✅ 5. Trích xuất và sắp xếp các key level theo thứ tự (level1, level2, ...)
    const levelKeys = Object.values(labelToKey)
        .filter(key => key.startsWith("level"))
        .sort((a, b) => {
            return parseInt(a.replace("level", "")) - parseInt(b.replace("level", ""));
        });

    let previousValue = null;
    let hasAnyLevel = false;
    let foundEmpty = false;

    for (let key of levelKeys) {
        let raw = data[key];
        // Nếu ô level này để trống
        if (!raw) {
            foundEmpty = true;
            continue;
        }
        // Nếu đã gặp một ô trống trước đó mà ô này lại có dữ liệu -> Lỗi nhảy bậc
        if (foundEmpty) {
            const msg = "👊 Không được bỏ trống level.";
            console.log(msg);
            write_log_regulation_clear(msg);
            return false;
        }
        hasAnyLevel = true;
        let value = parseFloat(raw);
        // Kiểm tra số hợp lệ
        if (isNaN(value) || !Number.isFinite(value)) {
            const msg = `👊 ${key} phải là một con số.`;
            console.log(msg);
            write_log_regulation_clear(msg);
            return false;
        }
        // Kiểm tra số âm
        if (value < 0) {
            const msg = `👊 ${key} không được là số âm.`;
            console.log(msg);
            write_log_regulation_clear(msg);
            return false;
        }
        // Kiểm tra thứ tự tăng dần (Level sau phải lớn hơn level trước)
        if (previousValue !== null && value <= previousValue) {
            const msg = `👊${key} phải lớn hơn level trước.`;
            console.log(msg);
            write_log_regulation_clear(msg);
            return false;
        }

        previousValue = value;
    }

    if (!hasAnyLevel) {
        const msg = "👊 Bạn phải nhập ít nhất một giá trị level.";
        console.log(msg);
        write_log_regulation_clear(msg);
        return false;
    }
    const msg = "💚 Dữ liệu hợp lệ.\n💚 Vẽ tiếp line tiếp theo.";
    write_log_regulation_clear(msg);
    return true;
}


function drawAllLines(ctx, arr_line, color = "yellow", width = 2, alpha = 0.3) {
    if (!Array.isArray(arr_line)) return;

    arr_line.forEach(line => {
        const x1 = line.PointStarX;
        const y1 = line.PointStarY;
        const x2 = line.PointEndX;
        const y2 = line.PointEndY;
        
        // Ưu tiên màu trong object line, nếu không có thì dùng màu mặc định
        const finalColor = line.color || color;
        const finalText = line.name || "";

        drawTextOnLine(ctx, x1, y1, x2, y2,finalText,"#FFFFFF")
        // Chỉ cần vẽ một lần với finalColor
        drawTransparentLine(ctx, x1, y1, x2, y2, alpha, finalColor);
        drawPoint(ctx, x1, y1, 2, finalColor);
        drawPoint(ctx, x2, y2, NUMBER_OF_POINTS_ON_A_ATRAIGHT_LINE, finalColor);
    });
}





function previewLine(canvas, ctx, currentX, currentY) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = "red";
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 4]); // nét đứt preview

    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(currentX, currentY);
    ctx.stroke();

    ctx.setLineDash([]);
}






























function write_log_regulation_clear(text){
    log_regulations.textContent = text;
}

function write_log_regulation_append(text){
    log_regulations.textContent += text;
}




function RenderDataRegulation(data){
    // scroll_content.innerHTML = "";
    video_product.style.display = "none";
    wrap_canvas.style.display = "flex";
    resizeAllCanvas();
    ctxImg.clearRect(0, 0, cImg.width, cImg.height);
    ctxShape.clearRect(0, 0, cShape.width, cShape.height);  // xóa hết ảnh cũ đi và tiến hành vẽ lại ảnh mới
    ctxPrev.clearRect(0, 0, cPrev.width, cPrev.height); 
    let status = data?.status;
    if (status == "erro"){console.log("Lỗi xảy ra :",data?.message);return;}
    data_regulation_draw  = data?.data_regualtion;
    data_regulation_draw["width"] = WIDTH_IMG_SHAPE
    data_regulation_draw["heigh"] = HEIGH_IMG_SHAPE
            const imgList = data?.path_arr_img;
            if (!imgList || imgList.length === 0) {write_log_regulation_clear("Hệ thống chưa có ảnh master nào"); console.log("Hệ thống chưa có ảnh master nào");return}
            console.log("Danh sách ảnh:", imgList);
            imgList.forEach((imgPath, index) => {
                const div_create = document.createElement("div");
                div_create.className = "div-index-img-mater";
                const h_create = document.createElement("p");
                h_create.innerText = `Ảnh master ${index}`;
                h_create.className = "p-index-img-master";
                const img = document.createElement("img");
                img.src = `${imgPath}?t=${Date.now()}`;  // dam bao  goi moi nhat
                img.alt = "Ảnh sản phẩm";
                img.style.width = "200px";
                img.style.margin = "10px";
                div_create.appendChild(img);
                div_create.appendChild(h_create);
                // scroll_content.appendChild(div_create);
                divCreateList.push(div_create);
                div_create.addEventListener("click", function () {
                    write_log_regulation_clear("✍️ Click chuột trái để vẽ các line.\n✍️ Trỏ vào line và click chuột phải để xóa line.\n✍️ Double click chuột trái để cấu hình cho line.\n✍️ Nhấn \"Áp dụng\" để lưu thông tin line.\n✍️Nhấn \"Xóa tất cả dữ liệu line\" để xóa tạm tất cả các line đã vẽ trong tất cả ảnh.\n✍️Nhấn \"Xóa dữ liệu quy định\" để xóa tạm các line trong ảnh hiện tại.")
                    start_draw =  true;
                    clearn_div(divCreateList);
                    console.log("Ảnh master đang chỉ tới là", index);
                    current_index_img = index;  // cap nhat bien toan cuc index
                    console.log("current_index_img : ", current_index_img);
                    table_regulations.innerHTML = "";   //Khong cho bang hien len khi click nua

                    //Ve lai du lieu tuong ung
                    console.log("du lieu tong data_regulation_draw click div :",data_regulation_draw);
                    let draw_img_regulation = data_regulation_draw?.[index];
                    console.log("draw_img_regulation:", draw_img_regulation);
                    if (draw_img_regulation){
                        console.log("index dang dung");
                        arr_line =  draw_img_regulation;
                        ctxShape.clearRect(0, 0, cPrev.width, cPrev.height); //xóa các hình
                        drawAllLines(ctxShape,arr_line);  // Vẽ lại cac hình sau khi xóa.
                    }
                    else{
                        arr_line = [];
                        ctxShape.clearRect(0, 0, cPrev.width, cPrev.height); //xóa các hình
                        drawAllLines(ctxShape,arr_line);  // Vẽ lại cac hình sau khi xóa.
                    }
                    





                    div_create.classList.add("div_click");
                    if (img.complete && img.naturalWidth !== 0) {
                        drawImageContain(ctxImg,cImg,img); 
                    } 
                    else {
                        img.onload = () => {
                          drawImageContain(ctxImg,cImg,img);
                        };
                    }
                });
        });
    
}







function resizeAllCanvas() {
  wrap_canvas.style.width = WIDTH_IMG_SHAPE + "px";
  wrap_canvas.style.height = HEIGH_IMG_SHAPE + "px";
  const rect = wrap_canvas.getBoundingClientRect();
  const dpr =  1;
  [cImg, cShape, cPrev].forEach(c => {
    c.width  = Math.round(rect.width * dpr);
    c.height = Math.round(rect.height * dpr);
    c.style.width  = rect.width + "px";
    c.style.height = rect.height + "px";
    const ctx = c.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  });
}




btn_all_erase.addEventListener("click", function(){
    data_regulation_draw = {};
    arr_line = [];
    ctxShape.clearRect(0, 0, cPrev.width, cPrev.height); //xóa các hình
    drawAllLines(ctxShape,arr_line);  // Vẽ lại cac hình sau khi xóa.
    console.log("Đã vào xóa dữ liệu");
    write_log_regulation_clear("⚡Xóa dữ liệu tạm tất cả ảnh thành công.");
});
btn_data_one_erase.addEventListener("click", function(){
    arr_line = [];
    data_regulation_draw[`${current_index_img}`] = [];
    ctxShape.clearRect(0, 0, cPrev.width, cPrev.height); //xóa các hình
    drawAllLines(ctxShape,arr_line);  // Vẽ lại cac hình sau khi xóa.
    write_log_regulation_clear("⚡Xóa dữ liệu tạm ảnh thành công.");
});




// function validateFullData_Regulation(fullData) {
//     // 1. Kiểm tra xem có dữ liệu không
//     if (!fullData || typeof fullData !== 'object') {
//         write_log_regulation_clear("Dữ liệu không hợp lệ.");
//         return false;
//     }
//     // 2. Duyệt qua các key từ '0', '1', '2'... (các index ảnh)
//     // Chúng ta chỉ lấy các key là số để tránh check nhầm 'width', 'heigh'
//     const imageKeys = Object.keys(fullData).filter(key => !isNaN(key));
//     if (imageKeys.length === 0) {
//         write_log_regulation_clear("Không tìm thấy dữ liệu đường thẳng nào trên các ảnh.");
//         return false;
//     }
//     for (let index of imageKeys) {
//         let linesArray = fullData[index];
//         // Nếu ảnh này đã được click nhưng chưa vẽ đường nào
//         if (!Array.isArray(linesArray) || linesArray.length === 0) {
//             write_log_regulation_clear(`Ảnh số ${index} chưa có dữ liệu đo lường.`);
//             return false;
//         }
//         // 3. Duyệt qua từng đường thẳng trong ảnh này
//         for (let i = 0; i < linesArray.length; i++) {
//             let lineData = linesArray[i];

//             // Giả lập mảng inputs giả để dùng lại hàm validateData_level cũ
//             // Hoặc tối ưu nhất là gọi các bước check logic trực tiếp:
            
//             // Check tên trống
//             if (!lineData.name) {
//                 write_log_regulation_clear(`Ảnh ${index}, đường thẳng ${i+1}: Tên không được trống.`);
//                 return false;
//             }
//             // Check logic level (Dùng logic từ hàm cũ của bạn)
//             let previousValue = null;
//             let hasAnyLevel = false;
            
//             // Lấy danh sách level1, level2...
//             const levels = Object.keys(lineData)
//                 .filter(k => k.startsWith("level"))
//                 .sort((a, b) => parseInt(a.replace("level", "")) - parseInt(b.replace("level", "")));

//             for (let lKey of levels) {
//                 let val = lineData[lKey];
//                 if (val === undefined || val === null || val === "") continue;

//                 let num = parseFloat(val);
//                 hasAnyLevel = true;

//                 if (isNaN(num) || num < 0) {
//                     write_log_regulation_clear(`Ảnh ${index}, Line "${lineData.name}": ${lKey} phải là số dương.`);
//                     return false;
//                 }

//                 if (previousValue !== null && num <= previousValue) {
//                     write_log_regulation_clear(`Ảnh ${index}, Line "${lineData.name}": ${lKey} phải lớn hơn level trước.`);
//                     return false;
//                 }
//                 previousValue = num;
//             }

//             if (!hasAnyLevel) {
//                 write_log_regulation_clear(`Ảnh ${index}, Line "${lineData.name}": Phải có ít nhất 1 level.`);
//                 return false;
//             }
//         }

//         // 4. KIỂM TRA TRÙNG TÊN TRONG CÙNG 1 ẢNH
//         const names = linesArray.map(l => l.name);
//         const hasDuplicateName = names.some((name, idx) => names.indexOf(name) !== idx);
//         if (hasDuplicateName) {
//             write_log_regulation_clear(`Ảnh ${index} có các đường thẳng bị trùng tên nhau.`);
//             return false;
//         }
//     }
//     write_log_regulation_clear("Toàn bộ dữ liệu hợp lệ! Đang gửi lên server...");
//     return true;
// }


// function check_validation_frame(data){
//     data_regulation_draw =  

// }
// function  checkPointClickInline(arr_point,x,y){
//     //xy là tọa độ của điểm vừa click .
//     if (arr_point.length == 0 ){console.log("Hiện tại chưa vẽ đường thẳng nào !");return false}
//     for(let line of arr_point){
//            let x1 = line?.PointStarX;
//            let y1 = line?.PointStarY;
//            let x2 = line?.PointEndX;
//            let y2 = line?.PointEndY;
//            if (isPointOnLineSegment(x1,y1,x2,y2,x,y)){
//                   return true,(x1,y1,x2,y2);
//            }
//     }
//     return false,null;
// }
