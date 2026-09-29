import { ModelRectangle } from "../model/model_rectangle.js";
import { canvasManager, scroll_container, WIDTH_IMG_SHAPE } from "../common_value.js";
import {
    ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE,
    additional_events,
    boxContentForeignObject,
    COLOR_RECT_SHAPE_REGION_DETECT,
    create_obj_cross_item,
    get_obj_product,
    obj_region_foreign_object_canvas,
    panner_region_foreign_object,
    refesh_btn,
    selected,
    setNameEventActivate,
    write_log_append,
    write_log_clear,
} from "./common_value_tool.js";
import { RectangleDrawer } from "../canvas/rectangel_drawer_canvas.js";
import { ForeignObjectInspector } from "../services/foreign_object_item_inspector.js";
import { ItemsInspector } from "../services/items_inspector.js";
import { postData } from "../utills/api.js";

additional_events.set("foreign-object-tool", event_transition_items);

const logForeignObject = document.getElementById("log-foreign-object");
const btnExitForeignObject = document.getElementById("btn-exit-foreign-object");
const btnCreateModel = document.getElementById("btn-create-model-foreign-object");
const btnRuntimeImages = document.getElementById("btn-runtime-images-foreign-object");
const btnRunModel = document.getElementById("btn-judment-foreign-object");
const btnDetectObject = document.getElementById("btn-detect-object-foreign-object");
const btnDeleteModel = document.getElementById("btn-delete-model-foreign-object");
const loadingPanel = document.getElementById("loading");
const loadingStatus = document.getElementById("loading-status");
const loadingBar = document.getElementById("loading-bar");
const loadingPercent = document.getElementById("loading-percent");
const foreignObjectPanels = [
    boxContentForeignObject,
    document.getElementById("runtime-train-images-panel-foreign-object"),
    document.getElementById("patchcore-result-panel-foreign-object"),
];

/**
 * Chỉ hiển thị một panel Dị vật và ẩn hai panel còn lại.
 *
 * @param {HTMLElement|null} activePanel Panel cần hiển thị.
 * @returns {void}
 * @throws {Error} Không chủ động phát sinh lỗi.
 */
function activateForeignObjectPanel(activePanel) {
    foreignObjectPanels.forEach(panel => {
        if (panel) panel.hidden = panel !== activePanel;
    });
}

foreignObjectPanels.forEach(panel => {
    if (panel) panel.hidden = true;
});

/**
 * Cập nhật loading panel cho tiến trình train model Dị vật.
 *
 * @param {boolean} busy True khi đang train.
 * @param {number} percent Phần trăm tiến độ từ 0 đến 100.
 * @param {string} message Nội dung trạng thái cần hiển thị.
 * @returns {void}
 * @throws {Error} Không chủ động phát sinh lỗi.
 */
function setForeignObjectBusy(busy, percent = 0, message = "") {
    if (loadingPanel) loadingPanel.style.display = busy ? "flex" : "none";
    if (loadingBar) loadingBar.style.width = `${percent}%`;
    if (loadingPercent) loadingPercent.textContent = `${percent}%`;
    if (loadingStatus && message) loadingStatus.textContent = message;
}

/**
 * Chờ train PatchCore Dị vật hoàn thành bằng cách đọc trạng thái từ API.
 *
 * @returns {Promise<void>} Resolve khi model đã được tạo xong.
 * @throws {Error} Khi API báo lỗi hoặc train vượt quá thời gian chờ.
 */
async function waitForForeignObjectTraining() {
    setForeignObjectBusy(true, 10, "Đang tạo model PatchCore...");
    let percent = 10;
    const progressTimer = setInterval(() => {
        if (percent < 95) setForeignObjectBusy(true, ++percent, "Đang train model...");
    }, 300);
    try {
        for (let attempt = 0; attempt < 600; attempt++) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            const query = new URLSearchParams({
                product_id: selected.product_id,
                frame_id: selected.frame_id,
                item_id: selected.items_id,
            });
            const response = await fetch(`/law_regulation/foreign_object/train_status?${query}`);
            const status = await response.json();
            if (!response.ok || !status?.ok) {
                throw new Error(status?.message || "Không đọc được trạng thái train.");
            }
            if (status.data?.completed) {
                setForeignObjectBusy(false, 100, "Hoàn thành");
                return;
            }
        }
        throw new Error("Train model quá thời gian chờ.");
    } finally {
        clearInterval(progressTimer);
        setForeignObjectBusy(false);
    }
}

