# ĐẶC TẢ YÊU CẦU KỸ THUẬT (URD / SRS)
**Tên module:** Tính toán thời gian đồng bộ chuyển động trục IAI và chụp ảnh chống nhòe (Stop-and-Shoot Vision & AI)  
**Phiên bản:** 1.0  
**Mục tiêu:** Xác định chính xác thời gian chờ ổn định cơ khí trước khi chụp ($T_{\text{settle}}$) và thời gian giữ trục đứng yên trong khi chụp ($T_{\text{hold}}$) để triệt tiêu 100% hiện tượng mờ nhòe (Motion Blur) trước khi đưa ảnh vào xử lý Computer Vision & AI, đồng thời tối ưu hóa Cycle Time.

---

## 1. Sơ đồ trình tự điều khiển chuẩn (Sequence Flow)

Quy trình tại mỗi điểm chụp $N$ bắt buộc tuân thủ đúng 4 bước tuần tự sau:

1. **Bước 1 (Di chuyển):** Phát lệnh cho trục IAI di chuyển đến vị trí chụp $N$. Chờ tín hiệu `PEND == ON` (và `BUSY == OFF`).
2. **Bước 2 (Chờ ổn định - $T_{\text{settle}}$):** Bắt đầu đếm Timer 1 với thời gian $T_{\text{settle}}$ để triệt tiêu toàn bộ dao động cơ khí dư của khung gá/camera.
3. **Bước 3 (Kích chụp & Giữ trục - $T_{\text{hold}}$):** Khi hết $T_{\text{settle}}$, phát xung `Trigger` chụp ảnh. Giữ trục IAI đứng yên tuyệt đối trong khoảng thời gian $T_{\text{hold}}$ (hoặc chờ tín hiệu phần cứng báo kết thúc phơi sáng).
4. **Bước 4 (Di chuyển điểm tiếp theo & Chạy AI song song):** Ngay khi kết thúc $T_{\text{hold}}$ (màn trập đã đóng), lập tức phát lệnh cho IAI di chuyển sang điểm $N+1$. Song song lúc trục đang chạy, dữ liệu ảnh được truyền về PC để chạy thuật toán Computer Vision + AI phán định `OK/NG`.

---

## 2. Thông số đầu vào cần thu thập (Input Parameters)

Để tính toán các bộ định thời (Timer), kỹ sư cần khai báo các thông số hệ thống sau:

| Ký hiệu | Tên thông số | Đơn vị | Giá trị mặc định / Gợi ý | Nguồn lấy thông số |
| :--- | :--- | :---: | :---: | :--- |
| $\text{FOV}$ | Chiều rộng vùng nhìn theo phương trục IAI | $\text{mm}$ | $50\text{ mm}$ | Thiết kế quang học |
| $N_{\text{px}}$ | Độ phân giải cảm biến theo phương chuyển động | $\text{pixels}$ | $2000\text{ px}$ | Datasheet Camera |
| $B_{\text{max}}$ | Độ nhòe tối đa cho phép trên ảnh | $\text{pixels}$ | $0.5\text{ px}$ (Chuẩn AI) | Yêu cầu bài toán Vision |
| $A_0$ | Biên độ sai số khi `PEND` bật (*Positioning Band*) | $\mu\text{m}$ | $10 - 100\ \mu\text{m}$ | Phần mềm IAI (PC-RCM) |
| $f_n$ | Tần số dao động riêng của hệ gá cơ khí | $\text{Hz}$ | $30 - 100\text{ Hz}$ | Đo thực nghiệm / Tra bảng |
| $\zeta$ | Hệ số tắt dần dao động cơ khí (*Damping Ratio*) | - | $0.05 - 0.10$ | Mặc định lấy $0.08$ cho gá kim loại |
| $T_{\text{exp}}$ | Thời gian phơi sáng của Camera (*Exposure Time*) | $\text{ms}$ | $0.1 - 10.0\text{ ms}$ | Cài đặt trên Camera SDK |
| $T_{\text{trig\_delay}}$ | Độ trễ từ lúc xuất lệnh Trigger đến lúc mở màn trập | $\text{ms}$ | $0.1\text{ ms}$ (I/O) hoặc $10\text{ ms}$ (SW) | Phụ thuộc kiểu Trigger |
| $T_{\text{safety}}$ | Thời gian dự phòng an toàn trước khi cho trục chạy | $\text{ms}$ | $2.0 - 5.0\text{ ms}$ | Cài đặt phần mềm |

---

## 3. Công thức tính toán chi tiết (Mathematical Specification)

