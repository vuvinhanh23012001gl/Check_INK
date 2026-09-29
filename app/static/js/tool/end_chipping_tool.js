console.log("Vào File End Chipping Tool");
import { ModelRectangle } from '../model/model_rectangle.js'; 
import {scroll_container,canvasManager,WIDTH_IMG_SHAPE}from "../common_value.js"
import {obj_region_end_chipping_canvas,boxContentEndChipping,get_obj_product,selected,checkSelected,
    additional_events,write_log_clear,write_log_append,COLOR_RECT_SHAPE_REGION_DETECT,create_obj_cross_item,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE,refesh_btn,setNameEventActivate,panner_region_end_chipping
} from "./common_value_tool.js"   
import {RectangleDrawer} from "../canvas/rectangel_drawer_canvas.js"
import {ItemsInspector} from "../services/items_inspector.js"
import {EndChippingInspector} from "../services/end_chipping_item_inspector.js"
import {postData} from "../utills/api.js";


additional_events.set("end-chipping-tool", event_transition_items);
const btn_judment_end_chipping = document.getElementById("btn-judment-end-chipping");
const btn_create_model_end_chipping = document.getElementById("btn-create-model-end-chipping");
const btn_runtime_images_end_chipping = document.getElementById("btn-runtime-images-end-chipping");
const btn_delete_model_end_chipping = document.getElementById("btn-delete-model-end-chipping");
const log_end_chipping = document.getElementById("log-end-chipping");
const btn_exit_end_chipping = document.getElementById("btn-exit-end-chipping");
const loadingPanel = document.getElementById("loading");
const loadingStatus = document.getElementById("loading-status");
const loadingBar = document.getElementById("loading-bar");
const loadingPercent = document.getElementById("loading-percent");
const endChippingPanels = [
    document.getElementById("table-cof-end-chipping"),
    document.getElementById("runtime-train-images-panel-end-chipping"),
    document.getElementById("patchcore-result-panel-end-chipping"),
];

function activateEndChippingPanel(activePanel) {
    endChippingPanels.forEach(panel => {
        if (panel) panel.hidden = panel !== activePanel;
    });
}

endChippingPanels.forEach(panel => {
    if (panel) panel.hidden = true;
});

btn_runtime_images_end_chipping?.addEventListener("click", async () => {
    if (selected.product_id < 0 || selected.frame_id < 0 || selected.items_id < 0) {
        write_log_append(log_end_chipping, "❌ Chưa xác định được product, frame hoặc item.");
        return;
    }
    const runtimeImagesPanel = document.getElementById("runtime-train-images-panel-end-chipping");
    if (runtimeImagesPanel) {
        runtimeImagesPanel.innerHTML = "";
        activateEndChippingPanel(runtimeImagesPanel);
    }
    const query = new URLSearchParams({
        product_id: selected.product_id,
        frame_id: selected.frame_id,
        item_id: selected.items_id,
    });
    try {
        const response = await fetch(`/law_regulation/end_chipping/runtime_images?${query}`);
        const payload = await response.json();
        if (!response.ok || !payload?.ok) {
            write_log_append(log_end_chipping, payload?.message || "Không lấy được ảnh runtime.");
            return;
        }
        renderRuntimeImages(payload.data?.images || []);
        if (!payload.data?.images?.length) {
            write_log_append(log_end_chipping, "⚠️ Không có ảnh runtime trong runtime/good.");
        }
    } catch (error) {
        write_log_append(log_end_chipping, `❌ ${error.message}`);
    }
});

btn_delete_model_end_chipping?.addEventListener("click", () => {
    if (selected.product_id < 0 || selected.frame_id < 0 || selected.items_id < 0) {
        write_log_append(log_end_chipping, "❌ Chưa xác định được product, frame hoặc item.");
        return;
    }
    document.dispatchEvent(new CustomEvent("open-confirm-overlay", {
        detail: {
            message: "Bạn có chắc chắn muốn xóa toàn bộ dữ liệu của model này?",
            confirmLabel: "Xóa",
            cancelLabel: "Hủy",
            onConfirm: deleteEndChippingModel,
        },
    }));
});