/**
 * Gửi ROI Dị vật đã chấp nhận tới API để tạo model PatchCore.
 *
 * @returns {Promise<void>} Resolve sau khi train hoàn thành hoặc xử lý lỗi.
 * @throws {Error} Lỗi API được ghi ra log và không phát sinh ra ngoài.
 */
async function createForeignObjectModel() {
    const inspector = getForeignObjectInspector();
    const rect = inspector?.getCropRoi();
    if (!rect || !rect.isValid()) {
        write_log_append(logForeignObject, "❌ Hãy vẽ và chấp nhận hình chữ nhật trước khi tạo model.");
        return;
    }
    if (selected.product_id < 0 || selected.frame_id < 0 || selected.items_id < 0) {
        write_log_append(logForeignObject, "❌ Chưa xác định được product, frame hoặc item.");
        return;
    }
    try {
        const response = await postData("/law_regulation/foreign_object/create_model", {
            product_id: selected.product_id,
            frame_id: selected.frame_id,
            item_id: selected.items_id,
            crop_roi: {
                xStart: rect.xStart,
                yStart: rect.yStart,
                xEnd: rect.xEnd,
                yEnd: rect.yEnd,
            },
            width_canvas: WIDTH_IMG_SHAPE,
            image_count: 16,
        });
        if (!response?.ok) throw new Error(response?.message || "Không thể bắt đầu tạo model.");
        write_log_append(logForeignObject, "✅ Đã đưa yêu cầu tạo model vào luồng train.");
        await waitForForeignObjectTraining();
        write_log_append(logForeignObject, "✅ Tạo model hoàn tất.");
    } catch (error) {
        setForeignObjectBusy(false);
        write_log_append(logForeignObject, `❌ ${error.message}`);
    }
}

/**
 * Tải và hiển thị các ảnh runtime/good của model Dị vật hiện tại.
 *
 * @returns {Promise<void>} Hoàn thành khi ảnh đã render hoặc log lỗi.
 * @throws {Error} Lỗi API được ghi ra log và không phát sinh ra ngoài.
 */
async function loadForeignObjectRuntimeImages() {
    if (selected.product_id < 0 || selected.frame_id < 0 || selected.items_id < 0) {
        write_log_append(logForeignObject, "❌ Chưa xác định được product, frame hoặc item.");
        return;
    }
    const panel = document.getElementById("runtime-train-images-panel-foreign-object");
    if (panel) {
        panel.innerHTML = "";
        activateForeignObjectPanel(panel);
    }
    const query = new URLSearchParams({
        product_id: selected.product_id,
        frame_id: selected.frame_id,
        item_id: selected.items_id,
    });
    try {
        const response = await fetch(`/law_regulation/foreign_object/runtime_images?${query}`);
        const payload = await response.json();
        if (!response.ok || !payload?.ok) {
            throw new Error(payload?.message || "Không lấy được ảnh runtime.");
        }
        renderForeignObjectRuntimeImages(payload.data?.images || []);
        if (!payload.data?.images?.length) {
            write_log_append(logForeignObject, "⚠️ Không có ảnh runtime trong runtime/good.");
        }
    } catch (error) {
        write_log_append(logForeignObject, `❌ ${error.message}`);
    }
}

/**
 * Render card ảnh runtime Dị vật, cho phép xem và xóa từng ảnh.
 *
 * @param {Array<{name: string, image: string}>} images Danh sách ảnh từ API.
 * @returns {void}
 * @throws {Error} Không chủ động phát sinh lỗi.
 */