### 3.1. Độ phân giải không gian ($R$) và Biên độ rung cho phép ($A_{\text{allow}}$)
* Kích thước thực tế của 1 điểm ảnh (pixel) quy đổi ra micromet:
  $$R = \frac{\text{FOV} \times 1000}{N_{\text{px}}} \quad (\mu\text{m/pixel})$$
* Biên độ dao động cơ khí tối đa cho phép để ảnh không bị nhòe quá $B_{\text{max}}$ (thường chọn $B_{\text{max}} = 0.5\text{ pixel}$):
  $$A_{\text{allow}} = B_{\text{max}} \times R = 0.5 \times R \quad (\mu\text{m})$$

---

### 3.2. Công thức 1: Tính thời gian chờ IAI ổn định trước khi Trigger ($T_{\text{settle}}$)
Sau khi tín hiệu `PEND` của IAI bật lên, trục và cơ cấu gá camera vẫn còn dao động tắt dần từ biên độ ban đầu $A_0$ xuống $A_{\text{allow}}$. Thời gian chờ $T_{\text{settle}}$ (tính bằng $\text{ms}$) được xác định theo công thức:

$$T_{\text{settle}} = \begin{cases} 
\frac{1000}{2 \pi \cdot f_n \cdot \zeta} \cdot \ln\left(\frac{A_0}{0.5 \times R}\right) & \text{nếu } A_0 > 0.5 \times R \\
5.0\text{ ms} & \text{nếu } A_0 \le 0.5 \times R 
\end{cases}$$

#### Bảng tham chiếu chọn nhanh $f_n$ và $T_{\text{settle}}$ (khi không có thiết bị đo rung):
| Kết cấu cơ khí thực tế | Tần số riêng $f_n$ ước tính | Khuyến nghị cài `Positioning Band` ($A_0$) trên IAI | Giá trị $T_{\text{settle}}$ cài đặt (với $R = 20\ \mu\text{m/px}$) |
| :--- | :---: | :---: | :---: |
| Gá thép nguyên khối, ngắn, Camera cố định | $80 - 120\text{ Hz}$ | $0.01\text{ mm}$ ($10\ \mu\text{m}$) | **$15\text{ ms} - 25\text{ ms}$** |
| Khung nhôm định hình tiêu chuẩn, IAI mang tải vừa | $45 - 60\text{ Hz}$ | $0.02\text{ mm}$ ($20\ \mu\text{m}$) | **$35\text{ ms} - 60\text{ ms}$** |
| Tay đòn vươn dài (Cantilever), tải nặng, dừng gấp | $25 - 40\text{ Hz}$ | $0.05\text{ mm}$ ($50\ \mu\text{m}$) | **$80\text{ ms} - 150\text{ ms}$** |

---

### 3.3. Công thức 2: Tính thời gian chờ chụp ảnh xong rồi mới di chuyển ($T_{\text{hold}}$)
Trục IAI **chỉ bắt buộc phải đứng yên trong suốt quá trình cảm biến mở màn trập phơi sáng ($T_{\text{exp}}$)**. Không cần chờ quá trình đọc ảnh (*Readout*), truyền ảnh (*Transfer*) và chạy AI (*Inference*).

Thời gian giữ trục đứng yên kể từ thời điểm phát lệnh Trigger:

$$T_{\text{hold}} = T_{\text{trig\_delay}} + T_{\text{exp}} + T_{\text{safety}} \quad (\text{ms})$$

* **Trường hợp 1 – Dùng Hardware Trigger (Đấu dây I/O trực tiếp):**
  * $T_{\text{trig\_delay}} \approx 0.1\text{ ms}$, $T_{\text{safety}} = 2.0\text{ ms}$
  * $$T_{\text{hold}} = T_{\text{exp}} + 2.1\text{ ms}$$
* **Trường hợp 2 – Dùng Software Trigger (Gửi lệnh qua cáp LAN GigE / USB3):**
  * Do hệ điều hành không thời gian thực có độ trễ truyền thông (Jitter), lấy $T_{\text{trig\_delay}} \approx 10.0\text{ ms}$, $T_{\text{safety}} = 5.0\text{ ms}$
  * $$T_{\text{hold}} = T_{\text{exp}} + 15.0\text{ ms}$$

---

### 3.4. Tổng thời gian dừng trục tại 1 điểm chụp ($T_{\text{total\_stop}}$)
Tổng thời gian trục IAI phải dừng lại tại mỗi tọa độ chụp là:
$$T_{\text{total\_stop}} = T_{\text{settle}} + T_{\text{hold}} \quad (\text{ms})$$

---

## 4. Yêu cầu kỹ thuật đối với Lập trình & Cấu hình phần cứng