async function deleteEndChippingModel() {
    try {
        const response = await fetch("/law_regulation/end_chipping/model", {
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
            write_log_append(log_end_chipping, payload?.message || "❌ Không thể xóa model.");
            return;
        }
        clearEndChippingModelView();
        write_log_append(log_end_chipping, "✅ Đã xóa model và toàn bộ dữ liệu liên quan.");
    } catch (error) {
        write_log_append(log_end_chipping, `❌ ${error.message}`);
    }
}

function clearEndChippingModelView() {
    const runtimeImagesPanel = document.getElementById("runtime-train-images-panel-end-chipping");
    if (runtimeImagesPanel) {
        runtimeImagesPanel.innerHTML = "";
        runtimeImagesPanel.hidden = true;
    }
    clearPatchCoreResult();
    canvasManager.clearPreviewCanvas();
}

function renderRuntimeImages(images) {
    const panel = document.getElementById("runtime-train-images-panel-end-chipping");
    if (!panel) return;
    panel.innerHTML = "";
    if (!Array.isArray(images) || images.length === 0) {
        panel.hidden = true;
        return;
    }
    activateEndChippingPanel(panel);
    const grid = document.createElement("div");
    grid.className = "runtime-train-images-grid";
    images.forEach(item => {
        const card = document.createElement("div");
        card.className = "runtime-train-image-card";
        const image = document.createElement("img");
        image.src = item.image;
        image.alt = item.name;
        image.addEventListener("click", () => {
            activateEndChippingPanel(panel);
            canvasManager.clearShapeCanvas();
            canvasManager.clearPreviewCanvas();
            showRuntimeImageOnCanvas(item.image);
        });
        const remove = document.createElement("button");
        remove.type = "button";
        remove.className = "runtime-train-image-delete";
        remove.textContent = "×";
        remove.addEventListener("click", event => {
            event.stopPropagation();
            deleteRuntimeImage(item.name, card);
        });
        card.append(image, remove);
        grid.appendChild(card);
    });
    panel.appendChild(grid);
}

function showRuntimeImageOnCanvas(dataUrl) {
    const image = new Image();
    image.onload = () => canvasManager.drawImageContain(canvasManager.ctxImg, canvasManager.cImg, image);
    image.src = dataUrl;
}

async function deleteRuntimeImage(imageName, card) {
    const response = await fetch("/law_regulation/end_chipping/runtime_image", {
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
    if (response.ok && payload?.ok) {
        card.remove();
        const panel = document.getElementById("runtime-train-images-panel-end-chipping");
        if (panel && !panel.querySelector(".runtime-train-image-card")) {
            panel.hidden = true;
        }
        write_log_append(log_end_chipping, `✅ Đã xóa ảnh runtime ${imageName}.`);
    } else {
        write_log_append(log_end_chipping, payload?.message || "Không thể xóa ảnh runtime.");
    }
}

function setEndChippingBusy(busy) {
    const panel = document.getElementById("panner-region-end-chipping");
    if (panel) panel.style.pointerEvents = busy ? "none" : "";
    if (loadingPanel) loadingPanel.style.display = busy ? "flex" : "none";
}

function setEndChippingProgress(percent, message) {
    if (loadingBar) loadingBar.style.width = `${percent}%`;
    if (loadingPercent) loadingPercent.textContent = `${percent}%`;
    if (loadingStatus && message) loadingStatus.textContent = message;
}

async function waitForEndChippingTraining() {
    setEndChippingBusy(true);
    setEndChippingProgress(10, "Đang tạo model PatchCore...");
    let progress = 10;
    const progressTimer = setInterval(() => {
        if (progress < 95) {
            progress += 1;
            setEndChippingProgress(progress, "Đang train model...");
        }
    }, 300);

    try {
        for (let attempt = 0; attempt < 600; attempt++) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            const query = new URLSearchParams({
                product_id: selected.product_id,
                frame_id: selected.frame_id,
                item_id: selected.items_id,
            });
            const response = await fetch(`/law_regulation/end_chipping/train_status?${query}`, {
                headers: { "Accept": "application/json" },
            });
            const responseText = await response.text();
            let status;
            try {
                status = JSON.parse(responseText);
            } catch (error) {
                throw new Error(`API trạng thái trả dữ liệu không hợp lệ (HTTP ${response.status})`);
            }
            if (!response.ok || !status?.ok) {
                throw new Error(
                    status?.message ||
                    status?.error_name ||
                    `Không đọc được trạng thái train (HTTP ${response.status})`
                );
            }
            if (status.data?.completed) {
                setEndChippingProgress(100, "Hoàn thành");
                setEndChippingBusy(false);
                write_log_append(log_end_chipping, "✅ Train model đã hoàn thành.");
                return;
            }
        }
        throw new Error("Train model quá thời gian chờ");
    } finally {
        clearInterval(progressTimer);
    }
}

btn_create_model_end_chipping.addEventListener("click", async () => {
    const inspector = create_obj_cross_item(
        ItemsInspector.TYPE_END_CHIPPING,
        EndChippingInspector,
        "setEndChippingItems"
    );
    const rect = inspector?.getCropRoi();
    if (!rect || !rect.isValid()) {
        write_log_append(log_end_chipping, "❌ Hãy vẽ và chấp nhận hình chữ nhật trước khi tạo model.");
        return;
    }
    if (selected.product_id < 0 || selected.frame_id < 0 || selected.items_id < 0) {
        write_log_append(log_end_chipping, "❌ Chưa xác định được product, frame hoặc item.");
        return;
    }
    const response = await postData("/law_regulation/end_chipping/create_model", {
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
    if (response?.ok || response?.status === "ok") {
        write_log_append(log_end_chipping, "✅ Đã đưa yêu cầu tạo model vào luồng train.");
        try {
            await waitForEndChippingTraining();
            write_log_append(log_end_chipping, "✅ Tạo model hoàn tất.");
        } catch (error) {
            setEndChippingBusy(false);
            write_log_append(log_end_chipping, `❌ ${error.message}`);
        }
    } else {
        setEndChippingBusy(false);
        write_log_append(log_end_chipping, "❌ Không thể bắt đầu tạo model.");
    }
});

btn_judment_end_chipping.addEventListener("click", async () => {
    const inspector = create_obj_cross_item(
        ItemsInspector.TYPE_END_CHIPPING,
        EndChippingInspector,
        "setEndChippingItems"
    );
    const rect = inspector?.getCropRoi();
    if (!rect || !rect.isValid()) {
        write_log_append(log_end_chipping, "❌ Hãy vẽ và chấp nhận hình chữ nhật trước khi chạy model.");
        return;
    }
    if (selected.product_id < 0 || selected.frame_id < 0 || selected.items_id < 0) {
        write_log_append(log_end_chipping, "❌ Chưa xác định được product, frame hoặc item.");
        return;
    }
    write_log_append(log_end_chipping, "⏳ Đang chạy model PatchCore...");
    try {
        const response = await postData("/law_regulation/end_chipping/run_model", {
            product_id: selected.product_id,
            frame_id: selected.frame_id,
            item_id: selected.items_id,
            crop_roi: {
                xStart: rect.xStart,
                yStart: rect.yStart,
                xEnd: rect.xEnd,
                yEnd: rect.yEnd,
                threshold: inspector.getThreshold(),
            },
            width_canvas: WIDTH_IMG_SHAPE,
        });
        if (!response?.ok) {
            write_log_append(log_end_chipping, `❌ ${response?.message || "Chạy model thất bại."}`);
            return;
        }
        renderPatchCoreResult(response.data || {});
        write_log_append(log_end_chipping, "✅ Đã chạy model PatchCore.");
    } catch (error) {
        write_log_append(log_end_chipping, `❌ ${error.message}`);
    }
});

function renderPatchCoreResult(data) {
    const resultPanel = document.getElementById("patchcore-result-panel-end-chipping");
    if (!resultPanel) return;
    activateEndChippingPanel(resultPanel);
    resultPanel.innerHTML = "";

    const image = document.createElement("img");
    image.src = data.image;
    image.alt = "Kết quả inference PatchCore";
    image.className = "patchcore-inference-image";

    const table = document.createElement("table");
    table.className = "patchcore-inference-table";
    const rows = [
        ["Trạng thái", data.status || "UNKNOWN"],
        ["Anomaly score", Number(data.score || 0).toFixed(6)],
        ["Số bounding box", Array.isArray(data.boxes) ? data.boxes.length : 0],
        ["Bounding boxes", JSON.stringify(data.boxes ||"Không tìm thấy bounding box")],
    ];
    rows.forEach(([label, value]) => {
        const row = table.insertRow();
        row.insertCell().textContent = label;
        row.insertCell().textContent = value;
    });
    resultPanel.append(image, table);
}






obj_region_end_chipping_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT,func_callback_click_on_rect);
obj_region_end_chipping_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_RIGHT_RECT,func_callback_click_mouse_right_into_line);
obj_region_end_chipping_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT_HAVE_ALREADY,func_callback_click_on_line_have_aready);

function func_callback_click_on_rect(data_shape){
    console.log("click vào khung",data_shape);
    console.log("boxContentEndChipping",boxContentEndChipping);
    boxContentEndChipping.appendChild(createEndChipping(data_shape)); 
}

btn_exit_end_chipping.addEventListener("click",()=>{
    console.log("Bạn vừa nhấn vào thoát Frame");
    canvasManager.clearShapeCanvas();
    canvasManager.clearPreviewCanvas();
    canvasManager.setTool(null);//đặt canvas bằng null
    boxContentEndChipping.innerHTML = "";
    panner_region_end_chipping.classList.remove("active");
    refesh_btn();
    get_obj_product().clearHighlight(scroll_container);
    setNameEventActivate(null);
})


function func_callback_click_mouse_right_into_line(coordinate){
    let obj_end_chipping_inspector = create_obj_cross_item(ItemsInspector.TYPE_END_CHIPPING,EndChippingInspector,"setEndChippingItems");
    let result_find_line  = obj_end_chipping_inspector.isPointOnRoiBorder(coordinate.x,coordinate.y,ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE);
    if (result_find_line){
        console.log("Click trúng đường viền");
        clearPatchCoreResult();
        obj_end_chipping_inspector.removeCropRoi();
        canvasManager.clearShapeCanvas();
        obj_end_chipping_inspector.drawAll(canvasManager);
        get_obj_product().highlightItems(scroll_container, ItemsInspector.TYPE_END_CHIPPING, "cropRoi");  
    }
}

function func_callback_click_on_line_have_aready(coordinate) {
    const inspector = create_obj_cross_item(
        ItemsInspector.TYPE_END_CHIPPING,
        EndChippingInspector,
        "setEndChippingItems"
    );
    if (!inspector) return;
    const rect = inspector.getCropRoi();
    if (!rect || !inspector.isPointOnRoiBorder(
        coordinate.x,
        coordinate.y,
        ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE
    )) return;

    clearPatchCoreResult();
    boxContentEndChipping.innerHTML = "";
    obj_region_end_chipping_canvas.have_return = true;
    boxContentEndChipping.appendChild(createEndChipping({
        ...rect,
        thresholdNG: inspector.getThreshold(),
    }));
}

function clearPatchCoreResult() {
    const resultPanel = document.getElementById("patchcore-result-panel-end-chipping");
    if (resultPanel) resultPanel.innerHTML = "";
}




export function event_transition_items(){
    boxContentEndChipping.innerHTML = "";
    const runtimeImagesPanel = document.getElementById("runtime-train-images-panel-end-chipping");
    if (runtimeImagesPanel) {
        runtimeImagesPanel.innerHTML = "";
        runtimeImagesPanel.hidden = true;
    }
    clearPatchCoreResult();
    obj_region_end_chipping_canvas.reset();
    canvasManager.clearShapeCanvas();
    get_obj_product().highlightItems(scroll_container, ItemsInspector.TYPE_END_CHIPPING, "cropRoi");  
    let obj_end_chipping_inspector = create_obj_cross_item(ItemsInspector.TYPE_END_CHIPPING,EndChippingInspector,"setEndChippingItems");
    if (obj_end_chipping_inspector){
        const rect = obj_end_chipping_inspector.getCropRoi();
        if (rect) {
            obj_region_end_chipping_canvas.setCurrentRectangle(rect);
            obj_end_chipping_inspector.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
            boxContentEndChipping.innerHTML = "";
            boxContentEndChipping.appendChild(createEndChipping(rect));
            activateEndChippingPanel(boxContentEndChipping);
        }
        return;
    }
}




function createEndChipping(data_end_chipping = null) {
    let obj_end_chipping_inspector = create_obj_cross_item(ItemsInspector.TYPE_END_CHIPPING,EndChippingInspector,"setEndChippingItems");
    const runtimeImagesPanel = document.getElementById("runtime-train-images-panel-end-chipping");
    if (runtimeImagesPanel) runtimeImagesPanel.hidden = true;
    activateEndChippingPanel(boxContentEndChipping);
    const wrapper = document.createElement("div");
    wrapper.id = "measure-end-chipping-wrapper";

    const table = document.createElement("table");
    table.className = "measure-weld-width-config-table";
    table.id = "measure-end-chipping-table";
    const rows = [
        "Tên hình",
        "Ngưỡng mẻ ống"
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
        input.id = `measure-end-chipping-input-${index}`;
        
        if (index === 0) {
            input.type = "text";
            input.placeholder = "Nhập tên hình";
            if (data_end_chipping) {
                input.value = data_end_chipping.name ?? "Lỗi mẻ cạnh";
            }
        } else if (index === 1) {
            input.type = "number";
            input.placeholder = "Nhập ngưỡng NG";
            input.min = "0";
            input.max = "1";
            input.step = "any";
            console.log(" obj_end_chipping_inspector.threshold", obj_end_chipping_inspector.threshold);
            input.value = obj_end_chipping_inspector.threshold ?? 0;
        }

        td.appendChild(input);
        tr.appendChild(th);
        tr.appendChild(td);
        table.appendChild(tr);
    });

    const saveRuntimeImagesRow = document.createElement("tr");
    saveRuntimeImagesRow.className = "config-row";
    const saveRuntimeImagesLabel = document.createElement("th");
    saveRuntimeImagesLabel.className = "config-label";
    saveRuntimeImagesLabel.textContent = "Lưu ảnh train";
    const saveRuntimeImagesValue = document.createElement("td");
    saveRuntimeImagesValue.className = "config-value";
    const saveRuntimeImagesControl = document.createElement("div");
    saveRuntimeImagesControl.className = "end-chipping-save-runtime-control";
    const enableSaveRuntimeImages = document.createElement("input");
    enableSaveRuntimeImages.type = "radio";
    enableSaveRuntimeImages.name = "enable-save-runtime-images";
    enableSaveRuntimeImages.id = "enable-save-runtime-images";
    const saveRuntimeImagesToggle = document.createElement("input");
    saveRuntimeImagesToggle.type = "checkbox";
    saveRuntimeImagesToggle.id = "save-runtime-images-end-chipping";
    saveRuntimeImagesToggle.className = "end-chipping-save-runtime-toggle";
    const saveRuntimeImagesSwitch = document.createElement("label");
    saveRuntimeImagesSwitch.className = "end-chipping-save-runtime-switch";
    saveRuntimeImagesSwitch.htmlFor = saveRuntimeImagesToggle.id;
    saveRuntimeImagesSwitch.title = "Bật để runtime lưu ảnh tại vị trí này làm dữ liệu train PatchCore cho lần tạo model sau.";
    const savedRuntimeImages = obj_end_chipping_inspector.getSaveRuntimeImages();
    enableSaveRuntimeImages.checked = savedRuntimeImages;
    saveRuntimeImagesToggle.checked = savedRuntimeImages;
    saveRuntimeImagesToggle.disabled = !enableSaveRuntimeImages.checked;

    let isRadioChecked = enableSaveRuntimeImages.checked;
    enableSaveRuntimeImages.addEventListener("mousedown", () => {
        isRadioChecked = enableSaveRuntimeImages.checked;
    });
    enableSaveRuntimeImages.addEventListener("click", () => {
        if (isRadioChecked) {
            enableSaveRuntimeImages.checked = false;
            isRadioChecked = false;
        } else {
            enableSaveRuntimeImages.checked = true;
            isRadioChecked = true;
        }
        saveRuntimeImagesToggle.disabled = !enableSaveRuntimeImages.checked;
        saveRuntimeImagesToggle.checked = enableSaveRuntimeImages.checked;
    });
    saveRuntimeImagesControl.append(enableSaveRuntimeImages, saveRuntimeImagesToggle, saveRuntimeImagesSwitch);
    saveRuntimeImagesValue.appendChild(saveRuntimeImagesControl);
    saveRuntimeImagesRow.append(saveRuntimeImagesLabel, saveRuntimeImagesValue);
    table.appendChild(saveRuntimeImagesRow);

    // ===== Buttons =====
    const actions = document.createElement("div");
    actions.className = "config-actions";

    const btnAccept = document.createElement("button");
    btnAccept.className = "btn btn-accept";
    btnAccept.id = "btn-accept-end-chipping";
    btnAccept.textContent = "Chấp nhận";
    btnAccept.addEventListener("click", () => {
            const nameEndChipping = document.getElementById("measure-end-chipping-input-0")?.value || "";
            const thresholdInput = document.getElementById("measure-end-chipping-input-1");
            const thresholdNG = Number(thresholdInput?.value);
            if (!Number.isFinite(thresholdNG) || thresholdNG < 0 || thresholdNG > 1) {
                write_log_clear(log_end_chipping, "❌ Ngưỡng mẻ ống phải là số trong khoảng từ 0 đến 1.");
                thresholdInput?.focus();
                return;
            }
            const shouldSaveRuntimeImages = Boolean(
                document.getElementById("enable-save-runtime-images")?.checked &&
                document.getElementById("save-runtime-images-end-chipping")?.checked
            );
            const objEndChippingCropROI = new ModelRectangle(
                0,
                nameEndChipping,
                data_end_chipping?.xStart,
                data_end_chipping?.yStart,
                data_end_chipping?.xEnd,
                data_end_chipping?.yEnd
            );
            const resultValidate = objEndChippingCropROI.validate();
            if (resultValidate.isValid) {
                if (typeof boxContentEndChipping !== "undefined") {
                    boxContentEndChipping.innerHTML = "";
                }
                obj_end_chipping_inspector.setCropRoi(objEndChippingCropROI);
                obj_end_chipping_inspector.threshold = thresholdNG;
                obj_end_chipping_inspector.setSaveRuntimeImages(shouldSaveRuntimeImages);
                write_log_clear(log_end_chipping, "✅ Dữ liệu hợp lệ.");
                if (typeof obj_region_end_chipping_canvas !== "undefined") {
                    obj_region_end_chipping_canvas.is_available_one_line = false;
                    obj_region_end_chipping_canvas.reset();
                }
                canvasManager.clearShapeCanvas();
                obj_end_chipping_inspector.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
                get_obj_product().highlightItems(scroll_container, ItemsInspector.TYPE_END_CHIPPING, "cropRoi");  
            } else {
                let alertMessage = "❌ THÔNG BÁO LỖI DỮ LIỆU NHẬP VÀO:\n\n";
                write_log_clear(log_end_chipping, alertMessage);
                resultValidate.errors.forEach(err => {
                    write_log_append(log_end_chipping, `📍 ${err.rowName}`);
                    write_log_append(log_end_chipping, ` - Giá trị hiện tại: "${err.currentVal}"`);
                    write_log_append(log_end_chipping, ` - Yêu cầu: ${err.expected}`);
                });
            }
        });

    const btnClear = document.createElement("button");
    btnClear.className = "btn btn-clear";
    btnClear.id = "btn-clear-end-chipping";
    btnClear.textContent = "Xóa";

    btnClear.addEventListener("click", () => {
        const inpName = document.getElementById("measure-end-chipping-input-0");
        const inpThreshold = document.getElementById("measure-end-chipping-input-1");
        const enableSaveRuntimeImages = document.getElementById("enable-save-runtime-images");
        const saveRuntimeImagesToggle = document.getElementById("save-runtime-images-end-chipping");
        if (inpName) inpName.value = "";
        if (inpThreshold) inpThreshold.value = "";
        if (enableSaveRuntimeImages) {
            enableSaveRuntimeImages.checked = false;
            isRadioChecked = false;
        }
        if (saveRuntimeImagesToggle) {
            saveRuntimeImagesToggle.checked = false;
            saveRuntimeImagesToggle.disabled = true;
        }
    });

    actions.appendChild(btnAccept);
    actions.appendChild(btnClear);

    wrapper.appendChild(table);
    wrapper.appendChild(actions);

    return wrapper;
}