function renderForeignObjectRuntimeImages(images) {
    const panel = document.getElementById("runtime-train-images-panel-foreign-object");
    if (!panel) return;
    panel.innerHTML = "";
    if (!Array.isArray(images) || images.length === 0) return;
    activateForeignObjectPanel(panel);
    const grid = document.createElement("div");
    grid.className = "runtime-train-images-grid";
    images.forEach(item => {
        const card = document.createElement("div");
        card.className = "runtime-train-image-card";
        const image = document.createElement("img");
        image.src = item.image;
        image.alt = item.name;
        image.addEventListener("click", () => {
            canvasManager.clearShapeCanvas();
            canvasManager.clearPreviewCanvas();
            showForeignObjectRuntimeImage(item.image);
        });
        const remove = document.createElement("button");
        remove.type = "button";
        remove.className = "runtime-train-image-delete";
        remove.textContent = "×";
        remove.addEventListener("click", event => {
            event.stopPropagation();
            deleteForeignObjectRuntimeImage(item.name, card);
        });
        card.append(image, remove);
        grid.appendChild(card);
    });
    panel.appendChild(grid);
}

/**
 * Hiển thị ảnh runtime Dị vật đã chọn lên canvas chính.
 *
 * @param {string} dataUrl Ảnh base64 từ API.
 * @returns {void}
 * @throws {Error} Không chủ động phát sinh lỗi.
 */
function showForeignObjectRuntimeImage(dataUrl) {
    const image = new Image();
    image.onload = () => canvasManager.drawImageContain(canvasManager.ctxImg, canvasManager.cImg, image);
    image.src = dataUrl;
}

/**
 * Xóa đúng một ảnh runtime Dị vật khỏi session hiện tại.
 *
 * @param {string} imageName Tên ảnh runtime cần xóa.
 * @param {HTMLElement} card Card ảnh tương ứng trên giao diện.
 * @returns {Promise<void>} Hoàn thành sau khi API xử lý.
 * @throws {Error} Lỗi API được ghi ra log và không phát sinh ra ngoài.
 */
async function deleteForeignObjectRuntimeImage(imageName, card) {
    try {
        const response = await fetch("/law_regulation/foreign_object/runtime_image", {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                product_id: selected.product_id,
                frame_id: selected.frame_id,
                item_id: selected.items_id,
                image_name: imageName,
            }),
        });
        const payload = await response.json();
        if (!response.ok || !payload?.ok) {
            throw new Error(payload?.message || "Không thể xóa ảnh runtime.");
        }
        card.remove();
        const panel = document.getElementById("runtime-train-images-panel-foreign-object");
        if (panel && !panel.querySelector(".runtime-train-image-card")) {
            write_log_append(logForeignObject, "⚠️ Không có ảnh runtime trong runtime/good.");
        }
        write_log_append(logForeignObject, `✅ Đã xóa ảnh runtime ${imageName}.`);
    } catch (error) {
        write_log_append(logForeignObject, `❌ ${error.message}`);
    }
}

/**
 * Kiểm tra model Dị vật đã tồn tại trước khi chạy hoặc xóa.
 *
 * @returns {Promise<boolean>} True khi model hoàn thành và sẵn sàng dùng.
 * @throws {Error} Lỗi API được ghi ra log và trả về false.
 */
async function hasForeignObjectModel() {
    if (selected.product_id < 0 || selected.frame_id < 0 || selected.items_id < 0) {
        write_log_append(logForeignObject, "❌ Chưa xác định được product, frame hoặc item.");
        return false;
    }
    try {
        const query = new URLSearchParams({
            product_id: selected.product_id,
            frame_id: selected.frame_id,
            item_id: selected.items_id,
        });
        const response = await fetch(`/law_regulation/foreign_object/train_status?${query}`);
        const payload = await response.json();
        if (!response.ok || !payload?.ok) {
            throw new Error(payload?.message || "Không đọc được trạng thái model Dị vật.");
        }
        if (!payload.data?.completed) {
            write_log_append(logForeignObject, "⚠️ Chưa tạo model Dị vật cho item này.");
            return false;
        }
        return true;
    } catch (error) {
        write_log_append(logForeignObject, `❌ ${error.message}`);
        return false;
    }
}

