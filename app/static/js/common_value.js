
// export const scroll_content = document.getElementById("scroll-content");
export const video_product = document.getElementById("video-product");    // Hiển thị hình ảnh
export const wrap_canvas =  document.getElementById("wrap-canvas");       //Hien thi canvas
export const coordinate = document.getElementById("coordinate");
export  const WIDTH_IMG_SHAPE = 1280;
export const HEIGH_IMG_SHAPE = 960;
export const CLICK_DELAY = 300; // ms (200–300ms là hợp lý)

// 1. Kết nối đúng vào Namespace /log
export const SocketLog = io("http://127.0.0.1:8000/log");   //chuyen de lay log realt time

export const cImg = document.getElementById("canvasImage"); //IMG  
export const ctxImg = cImg.getContext("2d");

export const cShape = document.getElementById("canvasShape");  //Luu Hinh Ve
export const ctxShape = cShape.getContext("2d");

export const cPrev = document.getElementById("canvasPreview");  //Luu hinh preview
export const ctxPrev = cPrev.getContext("2d");
export function drawTextOnLine(ctx, x1, y1, x2, y2, text, color) {
    // 1. Tính trung điểm để đặt chữ vào giữa đường thẳng
    const midX = (x1 + x2) / 2;
    const midY = (y1 + y2) / 2;

    // 2. Tính góc của đường thẳng (để chữ xoay theo đường)
    const angle = Math.atan2(y2 - y1, x2 - x1);

    ctx.save(); // Lưu trạng thái canvas
    ctx.translate(midX, midY); // Di chuyển tâm đến trung điểm
    ctx.rotate(angle); // Xoay canvas theo góc của đường thẳng
    
    // Thiết lập font và màu sắc
    ctx.font = "18px Arial";
    ctx.fillStyle = color;
    ctx.textAlign = "center";
    
    // Vẽ chữ (offset lên trên một chút để không đè khít lên đường kẻ)
    ctx.fillText(text, 0, -5); 

    ctx.restore(); // Khôi phục lại trạng thái ban đầu
}




export function drawPoint(ctx, x, y, radius = 3, color = "yellow") {
    // ham nay dung de vẽ 1 điểm trên canvas
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
}
export function checkPointClickInline(arr_point, x, y) {
    if (!arr_point || arr_point.length === 0) return null;

    for (let line of arr_point) {
        if (isPointOnLineSegment(
            line.PointStarX,
            line.PointStarY,
            line.PointEndX,
            line.PointEndY,
            x,
            y
        )) {
            return line; // trả về luôn object line
        }
    }

    return null;
}

export function isPointOnLineSegment(x1, y1, x2, y2, px, py, tolerance = 5) {

    const dx = x2 - x1;
    const dy = y2 - y1;

    const length = Math.sqrt(dx * dx + dy * dy);
    if (length === 0) return false;

    // Khoảng cách thực sự từ điểm tới đường
    const distance = Math.abs(dy * px - dx * py + x2*y1 - y2*x1) / length;

    if (distance > tolerance) return false;

    const dot = (px - x1) * dx + (py - y1) * dy;

    if (dot < 0) return false;
    if (dot > dx * dx + dy * dy) return false;

    return true;
}








export function drawTransparentLine(ctx, x1, y1, x2, y2, alpha = 0.3, color = "yellow") {

    ctx.save();                // lưu trạng thái cũ
    ctx.globalAlpha = alpha;   // độ mờ (0 → 1)

    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);

    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.restore();             // trả lại trạng thái ban đầu
}
export function getMousePositionInCanvas(canvas, event) {
  const rect = canvas.getBoundingClientRect();

  const scaleX = canvas.width  / rect.width;
  const scaleY = canvas.height / rect.height;

  const x = Math.floor(event.offsetX * scaleX);  
  const y = Math.floor(event.offsetY * scaleY);
  if (x < 0){ x = 0;}
  if (x > WIDTH_IMG_SHAPE) {x =  WIDTH_IMG_SHAPE;}
  if (y < 0){ y = 0;}
  if (y > HEIGH_IMG_SHAPE) {y =  HEIGH_IMG_SHAPE;}
  return { x, y };
}

