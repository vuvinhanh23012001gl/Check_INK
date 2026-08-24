const comButton = document.getElementById("btn-open-com-config");
const comOverlay = document.getElementById("overlay_config_com");
const comClose = document.getElementById("com-close");
const comForm = document.getElementById("com-form");
const comPorts = document.getElementById("com-ports-list");
const comSelect = document.getElementById("com-select");
const baudSelect = document.getElementById("baud-select");
const comStatus = document.getElementById("infor-com-connect");
const comInfo = document.getElementById("show_info_list_cam");
const comEmptyState = document.getElementById("com-empty-state");

async function requestCom(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Không thể xử lý cấu hình COM");
    return data;
}

function renderComConfig(data) {
    const config = data.config || {};
    const configuredPort = config.port_name || config.device_port;
    comPorts.innerHTML = "";
    (data.ports || []).forEach((port) => {
        const item = document.createElement("li");
        item.textContent = `${port.device} - ${port.description || "Không có mô tả"}`;
        if (port.device === configuredPort) item.classList.add("is-selected");
        comPorts.appendChild(item);
    });
    comSelect.innerHTML = "";
    (data.ports || []).forEach((port) => {
        const option = document.createElement("option");
        option.value = port.device;
        option.textContent = `${port.device} - ${port.description || "Không có mô tả"}`;
        option.selected = port.device === configuredPort;
        comSelect.appendChild(option);
    });
    comInfo.textContent = `${(data.ports || []).length} cổng`;
    if (!data.ports?.length) {
        comEmptyState.hidden = false;
        comEmptyState.textContent = "Không tìm thấy cổng COM trên máy";
    } else {
        comEmptyState.hidden = true;
    }
    baudSelect.value = String(config.baudrate || 115200);
    comStatus.textContent = data.connected ? `Đang kết nối: ${configuredPort}` : "Chưa kết nối";
    comStatus.className = `com-status ${data.connected ? "is-connected" : ""}`;
}

async function openComOverlay() {
    comOverlay.classList.add("is-visible");
    comOverlay.setAttribute("aria-hidden", "false");
    comStatus.textContent = "Đang tải danh sách cổng COM...";
    try { renderComConfig(await requestCom("/com/config")); }
    catch (error) { comStatus.textContent = error.message; }
}

comButton?.addEventListener("click", openComOverlay);
comClose?.addEventListener("click", () => {
    comOverlay.classList.remove("is-visible");
    comOverlay.setAttribute("aria-hidden", "true");
});
comForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    comStatus.textContent = "Đang mở cổng COM...";
    try {
        const result = await requestCom("/com/config", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({port_name: comSelect.value, baudrate: Number(baudSelect.value)})
        });
        renderComConfig(result);
        const configuredPort = result.config.port_name || result.config.device_port;
        comStatus.textContent = result.success
            ? `Đã mở và lưu ${configuredPort}`
            : `${result.message || "Không thể mở cổng COM"} (${configuredPort})`;
        comStatus.className = `com-status ${result.success ? "is-connected" : "is-error"}`;
    } catch (error) {
        comStatus.textContent = `Mở cổng COM thất bại: ${error.message}`;
        comStatus.className = "com-status is-error";
    }
});