/**
 * Chạy inference PatchCore Dị vật và hiển thị kết quả.
 *
 * @returns {Promise<void>} Hoàn thành sau khi render kết quả hoặc ghi log lỗi.
 * @throws {Error} Lỗi API được ghi ra log và không phát sinh ra ngoài.
 */
async function runForeignObjectModel() {
    const inspector = getForeignObjectInspector();
    const rect = inspector?.getCropRoi();
    if (!rect || !rect.isValid()) {
        write_log_append(logForeignObject, "❌ Hãy vẽ và chấp nhận hình chữ nhật trước khi chạy model.");
        return;
    }
    if (!await hasForeignObjectModel()) return;
    write_log_append(logForeignObject, "⏳ Đang chạy model PatchCore...");
    try {
        const response = await postData("/law_regulation/foreign_object/run_model", {
            product_id: selected.product_id,
            frame_id: selected.frame_id,
            item_id: selected.items_id,
            crop_roi: {
                xStart: rect.xStart,
                yStart: rect.yStart,
                xEnd: rect.xEnd,
                yEnd: rect.yEnd,
            },
            width_canvas: WIDTH_IMG_SHAPE,
        });
        if (!response?.ok) throw new Error(response?.message || "Chạy model thất bại.");
        renderForeignObjectPatchCoreResult(response.data || {});
        write_log_append(logForeignObject, "✅ Đã chạy model PatchCore.");
    } catch (error) {
        write_log_append(logForeignObject, `❌ ${error.message}`);
    }
}

/**
 * Chạy YOLO trên từng vùng bất thường do PatchCore phát hiện.
 *
 * @returns {Promise<void>} Hoàn thành sau khi render kết quả hoặc ghi log lỗi.
 * @throws {Error} Lỗi API được ghi ra log và không phát sinh ra ngoài.
 */
async function runForeignObjectObjectModel() {
    const inspector = getForeignObjectInspector();
    const rect = inspector?.getCropRoi();
    if (!rect || !rect.isValid()) {
        write_log_append(logForeignObject, "❌ Hãy vẽ và chấp nhận hình chữ nhật trước khi chạy model.");
        return;
    }
    if (!await hasForeignObjectModel()) return;
    write_log_append(logForeignObject, "⏳ Đang phát hiện đối tượng trong vùng bất thường...");
    try {
        const response = await postData("/law_regulation/foreign_object/run_object_model", {
            product_id: selected.product_id,
            frame_id: selected.frame_id,
            item_id: selected.items_id,
            crop_roi: {
                xStart: rect.xStart,
                yStart: rect.yStart,
                xEnd: rect.xEnd,
                yEnd: rect.yEnd,
            },
            width_canvas: WIDTH_IMG_SHAPE,
        });
        if (!response?.ok) throw new Error(response?.message || "Chạy model phát hiện đối tượng thất bại.");
        renderForeignObjectObjectDetectionResult(response.data || {});
        write_log_append(logForeignObject, "✅ Đã phát hiện đối tượng trong vùng bất thường.");
    } catch (error) {
        write_log_append(logForeignObject, `❌ ${error.message}`);
    }
}

/**
 * Render một ảnh duy nhất có vùng bất thường PatchCore và object YOLO.
 *
 * @param {object} data Dữ liệu từ endpoint phát hiện đối tượng.
 * @returns {void}
 * @throws {Error} Không chủ động phát sinh lỗi.
 */