export function drawImageContain(ctx, canvas, img) {
    const cw = canvas.width;
    const ch = canvas.height;

    const iw = img.naturalWidth;
    const ih = img.naturalHeight;

    if (!iw || !ih) {
        console.warn("Image chưa load xong!");
        return null;
    }

    const scale = Math.min(cw / iw, ch / ih);

    const nw = iw * scale;
    const nh = ih * scale;

    const dx = (cw - nw) / 2;
    const dy = (ch - nh) / 2;

    ctx.clearRect(0, 0, cw, ch);
    ctx.drawImage(img, dx, dy, nw, nh);


}

const COM_KEY = "com_connected";

export function set_com_connection(isConnected) {
    // Lưu trạng thái kết nối (true/false) dưới dạng string
    sessionStorage.setItem(COM_KEY, isConnected ? "true" : "false");
}

export function get_com_connection() {
    // Khởi tạo giá trị mặc định là false nếu chưa có trong session
    if (sessionStorage.getItem(COM_KEY) === null) {
        sessionStorage.setItem(COM_KEY, "false");
    }
    // Trả về kiểu Boolean chuẩn
    return sessionStorage.getItem(COM_KEY) === "true";
}


const CAMERA_KEY = "camera_connected";
export function set_camera_connection(isConnected) {
    // Lưu trạng thái kết nối (true/false) dưới dạng string
    sessionStorage.setItem(CAMERA_KEY, isConnected ? "true" : "false");
}
export function get_camera_connection() {
    // Khởi tạo giá trị mặc định là false nếu chưa có trong session
    if (sessionStorage.getItem(CAMERA_KEY) === null) {
        sessionStorage.setItem(CAMERA_KEY, "false");
    }
    // Trả về kiểu Boolean chuẩn
    return sessionStorage.getItem(CAMERA_KEY) === "true";
}

SocketLog.on("connect", () => {
    console.log("Đã kết nối vào kênh SocketLog. ID:", SocketLog.id);
});

SocketLog.on("disconnect", () => {
    console.log("Đã mất kết nối với kênh SocketLog");
});

export const SocketData = io("http://127.0.0.1:8000/data"); // chuyen de truyen data real time
SocketData.on("connect", () => {
    console.log("Đã kết nối vào kênh SocketData . ID:", SocketData.id);
});

SocketData.on("disconnect", () => {
    console.log("Đã mất kết nối với kênh SocketData  ID:",SocketData.id);
});

export function show_video_product(){
        let ws = new WebSocket("ws://127.0.0.1:8000/captureproduct/ws");
        video_product.style.display = "block";
        ws.binaryType = "arraybuffer";
        ws.onopen = () => {
                console.log("WebSocket connected");
        };
        ws.onclose = () => {
            console.log("WebSocket closed");
        };
        ws.onerror = (err) => {
                console.error("WebSocket error", err);
        };
        ws.onmessage = (event) => {
        const blob = new Blob([event.data], { type: "image/jpeg" });
        video_product.src = URL.createObjectURL(blob);
    };
}
    


export async function postData(url = "", data = {}) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  const text = await response.text();

  let json;
  try {
    json = JSON.parse(text);
  } catch {
    console.error("❌ Response không phải JSON:", text);
    return null;
  }

  if (!response.ok) {
    console.error("❌ HTTP error:", response.status, json);
    return null;
  }

  return json;
}

export async function fetchGet(url, timeout = 10000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Accept": "application/json"
            },
            signal: controller.signal
        });

        clearTimeout(timer);

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        return await response.json();

    } catch (error) {
        console.error("Fetch GET error:", error);
        return null;
    }
}


export async function fetchGetSendData(url, data = {}) {
    try {
        // Chuyển object data thành query string: {id:1,name:"A"} => ?id=1&name=A
        const queryString = new URLSearchParams(data).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;

        const response = await fetch(fullUrl, {
            method: "GET",
            headers: {
                "Accept": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Fetch GET error:", error);
        return null;
    }
}

export function clearn_div(div_card_arr) {
  if (!div_card_arr) return;
  for (let i = 0; i < div_card_arr.length; i++) {
    div_card_arr[i].classList.remove("div_click");
  }
}


export function removeClassFromList(elementList, className) {
    if (!elementList || !className) {
        console.log("class hoặc element không tồn tại")
        return;
    }
    for (let i = 0; i < elementList.length; i++) {
        elementList[i].classList.remove(className);
    }
}