### 4.1. Yêu cầu cấu hình trên bộ điều khiển IAI (Phần mềm PC-RCM)
1. **Thu nhỏ `Positioning Band` (In-position width):** Bắt buộc chỉnh cột `Positioning Band` tại các điểm chụp từ mặc định $0.10\text{ mm}$ xuống còn **$0.01\text{ mm} - 0.02\text{ mm}$** để cờ `PEND` chỉ bật khi trục đã thực sự tiến sát đích và giảm tốc hoàn toàn.
2. **Cài đặt giảm tốc êm (Deceleration / S-Curve):** Giảm thông số Deceleration tại điểm chụp (hoặc bật bộ lọc *Vibration Suppression*) để hạn chế quán tính giật khung máy khi phanh.

### 4.2. Yêu cầu lập trình đồng bộ Camera (Ưu tiên cơ chế Handshake thay cho Timer $T_{\text{hold}}$)
Để đạt độ tin cậy tuyệt đối (không bao giờ chạy sớm gây nhòe ảnh khi mạng bị trễ), phần mềm/PLC cần ưu tiên áp dụng cơ chế bắt sự kiện kết thúc phơi sáng thay vì dùng Timer $T_{\text{hold}}$ cố định:
* **Phương án A (Qua PLC I/O):** Cấu hình chân Output của Camera ở chế độ `ExposureActive`. Sau khi kích Trigger, PLC chờ **sườn xuống (Falling Edge)** của tín hiệu `ExposureActive` (báo hiệu màn trập đã đóng 100%) rồi lập tức cho IAI di chuyển sang điểm tiếp theo.
* **Phương án B (Qua PC SDK - GenICam/IDS/Basler):** Đăng ký callback bắt sự kiện `EventExposureEnd` từ Camera. Ngay khi nhận sự kiện `EventExposureEnd`, luồng điều khiển chuyển động (Motion Thread) cho phép IAI chạy tiếp ngay lập tức mà không cần đợi hàm `GrabFrame()` tải xong toàn bộ bức ảnh về RAM.

### 4.3. Yêu cầu kiểm tra độ nét trước khi đưa vào AI (Sharpness Gate)
* Tại luồng xử lý ảnh (Vision Thread), trước khi đẩy ảnh vào mô hình AI phán định `OK/NG`, phải tính chỉ số độ nét (ví dụ: phương sai Laplacian $\sigma^2_{\text{Laplacian}}$).
* Nếu $\sigma^2_{\text{Laplacian}} < \text{Threshold}_{\text{blur}}$, hệ thống phải ghi log cảnh báo rung cơ khí hoặc thực hiện chụp lại (Re-trigger) thay vì đưa ảnh nhòe vào AI gây phán định sai (False NG / Escape).

---

## 5. Ví dụ tính toán mẫu (Test Case chuẩn để nghiệm thu)

**Giả thiết bài toán:**
* Vùng nhìn $\text{FOV} = 40\text{ mm}$, độ phân giải Camera $N_{\text{px}} = 2000\text{ pixels}$ $\rightarrow R = 20\ \mu\text{m/pixel}$.
* Ngưỡng nhòe cho phép $B_{\text{max}} = 0.5\text{ pixel}$ $\rightarrow A_{\text{allow}} = 10\ \mu\text{m}$.
* Cài đặt `Positioning Band` trên IAI: $0.05\text{ mm}$ ($A_0 = 50\ \mu\text{m}$).
* Khung gá nhôm định hình có $f_n = 50\text{ Hz}$, $\zeta = 0.08$.
* Camera phơi sáng $T_{\text{exp}} = 2.0\text{ ms}$, kích chụp bằng Hardware Trigger ($T_{\text{trig\_delay}} = 0.1\text{ ms}$, $T_{\text{safety}} = 2.0\text{ ms}$).

**Kết quả cài đặt vào hệ thống:**
1. **Timer 1 - Chờ ổn định sau `PEND` ($T_{\text{settle}}$):**
   $$T_{\text{settle}} = \frac{1000}{2 \pi \times 50 \times 0.08} \cdot \ln\left(\frac{50}{10}\right) = 39.79 \times 1.609 \approx \mathbf{64.0\text{ ms}}$$
2. **Timer 2 - Chờ chụp xong trước khi chạy tiếp ($T_{\text{hold}}$):**
   $$T_{\text{hold}} = 0.1 + 2.0 + 2.0 = \mathbf{4.1\text{ ms}}$$
3. **Tổng thời gian dừng trục tại điểm chụp ($T_{\text{total\_stop}}$):**
   $$T_{\text{total\_stop}} = 64.0 + 4.1 = \mathbf{68.1\text{ ms}}$$