function renderForeignObjectObjectDetectionResult(data) {
    const panel = document.getElementById("patchcore-result-panel-foreign-object");
    if (!panel) return;
    activateForeignObjectPanel(panel);
    panel.innerHTML = "";

    const image = new Image();
    image.onload = () => {
        const canvas = document.createElement("canvas");
        canvas.width = image.naturalWidth;
        canvas.height = image.naturalHeight;
        const context = canvas.getContext("2d");
        context.drawImage(image, 0, 0);

        const patchcoreBoxes = Array.isArray(data.boxes) ? data.boxes : [];
        patchcoreBoxes.forEach((box, index) => {
            const x = Number(box.x || 0);
            const y = Number(box.y || 0);
            const width = Number(box.width || 0);
            const height = Number(box.height || 0);
            context.strokeStyle = "#1677ff";
            context.lineWidth = Math.max(2, canvas.width / 800);
            context.strokeRect(x, y, width, height);
            drawBoxLabel(context, `Vùng bất thường ${index + 1}`, x, y, "#1677ff");
        });

        const detections = Array.isArray(data.detections) ? data.detections : [];
        detections.forEach((detection, index) => {
            const bbox = detection?.bbox || {};
            const x1 = Number(bbox.x1 || 0);
            const y1 = Number(bbox.y1 || 0);
            const x2 = Number(bbox.x2 || 0);
            const y2 = Number(bbox.y2 || 0);
            context.strokeStyle = "#00a651";
            context.lineWidth = Math.max(2, canvas.width / 800);
            context.strokeRect(x1, y1, x2 - x1, y2 - y1);
            const className = detection.class_name || "Đối tượng";
            const confidence = Number(detection.confidence || 0) * 100;
            drawBoxLabel(
                context,
                `${index + 1}. ${className} (${confidence.toFixed(1)}%)`,
                x1,
                y1,
                "#00a651"
            );
        });

        const resultImage = document.createElement("img");
        resultImage.src = canvas.toDataURL("image/png");
        resultImage.alt = "Kết quả phát hiện vùng bất thường";
        resultImage.className = "patchcore-inference-image";
        panel.prepend(resultImage);
    };
    image.src = data.image || "";

    const table = document.createElement("table");
    table.className = "patchcore-inference-table";
    const patchcoreBoxes = Array.isArray(data.boxes) ? data.boxes : [];
    const detections = Array.isArray(data.detections) ? data.detections : [];
    const verdict = detections.length > 0
        ? "NG - Đã phát hiện đối tượng"
        : patchcoreBoxes.length > 0
            ? "NG - Có vùng bất thường, chưa nhận diện được đối tượng"
            : "OK - Không phát hiện bất thường";
    [
        ["Kết quả phán định", verdict],
        ["Điểm bất thường", Number(data.score || 0).toFixed(6)],
        ["Số vùng bất thường", patchcoreBoxes.length],
        ["Số đối tượng phát hiện", detections.length],
    ].forEach(([label, value]) => {
        const row = table.insertRow();
        row.insertCell().textContent = label;
        row.insertCell().textContent = value;
    });

    if (detections.length > 0) {
        const heading = table.insertRow();
        heading.insertCell().textContent = "Chi tiết đối tượng";
        heading.insertCell().textContent = "Tên / độ tin cậy / tọa độ";
        detections.forEach((detection, index) => {
            const bbox = detection?.bbox || {};
            const confidence = Number(detection.confidence || 0) * 100;
            const coordinates = [bbox.x1, bbox.y1, bbox.x2, bbox.y2]
                .map(value => Number(value || 0).toFixed(0))
                .join(", ");
            const row = table.insertRow();
            row.insertCell().textContent = `Đối tượng ${index + 1}`;
            row.insertCell().textContent = `${detection.class_name || "Không xác định"} | ${confidence.toFixed(1)}% | [${coordinates}]`;
        });
    }
    panel.appendChild(table);
}

/**
 * Vẽ nhãn cho bounding box trên ảnh kết quả.
 *
 * @param {CanvasRenderingContext2D} context Context của canvas kết quả.
 * @param {string} label Nội dung nhãn.
 * @param {number} x Tọa độ trái.
 * @param {number} y Tọa độ trên.
 * @param {string} color Màu box và nhãn.
 * @returns {void}
 */
