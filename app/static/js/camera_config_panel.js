import { openOptionPanel } from "./panel_manager.js";
import { active_sceen_show_video, show_video_product } from "./common_value.js";

const cameraConfigButton = document.getElementById("btn-open-camera-config");
const cameraConfigPanel = document.getElementById("paner-camera-config");
const cameraConfigLog = document.getElementById("camera-config-log");
const balanceAuto = document.getElementById("camera-balance-auto");
const balanceInputs = [
    document.getElementById("camera-balance-red"),
    document.getElementById("camera-balance-green"),
    document.getElementById("camera-balance-blue")
];
const cameraConfigFields = [
    "acquisition_frame_rate", "exposure_time", "gain", "gamma",
    "black_level", "exposure_auto", "trigger_mode", "trigger_selector"
];

function renderCameraConfig(config) {
    cameraConfigFields.forEach((field) => {
        const input = document.querySelector(`#paner-camera-config [name="${field}"]`);
        if (input && config[field] !== undefined) input.value = config[field];
    });
    const whiteBalanceFields = {
        balance_ratio_red: document.getElementById("camera-balance-red"),
        balance_ratio_green: document.getElementById("camera-balance-green"),
        balance_ratio_blue: document.getElementById("camera-balance-blue")
    };
    Object.entries(whiteBalanceFields).forEach(([field, input]) => {
        if (input && config[field] !== undefined) input.value = config[field];
    });
    if (balanceAuto && config.balance_white_auto !== undefined) {
        const isAuto = String(config.balance_white_auto).toLowerCase() !== "off";
        balanceAuto.setAttribute("aria-pressed", String(isAuto));
    }
    updateWhiteBalanceState();
}

function readCameraConfigValues() {
    return Object.fromEntries(cameraConfigFields.map((field) => {
        const input = document.querySelector(`#paner-camera-config [name="${field}"]`);
        return [field, input.type === "number" ? Number(input.value) : input.value];
    }));
}

async function requestCameraConfig(url, method = "GET", values) {
    console.log(`[CameraConfig] Gửi request ${method} ${url}`, values || "");
    const response = await fetch(url, {
        method,
        headers: values ? {"Content-Type": "application/json"} : {},
        body: values ? JSON.stringify(values) : undefined
    });
    console.log(`[CameraConfig] Backend response ${response.status} ${response.statusText}`);
    const result = await response.json();
    console.log("[CameraConfig] Dữ liệu backend trả về:", result);
    if (!response.ok) throw new Error(result.detail || "Không thể xử lý cấu hình camera");
    return result;
}

function showCameraApplyResult(result, successMessage) {
    const applyResult = result?.apply_result;
    if (!cameraConfigLog) return;
    const featureSaveResult = result?.feature_save_result;
    if (applyResult?.applied && (!featureSaveResult || featureSaveResult.saved)) {
        cameraConfigLog.textContent = `${successMessage} - Đã gửi thành công tới camera`;
        return;
    }
    const errors = applyResult?.errors?.join(" | ") || featureSaveResult?.error || "Không nhận được xác nhận từ camera";
    cameraConfigLog.textContent = `Gửi hoặc lưu features.cfg thất bại: ${errors}`;
}

function updateWhiteBalanceState() {
    const isAuto = balanceAuto?.getAttribute("aria-pressed") === "true";
    balanceInputs.forEach((input) => { input.disabled = !isAuto; });
    const state = document.querySelector(".camera-auto-toggle-state");
    if (state) state.textContent = isAuto ? "On" : "Off";
    balanceAuto?.classList.toggle("is-on", isAuto);
}

function openCameraConfigPanel() {
    if (!cameraConfigPanel) return;
    console.log("[CameraConfig] Đã nhấn Cấu hình camera");
    openOptionPanel(cameraConfigPanel);
    updateWhiteBalanceState();
    if (cameraConfigLog) cameraConfigLog.textContent = "Đang mở cấu hình camera...";
    requestCameraConfig("/camera/config")
        .then((result) => {
            console.log("[CameraConfig] Cấu hình camera nhận được khi mở panel:", result);
            renderCameraConfig(result);
        })
        .catch((error) => {
            console.error("[CameraConfig] Lỗi nhận cấu hình từ backend:", error);
            if (cameraConfigLog) cameraConfigLog.textContent = error.message;
        });
}

if (cameraConfigButton && cameraConfigPanel) {
    balanceAuto?.addEventListener("click", () => {
        const isAuto = balanceAuto.getAttribute("aria-pressed") === "true";
        balanceAuto.setAttribute("aria-pressed", String(!isAuto));
        updateWhiteBalanceState();
    });
    document.getElementById("camera-config-stream")?.addEventListener("click", () => {
        active_sceen_show_video();
        show_video_product();
        if (cameraConfigLog) cameraConfigLog.textContent = "Đã mở Stream video camera";
    });
    document.getElementById("camera-config-accept")?.addEventListener("click", () => {
        requestCameraConfig("/camera/config/apply", "POST", readCameraConfigValues())
            .then((result) => {
                renderCameraConfig(result.config);
                showCameraApplyResult(result, "Đã Accept và áp dụng cấu hình camera");
            }).catch((error) => { if (cameraConfigLog) cameraConfigLog.textContent = error.message; });
    });
    document.getElementById("camera-config-save")?.addEventListener("click", () => {
        requestCameraConfig("/camera/config/save", "POST", readCameraConfigValues())
            .then((result) => {
                renderCameraConfig(result.config);
                showCameraApplyResult(result, "Đã Save cấu hình camera");
            }).catch((error) => { if (cameraConfigLog) cameraConfigLog.textContent = error.message; });
    });
    document.getElementById("camera-config-cancel")?.addEventListener("click", async () => {
        if (cameraConfigLog) cameraConfigLog.textContent = "Đang gửi yêu cầu thoát...";
        try {
            const result = await requestCameraConfig("/camera/exit");
            console.log("[CameraConfig] Backend xác nhận thoát:", result);
            if (result.redirect_url) window.location.href = result.redirect_url;
        } catch (error) {
            console.error("[CameraConfig] Lỗi thoát cấu hình camera:", error);
            if (cameraConfigLog) cameraConfigLog.textContent = `Thoát thất bại: ${error.message}`;
        }
    });
}

document.addEventListener("click", (event) => {
    if (event.target.closest("#btn-open-camera-config")) openCameraConfigPanel();
});