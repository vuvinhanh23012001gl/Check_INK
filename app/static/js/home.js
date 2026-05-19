// import {postData,scroll_content,clearn_div,video_product,wrap_canvas,logSocketData,logSocket,WIDTH_IMG_SHAPE,HEIGH_IMG_SHAPE,set_camera_connection} from "./common_value.js"
import {postData,clearn_div,video_product,wrap_canvas,logSocketData,logSocket,WIDTH_IMG_SHAPE,HEIGH_IMG_SHAPE,set_camera_connection} from "./common_value.js"


const status_judment = document.querySelector(".paner-main-status-product");
const log_judment = document.getElementById("log_judment");
const btn_left = document.querySelector(".scroll-up");   
const btn_right = document.querySelector(".scroll-down");
const scroll_container = document.querySelector(".scroll-container");
const div_show_point_detect = document.getElementById("table-show-point-detect");

const circle_status_connect_camera =  document.getElementById("element-circle-status-camera");
const label_status_connect_camera = document.getElementById("status-connect-cam");

let divCreateList_Home = [];

// const SCROLL_STEP = 300;
// btn_left.addEventListener("click", () => {
//   scroll_content.scrollBy({ left: -SCROLL_STEP, behavior: "smooth" });
// });
// btn_right.addEventListener("click", () => {
//   scroll_content.scrollBy({ left: SCROLL_STEP, behavior: "smooth" });
// });

scroll_container.addEventListener("scroll", Event_press_left_right);

logSocketData.on("data_output_judment", data =>{
  console.log("data judment :",data);
  handle_judment_realtime(data?.msg?.data_output_judment);
});


logSocketData.on("status_camera", data =>{
  let status_connect  = data?.status;
  // console.log("data",data);
  set_camera_connection(status_connect);
  isConect(status_connect,circle_status_connect_camera,label_status_connect_camera,"Camera");
});


logSocket.on("log_Home", (data) => {
    console.log("Dữ liệu sản phẩm nhận được log_Home :", data);
    log_judment.innerHTML += `<p>${data?.msg}</p>`;
});
function handle_judment_realtime(data)
{
  let arr_line = data?.arr_line;
  let img_package = data?.img;
  let index = data?.index;
  let status_judment_frame = data?.judment_frame;
  if (arr_line && img_package && index != undefined && status_judment_frame != undefined){
    console.log(`Dữ liệu phán định tại index:${index} hợp lệ.`);
    const table = create_show_table(arr_line);
    div_show_point_detect.innerHTML = "";
    div_show_point_detect.appendChild(table);
        Run_div(index,status_judment_frame,divCreateList_Home);
        video_product.src = `data:image/png;base64,${img_package}`; 
        // CSS inline để ảnh không quá to làm vỡ bảng
        video_product.style.width = `${WIDTH_IMG_SHAPE}px`;
        video_product.style.height = `${HEIGH_IMG_SHAPE}px`;
        wrap_canvas.style.display = "none";
        video_product.style.display = "flex";
        let status_judment = data?.judment;
        if (status_judment == undefined){
             setStatusDefault();
            
        }
        else if (status_judment){
            setStatusOK();
            clearn_div_img(divCreateList_Home);
        }
        else{
             setStatusNG();
            clearn_div_img(divCreateList_Home);
        }
        
  }
}

function Run_div(index, status_frame, div_card) {
  if (!div_card || !div_card[index]) return; // tránh lỗi nếu index sai

  // Xóa class cũ (nếu có)
  div_card[index].classList.remove('ok', 'erro');

  // Thêm class tương ứng
  if (status_frame) {
    div_card[index].classList.add('ok');
  } else {
    div_card[index].classList.add('erro');
  }
}