function drawBoxLabel(context, label, x, y, color) {
    context.font = "bold 14px Arial";
    const textWidth = context.measureText(label).width;
    const textY = Math.max(18, y);
    context.fillStyle = color;
    context.fillRect(x, textY - 18, textWidth + 8, 20);
    context.fillStyle = "#ffffff";
    context.fillText(label, x + 4, textY - 4);
}

/**
 * Render ảnh và thông tin inference PatchCore Dị vật.
 *
 * @param {object} data Dữ liệu kết quả trả về từ API.
 * @returns {void}
 * @throws {Error} Không chủ động phát sinh lỗi.
 */
function renderForeignObjectPatchCoreResult(data) {
    const panel = document.getElementById("patchcore-result-panel-foreign-object");
    if (!panel) return;
    activateForeignObjectPanel(panel);
    panel.innerHTML = "";
    const image = document.createElement("img");
    image.src = data.image;
    image.alt = "Kết quả inference PatchCore Dị vật";
    image.className = "patchcore-inference-image";
    const table = document.createElement("table");
    table.className = "patchcore-inference-table";
    const rows = [
        ["Trạng thái", data.status || "UNKNOWN"],
        ["Anomaly score", Number(data.score || 0).toFixed(6)],
        ["Số bounding box", Array.isArray(data.boxes) ? data.boxes.length : 0],
        ["Bounding boxes", JSON.stringify(data.boxes || "Không tìm thấy bounding box")],
    ];
    rows.forEach(([label, value]) => {
        const row = table.insertRow();
        row.insertCell().textContent = label;
        row.insertCell().textContent = value;
    });
    panel.append(image, table);
}

/**
 * Mở panner xác nhận trước khi xóa model Dị vật.
 *
 * @returns {Promise<void>} Hoàn thành khi panner được mở hoặc ghi log lỗi.
 * @throws {Error} Không chủ động phát sinh lỗi.
 */
async function requestDeleteForeignObjectModel() {
    if (!await hasForeignObjectModel()) return;
    document.dispatchEvent(new CustomEvent("open-confirm-overlay", {
        detail: {
            message: "Bạn có chắc chắn muốn xóa toàn bộ dữ liệu của model Dị vật này?",
            confirmLabel: "Xóa",
            cancelLabel: "Hủy",
            onConfirm: deleteForeignObjectModel,
        },
    }));
}

/**
 * Xóa model Dị vật hiện tại, giữ nguyên ROI và cấu hình inspector.
 *
 * @returns {Promise<void>} Hoàn thành sau khi dọn các panel liên quan.
 * @throws {Error} Lỗi API được ghi ra log và không phát sinh ra ngoài.
 */
async function deleteForeignObjectModel() {
    try {
        const response = await fetch("/law_regulation/foreign_object/model", {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                product_id: selected.product_id,
                frame_id: selected.frame_id,
                item_id: selected.items_id,
            }),
        });
        const payload = await response.json();
        if (!response.ok || !payload?.ok) {
            throw new Error(payload?.message || "Không thể xóa model Dị vật.");
        }
        const runtimePanel = document.getElementById("runtime-train-images-panel-foreign-object");
        const resultPanel = document.getElementById("patchcore-result-panel-foreign-object");
        if (runtimePanel) {
            runtimePanel.innerHTML = "";
            runtimePanel.hidden = true;
        }
        if (resultPanel) {
            resultPanel.innerHTML = "";
            resultPanel.hidden = true;
        }
        canvasManager.clearPreviewCanvas();
        write_log_append(logForeignObject, "✅ Đã xóa model Dị vật và toàn bộ dữ liệu liên quan.");
    } catch (error) {
        write_log_append(logForeignObject, `❌ ${error.message}`);
    }
}

/** Lấy hoặc tạo inspector Dị vật tại item đang chọn. */
function getForeignObjectInspector() {
    return create_obj_cross_item(
        ItemsInspector.TYPE_FOREIGN_OBJECT,
        ForeignObjectInspector,
        "setForeignObjectItems"
    );
}

