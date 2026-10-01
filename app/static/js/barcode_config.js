// ==========================================
// BARCODE CONFIGURATION CONTROLLER
// Quản lý hiển thị và tương tác cấu hình Barcode
// ==========================================

const btnOpenBarcode = document.getElementById("btn-open-barcode-config");
const overlayBarcode = document.getElementById("overlay-barcode-config");
const btnCloseBarcode = document.getElementById("close-barcode-config");

const formAddBarcode = document.getElementById("form-add-barcode");
const barcodeStatusMsg = document.getElementById("barcode-status-msg");
const barcodeListBody = document.getElementById("barcode-list-body");

const inputOperator = document.getElementById("barcode-operator");
const inputFactory = document.getElementById("barcode-factory");
const inputLine = document.getElementById("barcode-line");
const selectRole = document.getElementById("barcode-role");
const inputCode = document.getElementById("barcode-code");

// Mở panel Cấu hình Barcode
if (btnOpenBarcode && overlayBarcode) {
    btnOpenBarcode.addEventListener("click", () => {
        console.log("Mở bảng Cấu hình Barcode");
        overlayBarcode.style.display = "flex";
        if (barcodeStatusMsg) {
            barcodeStatusMsg.innerText = "";
        }
        if (inputOperator) {
            inputOperator.focus();
        }
    });
}

// Đóng panel khi bấm nút X
if (btnCloseBarcode && overlayBarcode) {
    btnCloseBarcode.addEventListener("click", () => {
        console.log("Đóng bảng Cấu hình Barcode");
        overlayBarcode.style.display = "none";
    });
}

// Đóng panel khi click ra ngoài vùng backdrop
if (overlayBarcode) {
    overlayBarcode.addEventListener("click", (event) => {
        if (event.target === overlayBarcode) {
            overlayBarcode.style.display = "none";
        }
    });
}

// Xử lý tạo tài khoản Barcode trên giao diện
if (formAddBarcode) {
    formAddBarcode.addEventListener("submit", (event) => {
        event.preventDefault();

        const operator = inputOperator ? inputOperator.value.trim() : "";
        const factory = inputFactory ? inputFactory.value.trim() : "";
        const line = inputLine ? inputLine.value.trim() : "";
        const role = selectRole ? selectRole.value : "User";
        const code = inputCode ? inputCode.value.trim() : "";

        if (!operator || !factory || !line || !code) {
            if (barcodeStatusMsg) {
                barcodeStatusMsg.innerText = "⚠️ Vui lòng điền đầy đủ thông tin";
                barcodeStatusMsg.style.color = "#f87171";
            }
            return;
        }

        // Tạo dòng mới trong bảng
        if (barcodeListBody) {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${escapeHtml(operator)}</td>
                <td>${escapeHtml(factory)}</td>
                <td>${escapeHtml(line)}</td>
                <td><span style="padding: 2px 8px; border-radius: 4px; font-weight: bold; background: ${role === 'Manager' ? '#854d0e' : '#1e3a8a'}; color: ${role === 'Manager' ? '#fef08a' : '#bfdbfe'};">${escapeHtml(role)}</span></td>
                <td><code>${escapeHtml(code)}</code></td>
                <td><button type="button" class="btn_erase btn-delete-barcode">🗑️ Xóa</button></td>
            `;

            // Xử lý xóa dòng
            const deleteBtn = tr.querySelector(".btn-delete-barcode");
            if (deleteBtn) {
                deleteBtn.addEventListener("click", () => {
                    tr.remove();
                });
            }

            barcodeListBody.appendChild(tr);
        }

        if (barcodeStatusMsg) {
            barcodeStatusMsg.innerText = "✅ Tạo tài khoản thành công!";
            barcodeStatusMsg.style.color = "#22c55e";
        }

        // Xóa trắng input mã barcode và tên để nhập tiếp
        if (inputOperator) inputOperator.value = "";
        if (inputCode) inputCode.value = "";
        if (inputOperator) inputOperator.focus();
    });
}

// Bắt sự kiện xóa cho các dòng mẫu có sẵn
if (barcodeListBody) {
    const initialDeleteButtons = barcodeListBody.querySelectorAll(".btn-delete-barcode, .btn_erase");
    initialDeleteButtons.forEach((btn) => {
        btn.addEventListener("click", (e) => {
            const row = e.target.closest("tr");
            if (row) {
                row.remove();
            }
        });
    });
}

// Hàm chống XSS cho dữ liệu hiển thị trên bảng
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}