function create_show_table(data) {
  const headers = ["STT", "Tên line", "Chiều dài", "Level", "Trạng thái"];
  const table = document.createElement("table");
  table.className = "master-table";

  // 1. Tạo phần đầu (thead)
  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  headerRow.className = "master-header";
  
  headers.forEach(text => {
    const th = document.createElement("th");
    th.textContent = text;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  table.appendChild(thead);

  // 2. Tạo phần thân (tbody)
  const tbody = document.createElement("tbody");
  
  data?.forEach((item, index) => {
    const tr = document.createElement("tr");
    tr.className = "point-table";

    // --- XỬ LÝ LOGIC TẠI ĐÂY ---
    
    // Làm tròn chiều dài (width) - dùng Math.round()
    const displayWidth = (item?.width != null) ? Number(item.width).toFixed(3) : "";
    // Chuyển đổi trạng thái (status)
    const displayStatus = item?.status === true ? "OK" : (item?.status === false ? "NG" : "");
   
    const fields = [
      index + 1,          // STT
      item?.name_line, 
      displayWidth,       // Đã làm tròn
      item?.level, 
      displayStatus       // Hiển thị OK nếu true
    ];
    
    fields.forEach(text => {
      const td = document.createElement("td");
      td.textContent = text ?? ""; 
      tr.appendChild(td);
    });

    tbody.appendChild(tr);
  });
  
  table.appendChild(tbody);
  return table;
}
function Event_press_left_right() {
    // const scroll_width = scroll_content.scrollWidth;
    const scroll_client = scroll_container.clientWidth;
    const scroll_left = scroll_container.scrollLeft;
    if (scroll_width > scroll_client) {
      btn_left.style.display = scroll_left > 0 ? "block" : "none";
      btn_right.style.display = (scroll_left + scroll_client) < scroll_width ? "block" : "none";
    } else {
      btn_left.style.display = "none";
      btn_right.style.display = "none";
    }
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("Vào DOM");
 
  // const table = create_show_table(listData);
  // div_show_point_detect.appendChild(table);
  // setStatusOK();
    // setStatusNG();
  // setStatusWarning();

  postData("/data_home", {"status": "UI_Main"}).then(data => {
        RenderDataHome(data) 
        console.log('data',data);
   }); 
});


   

function RenderDataHome(data){
    // scroll_content.innerHTML = "";
    video_product.style.display = "flex";
    wrap_canvas.style.display = "None";
    let status = data?.status;
    if (status == "erro"){
        console.log("Lỗi chọn sản phẩm ");
    }
    else{   
            const imgList = data?.path_arr_img;
            
            console.log("Danh sách ảnh:", imgList);
        //     imgList.forEach((imgPath, index) => {
        //         const div_create = document.createElement("div");
        //         div_create.className = "div-index-img-mater";
        //         const h_create = document.createElement("p");
        //         h_create.innerText = `Ảnh master ${index}`;
        //         h_create.className = "p-index-img-master";
        //         const img = document.createElement("img");
        //         img.src = `${imgPath}?t=${Date.now()}`;  // dam bao  goi moi nhat
        //         img.alt = "Ảnh sản phẩm";
        //         img.style.width = "200px";
        //         img.style.margin = "10px";
        //         div_create.appendChild(img);
        //         div_create.appendChild(h_create);
        //         scroll_content.appendChild(div_create);
        //         divCreateList_Home.push(div_create);
        //         div_create.addEventListener("click", function () {
        //             clearn_div(divCreateList_Home);
        //             console.log("Ảnh master đang chỉ tới là", index);
        //             div_create.classList.add("div_click");
        //             video_product.src = `${imgPath}?t=${Date.now()}`;  
        //             video_product.style.width = "1365.33px";
        //             video_product.style.height = "1024px";
        //             video_product.style.display = "flex";
        //         });
        // });
    }
}
function clearn_div_img(div_card) {
  if (!div_card) return;
  for (let i = 0; i < div_card.length; i++) {
    div_card[i].classList.remove('ok', 'erro');
  }
}
function resetStatusDisplay() {
      status_judment.innerHTML ="--";
      status_judment.classList.remove("WARNING");
      status_judment.classList.remove("NG");
      status_judment.classList.remove("OK");
}
function setStatusOK() {
    resetStatusDisplay();
    status_judment.classList.add("OK");
    status_judment.innerHTML = "OK";
}

function setStatusWarning() {
    resetStatusDisplay();
    status_judment.classList.add("WARNING");
    status_judment.innerHTML = "⚠️ CẢNH BÁO";
}
function setStatusDefault() {
    resetStatusDisplay();
    status_judment.innerHTML = "--";
}
function setStatusNG() {
    resetStatusDisplay();
    status_judment.classList.add("NG");
    status_judment.innerHTML = "NG";
}

function isConect(isconect,element_circle,element_lable,str_lable){
    if (isconect) {
        element_circle.classList.remove("off");
        element_circle.classList.add("on");
        element_lable.innerText = `${str_lable} đã kết nối`;
        } else {
        element_circle.classList.add("off");
        element_circle.classList.remove("on");
        element_lable.innerText = `${str_lable} mất kết nối`;
    }  
}