/** Hiển thị bảng cấu hình rectangle Dị vật. */
function createForeignObjectConfig(rectData = null) {
    const inspector = getForeignObjectInspector();
    activateForeignObjectPanel(boxContentForeignObject);
    const wrapper = document.createElement("div");
    wrapper.id = "foreign-object-wrapper";
    const table = document.createElement("table");
    table.className = "measure-weld-width-config-table";
    const fields = [
        { label: "Tên hình", type: "text", value: rectData?.name ?? "Dị vật" },
        { label: "Ngưỡng dị vật", type: "number", value: inspector.getThreshold() },
    ];
    fields.forEach((field, index) => {
        const row = document.createElement("tr");
        row.className = "config-row";
        const label = document.createElement("th");
        label.className = "config-label";
        label.textContent = field.label;
        const cell = document.createElement("td");
        cell.className = "config-value";
        const input = document.createElement("input");
        input.className = "config-input";
        input.id = `foreign-object-input-${index}`;
        input.type = field.type;
        input.value = field.value;
        if (field.type === "number") {
            input.min = "0";
            input.max = "1";
            input.step = "any";
        }
        cell.appendChild(input);
        row.append(label, cell);
        table.appendChild(row);
    });

    const saveRow = document.createElement("tr");
    saveRow.className = "config-row";
    const saveLabel = document.createElement("th");
    saveLabel.className = "config-label";
    saveLabel.textContent = "Lưu ảnh train";
    const saveCell = document.createElement("td");
    saveCell.className = "config-value";
    const controls = document.createElement("div");
    controls.className = "end-chipping-save-runtime-control";
    const enableRadio = document.createElement("input");
    enableRadio.type = "radio";
    enableRadio.name = "enable-save-foreign-object-images";
    const toggle = document.createElement("input");
    toggle.type = "checkbox";
    toggle.id = "save-runtime-images-foreign-object";
    toggle.className = "end-chipping-save-runtime-toggle";
    const switchLabel = document.createElement("label");
    switchLabel.className = "end-chipping-save-runtime-switch";
    switchLabel.htmlFor = toggle.id;
    switchLabel.title = "Bật để runtime lưu ảnh tại vị trí này làm dữ liệu train PatchCore cho lần tạo model sau.";
    enableRadio.checked = inspector.getSaveRuntimeImages();
    toggle.checked = enableRadio.checked;
    toggle.disabled = !enableRadio.checked;

    let isForeignRadioChecked = enableRadio.checked;
    enableRadio.addEventListener("mousedown", () => {
        isForeignRadioChecked = enableRadio.checked;
    });
    enableRadio.addEventListener("click", () => {
        if (isForeignRadioChecked) {
            enableRadio.checked = false;
            isForeignRadioChecked = false;
        } else {
            enableRadio.checked = true;
            isForeignRadioChecked = true;
        }
        toggle.disabled = !enableRadio.checked;
        toggle.checked = enableRadio.checked;
    });
    controls.append(enableRadio, toggle, switchLabel);
    saveCell.appendChild(controls);
    saveRow.append(saveLabel, saveCell);
    table.appendChild(saveRow);

    const actions = document.createElement("div");
    actions.className = "config-actions";
    const accept = document.createElement("button");
    accept.className = "btn btn-accept";
    accept.textContent = "Chấp nhận";
    accept.addEventListener("click", () => {
        const thresholdInput = document.getElementById("foreign-object-input-1");
        const threshold = Number(thresholdInput?.value);
        if (!Number.isFinite(threshold) || threshold < 0 || threshold > 1) {
            write_log_clear(logForeignObject, "❌ Ngưỡng dị vật phải là số trong khoảng từ 0 đến 1.");
            thresholdInput?.focus();
            return;
        }
        const rectangle = new ModelRectangle(
            0,
            document.getElementById("foreign-object-input-0")?.value || "Dị vật",
            rectData?.xStart, rectData?.yStart, rectData?.xEnd, rectData?.yEnd
        );
        const validation = rectangle.validate();
        if (!validation.isValid) {
            write_log_clear(logForeignObject, "❌ Dữ liệu rectangle không hợp lệ.");
            return;
        }
        inspector.setCropRoi(rectangle);
        inspector.setThreshold(threshold);
        inspector.setSaveRuntimeImages(enableRadio.checked && toggle.checked);
        boxContentForeignObject.innerHTML = "";
        obj_region_foreign_object_canvas.reset();
        obj_region_foreign_object_canvas.setCurrentRectangle(rectangle);
        inspector.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
        get_obj_product().highlightItems(scroll_container, ItemsInspector.TYPE_FOREIGN_OBJECT, "cropRoi");
        write_log_clear(logForeignObject, "✅ Dữ liệu hợp lệ.");
    });
    const clear = document.createElement("button");
    clear.className = "btn btn-clear";
    clear.textContent = "Xóa";
    clear.addEventListener("click", () => {
        document.getElementById("foreign-object-input-0").value = "";
        document.getElementById("foreign-object-input-1").value = "";
        enableRadio.checked = false;
        isForeignRadioChecked = false;
        toggle.checked = false;
        toggle.disabled = true;
    });
    actions.append(accept, clear);
    wrapper.append(table, actions);
    return wrapper;
}

/** Nạp item hiện tại và vẽ lại ROI Dị vật nếu đã tồn tại. */
export function event_transition_items() {
    boxContentForeignObject.innerHTML = "";
    obj_region_foreign_object_canvas.reset();
    canvasManager.clearShapeCanvas();
    const inspector = getForeignObjectInspector();
    const rectangle = inspector?.getCropRoi();
    if (rectangle) {
        obj_region_foreign_object_canvas.setCurrentRectangle(rectangle);
        inspector.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
    }
    get_obj_product().highlightItems(scroll_container, ItemsInspector.TYPE_FOREIGN_OBJECT, "cropRoi");
}

obj_region_foreign_object_canvas.on(
    RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT,
    rectangle => boxContentForeignObject.appendChild(createForeignObjectConfig(rectangle))
);
obj_region_foreign_object_canvas.on(
    RectangleDrawer.NAME_EVENT_WHEN_CLICK_RIGHT_RECT,
    coordinate => {
        const inspector = getForeignObjectInspector();
        if (!inspector?.isPointOnRoiBorder(coordinate.x, coordinate.y, ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE)) return;
        inspector.removeCropRoi();
        canvasManager.clearShapeCanvas();
        get_obj_product().highlightItems(scroll_container, ItemsInspector.TYPE_FOREIGN_OBJECT, "cropRoi");
    }
);
obj_region_foreign_object_canvas.on(
    RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT_HAVE_ALREADY,
    coordinate => {
        const inspector = getForeignObjectInspector();
        const rectangle = inspector?.getCropRoi();
        if (!rectangle || !inspector.isPointOnRoiBorder(coordinate.x, coordinate.y, ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE)) return;
        boxContentForeignObject.innerHTML = "";
        obj_region_foreign_object_canvas.have_return = true;
        boxContentForeignObject.appendChild(createForeignObjectConfig(rectangle));
    }
);

btnCreateModel?.addEventListener("click", createForeignObjectModel);
btnRuntimeImages?.addEventListener("click", loadForeignObjectRuntimeImages);
btnRunModel?.addEventListener("click", runForeignObjectModel);
btnDetectObject?.addEventListener("click", runForeignObjectObjectModel);
btnDeleteModel?.addEventListener("click", requestDeleteForeignObjectModel);
btnExitForeignObject?.addEventListener("click", () => {
    canvasManager.clearShapeCanvas();
    canvasManager.clearPreviewCanvas();
    canvasManager.setTool(null);
    boxContentForeignObject.innerHTML = "";
    panner_region_foreign_object.classList.remove("active");
    refesh_btn();
    get_obj_product().clearHighlight(scroll_container);
    setNameEventActivate(null);
});