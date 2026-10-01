import { ModelRectangle } from "../model/model_rectangle.js";
import { canvasManager, scroll_container, WIDTH_IMG_SHAPE } from "../common_value.js";
import { RectangleDrawer } from "../canvas/rectangel_drawer_canvas.js";
import { AirBubblesItemInspector } from "../services/air_bubbles_item_inspector.js";
import { ItemsInspector } from "../services/items_inspector.js";
import { postData, fetchGet } from "../utills/api.js";
import {
    ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE,
    COLOR_RECT_SHAPE_REGION_DETECT,
    additional_events,
    boxContentAirBubbles,
    create_obj_cross_item,
    get_obj_product,
    obj_region_air_bubbles_canvas,
    panner_region_air_bubbles,
    refesh_btn,
    selected,
    setNameEventActivate,
    write_log_clear,
} from "./common_value_tool.js";

const EVENT_NAME = "air-bubbles-tool";
const logAirBubbles = document.getElementById("log-air-bubbles");
const closeButton = document.getElementById("btn-exit-air-bubbles");
const clearButton = document.getElementById("btn-clear-air-bubbles");
const judgmentButton = document.getElementById("btn-judment-air-bubbles");
const identifyWeldSeamButton = document.getElementById("btn-identify-weld-seam");
const deleteWeldSeamButton = document.getElementById("btn-delete-weld-seam");

additional_events.set(EVENT_NAME, event_transition_items);
obj_region_air_bubbles_canvas.on(
    RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT,
    openRectangleEditor,
);
obj_region_air_bubbles_canvas.on(
    RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT_HAVE_ALREADY,
    selectStoredRectangle,
);
obj_region_air_bubbles_canvas.on(
    RectangleDrawer.NAME_EVENT_WHEN_CLICK_RIGHT_RECT,
    removeStoredRectangle,
);

function getInspector() {
    return create_obj_cross_item(
        ItemsInspector.TYPE_AIR_BUBBLES,
        AirBubblesItemInspector,
        "setAirBubblesItems",
    );
}

function selectStoredRectangle(coordinate) {
    const inspector = getInspector();
    const rectangle = inspector?.findRectangleOnBorder(
        coordinate.x,
        coordinate.y,
        ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE,
    );
    if (!rectangle) return;
    obj_region_air_bubbles_canvas.have_return = true;
    openRectangleEditor(rectangle);
}

function removeStoredRectangle(coordinate) {
    const inspector = getInspector();
    const rectangle = inspector?.findRectangleOnBorder(
        coordinate.x,
        coordinate.y,
        ACTIVATION_DISTANCE_WHEN_CLICKING_THE_SQUARE,
    );
    if (!rectangle) return;
    inspector.removeRectangle(rectangle.id);
    boxContentAirBubbles.innerHTML = "";
    obj_region_air_bubbles_canvas.reset();
    inspector.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
    updateHighlight();
    write_log_clear(logAirBubbles, `Đã xóa vùng ${rectangle.name}.`);
}

function openRectangleEditor(rectangle) {
    if (!rectangle || rectangle.xStart < 0) return;
    const inspector = getInspector();
    boxContentAirBubbles.innerHTML = "";
    const wrapper = document.createElement("div");
    wrapper.className = "air-bubbles-editor";

    const label = document.createElement("label");
    label.textContent = "Tên vùng kiểm tra";
    label.htmlFor = "air-bubbles-name";
    const input = document.createElement("input");
    input.id = "air-bubbles-name";
    input.className = "config-input";
    input.value = rectangle.name || `Bọt khí ${inspector.getNextId() + 1}`;

    const actions = document.createElement("div");
    actions.className = "config-actions";
    const acceptButton = document.createElement("button");
    acceptButton.type = "button";
    acceptButton.className = "btn btn-accept";
    acceptButton.textContent = "Chấp nhận";
    acceptButton.addEventListener("click", () => {
        const name = input.value.trim();
        if (!name) {
            write_log_clear(logAirBubbles, "Tên vùng không được để trống.");
            return;
        }
        const id = Number.isInteger(rectangle.id) && rectangle.id >= 0
            ? rectangle.id
            : inspector.getNextId();
        const model = new ModelRectangle(
            id,
            name,
            rectangle.xStart,
            rectangle.yStart,
            rectangle.xEnd,
            rectangle.yEnd,
        );
        if (!model.isValid() || !inspector.addRectangle(model)) {
            write_log_clear(logAirBubbles, "Dữ liệu hình chữ nhật không hợp lệ.");
            return;
        }
        boxContentAirBubbles.innerHTML = "";
        obj_region_air_bubbles_canvas.reset();
        inspector.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
        updateHighlight();
        write_log_clear(
            logAirBubbles,
            `Đã lưu ${name}. Có thể tiếp tục vẽ vùng mới.`,
        );
    });
    const clearInputButton = document.createElement("button");
    clearInputButton.type = "button";
    clearInputButton.className = "btn btn-clear";
    clearInputButton.textContent = "Xóa";
    clearInputButton.addEventListener("click", () => {
        input.value = "";
    });
    actions.appendChild(acceptButton);
    actions.appendChild(clearInputButton);
    wrapper.append(label, input, actions);
    boxContentAirBubbles.appendChild(wrapper);
}

function updateHighlight() {
    get_obj_product()?.highlightItems(
        scroll_container,
        ItemsInspector.TYPE_AIR_BUBBLES,
        "rectangles",
    );
}

/**
 * Hiển thị bảng kết quả phán định OK/NG bọt khí trong vùng cof-and-inf-tool-content.
 * @param {object} data Kết quả trả về từ API /air_bubbles/run_model
 */
export function renderAirBubblesResultTable(data = {}) {
    boxContentAirBubbles.innerHTML = "";

    const wrapper = document.createElement("div");
    wrapper.className = "air-bubbles-result-panel";
    wrapper.style.padding = "10px";
    wrapper.style.display = "flex";
    wrapper.style.flexDirection = "column";
    wrapper.style.gap = "10px";

    const detectionOnly = data.status === "DETECT_ONLY" || data.has_weld_reference === false;
    const isOk = data.is_ok === true;
    const statusColor = detectionOnly ? "#1565c0" : isOk ? "#00c853" : "#d50000";
    const statusBg = detectionOnly ? "#e3f2fd" : isOk ? "#e8f5e9" : "#ffebee";

    // 1. Badge kết quả tổng quan
    const badge = document.createElement("div");
    badge.className = "air-bubbles-status-badge";
    badge.style.display = "flex";
    badge.style.alignItems = "center";
    badge.style.justifyContent = "space-between";
    badge.style.padding = "8px 14px";
    badge.style.borderRadius = "8px";
    badge.style.fontWeight = "bold";
    badge.style.fontSize = "13px";
    badge.style.backgroundColor = statusBg;
    badge.style.color = statusColor;
    badge.style.border = `1.5px solid ${statusColor}`;

    const badgeTitle = document.createElement("span");
    badgeTitle.textContent = detectionOnly
        ? "◉ CHỈ PHÁT HIỆN"
        : isOk ? "✓ KẾT QUẢ: OK" : "✗ KẾT QUẢ: NG";
    const badgeSub = document.createElement("span");
    badgeSub.style.fontSize = "12px";
    badgeSub.textContent = data.message || (isOk ? "Không phát hiện bọt khí" : "Phát hiện bọt khí");
    badge.append(badgeTitle, badgeSub);
    wrapper.appendChild(badge);

    // 2. Bảng tóm tắt số liệu
    const summaryTable = document.createElement("table");
    summaryTable.className = "patchcore-inference-table";
    summaryTable.style.width = "100%";
    summaryTable.style.fontSize = "12px";

    const objects = data.objects || [];
    const insideCount = detectionOnly
        ? null
        : data.inside_weld_count ?? objects.filter(o => o.is_inside_weld).length;
    const outsideCount = detectionOnly
        ? null
        : data.outside_weld_count ?? (objects.length - insideCount);
    const weldStatus = data.has_weld_reference
        ? "✓ Đã xác định đường hàn"
        : "⚠️ Chưa có tham chiếu đường hàn";

    const summaryRows = [
        ["Đường hàn", weldStatus],
        ["Tổng bọt khí", `${objects.length} đối tượng`],
        ["Trong đường hàn", detectionOnly ? "Chưa đánh giá" : `${insideCount} (Quy định: 0)`],
        ["Ngoài đường hàn", detectionOnly ? "Chưa đánh giá" : `${outsideCount} (Quy định: 0)`],
    ];

    summaryRows.forEach(([label, value], idx) => {
        const row = summaryTable.insertRow();
        const cellLabel = row.insertCell();
        cellLabel.textContent = label;
        cellLabel.style.fontWeight = "600";
        cellLabel.style.width = "40%";
        cellLabel.style.padding = "6px 10px";

        const cellVal = row.insertCell();
        cellVal.textContent = value;
        cellVal.style.padding = "6px 10px";

        if (idx === 2 && insideCount > 0) {
            cellVal.style.color = "#d50000";
            cellVal.style.fontWeight = "bold";
        } else if (idx === 3 && outsideCount > 0) {
            cellVal.style.color = "#e65100";
            cellVal.style.fontWeight = "bold";
        }
    });
    wrapper.appendChild(summaryTable);

    // 3. Bảng chi tiết từng bọt khí (nếu có)
    if (objects.length > 0) {
        const detailTitle = document.createElement("div");
        detailTitle.style.fontWeight = "bold";
        detailTitle.style.fontSize = "12px";
        detailTitle.style.color = "#37474f";
        detailTitle.textContent = "Danh sách bọt khí phát hiện:";
        wrapper.appendChild(detailTitle);

        const detailTable = document.createElement("table");
        detailTable.className = "patchcore-inference-table";
        detailTable.style.width = "100%";
        detailTable.style.fontSize = "11px";

        const thead = detailTable.createTHead();
        const headerRow = thead.insertRow();
        const headers = ["#", "Tọa độ (X, Y)", "Tin cậy", "Vị trí", "Đánh giá"];
        headers.forEach(h => {
            const th = document.createElement("th");
            th.textContent = h;
            th.style.padding = "6px 8px";
            th.style.background = "#eceff1";
            th.style.textAlign = "left";
            headerRow.appendChild(th);
        });

        const tbody = detailTable.createTBody();
        objects.forEach((obj, idx) => {
            const row = tbody.insertRow();
            const bbox = obj.bbox || {};
            const cx = Math.round((bbox.x1 + bbox.x2) / 2) || obj.center?.[0] || "-";
            const cy = Math.round((bbox.y1 + bbox.y2) / 2) || obj.center?.[1] || "-";
            const conf = ((obj.confidence || 0) * 100).toFixed(1) + "%";
            const isInside = obj.is_inside_weld === true;
            const locText = detectionOnly
                ? "Chưa đánh giá"
                : obj.location_text || (isInside ? "Trong đường hàn" : "Ngoài đường hàn");

            row.insertCell().textContent = idx + 1;
            row.insertCell().textContent = `(${cx}, ${cy})`;
            row.insertCell().textContent = conf;

            const locCell = row.insertCell();
            locCell.textContent = locText;
            locCell.style.fontWeight = "bold";
            locCell.style.color = detectionOnly
                ? "#1565c0"
                : isInside ? "#d50000" : "#ef6c00";

            const evalCell = row.insertCell();
            evalCell.textContent = detectionOnly ? "Chưa đánh giá" : "NG";
            evalCell.style.fontWeight = "bold";
            evalCell.style.color = detectionOnly ? "#1565c0" : "#d50000";
        });
        wrapper.appendChild(detailTable);
    }

    boxContentAirBubbles.appendChild(wrapper);
}

/**
 * Hiển thị bảng thông tin tham chiếu đường hàn đã nhận diện.
 * @param {object} weldData Dữ liệu polygon, skeleton và kích thước ảnh
 */
export function renderWeldSeamInfoTable(weldData) {
    boxContentAirBubbles.innerHTML = "";

    const wrapper = document.createElement("div");
    wrapper.style.padding = "10px";
    wrapper.style.display = "flex";
    wrapper.style.flexDirection = "column";
    wrapper.style.gap = "10px";

    const badge = document.createElement("div");
    badge.style.display = "flex";
    badge.style.alignItems = "center";
    badge.style.justifyContent = "space-between";
    badge.style.padding = "8px 12px";
    badge.style.borderRadius = "8px";
    badge.style.fontWeight = "bold";
    badge.style.fontSize = "13px";
    badge.style.backgroundColor = "#e8f5e9";
    badge.style.color = "#2e7d32";
    badge.style.border = "1.5px solid #4caf50";
    badge.textContent = "✓ Đã xác định đường hàn thành công";
    wrapper.appendChild(badge);

    const table = document.createElement("table");
    table.className = "patchcore-inference-table";
    table.style.width = "100%";
    table.style.fontSize = "12px";

    const skelCount = weldData?.skeleton?.length || 0;
    const polyCount = weldData?.polygon?.length || 0;

    const rows = [
        ["Trạng thái", "Đã phân tích (RAM preview)"],
        ["Viền đa giác", `${polyCount} contour (Xanh lá)`],
        ["Điểm tâm skeleton", `${skelCount} điểm (Vàng)`],
        ["Kích thước ảnh", `${weldData?.width || 0} x ${weldData?.height || 0} px`],
        ["Lưu trữ", "Nhấn 'Lưu Master' để lưu đĩa"],
    ];

    rows.forEach(([label, value]) => {
        const row = table.insertRow();
        const cellLabel = row.insertCell();
        cellLabel.textContent = label;
        cellLabel.style.fontWeight = "600";
        cellLabel.style.width = "40%";
        cellLabel.style.padding = "6px 10px";

        const cellVal = row.insertCell();
        cellVal.textContent = value;
        cellVal.style.padding = "6px 10px";
    });
    wrapper.appendChild(table);

    boxContentAirBubbles.appendChild(wrapper);
}

// Xử lý nút "Xác định đường hàn"
identifyWeldSeamButton?.addEventListener("click", async () => {
    if (!selected || selected.product_id < 0 || selected.frame_id < 0 || selected.items_id < 0) {
        write_log_clear(logAirBubbles, "Chưa chọn đầy đủ sản phẩm, frame và item.");
        return;
    }
    write_log_clear(logAirBubbles, "⏳ Đang xác định đường hàn bằng U-Net & Skeleton...");
    try {
        const result = await postData("/law_regulation/air_bubbles/identify_weld_seam", {
            select: selected,
        });
        if (!result?.ok) {
            write_log_clear(logAirBubbles, `❌ Lỗi xác định đường hàn: ${result?.message || "Không xác định"}`);
            return;
        }
        const weldData = result.data || {};
        const inspector = getInspector();
        inspector.setWeldData(weldData);

        // Vẽ lại canvas với viền đa giác xanh lá và trục tâm skeleton vàng
        inspector.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);

        // Render bảng thông số vào vùng cof-and-inf-tool-content
        renderWeldSeamInfoTable(weldData);

        write_log_clear(
            logAirBubbles,
            "✅ Đã xác định đường hàn thành công! Viền đa giác (xanh lá) và trục tâm (vàng) đã được vẽ lên ảnh.",
        );
    } catch (error) {
        write_log_clear(logAirBubbles, `❌ Lỗi kết nối API xác định đường hàn: ${error.message}`);
    }
});

deleteWeldSeamButton?.addEventListener("click", async () => {
    if (!selected || selected.product_id < 0 || selected.frame_id < 0 || selected.items_id < 0) {
        write_log_clear(logAirBubbles, "Chưa chọn đầy đủ sản phẩm, frame và item.");
        return;
    }
    const inspector = getInspector();
    if (!inspector) {
        write_log_clear(logAirBubbles, "Không tìm thấy dữ liệu item đang chọn.");
        return;
    }

    deleteWeldSeamButton.disabled = true;
    write_log_clear(logAirBubbles, "⏳ Đang xóa đường hàn...");
    try {
        const result = await postData("/law_regulation/air_bubbles/delete_weld_reference", {
            select: selected,
        });
        if (!result?.ok) {
            write_log_clear(logAirBubbles, `❌ ${result?.message || "Xóa đường hàn thất bại."}`);
            return;
        }

        inspector.setWeldReferenceId(null);
        inspector.setWeldData(null);
        inspector.removeBoxs();
        boxContentAirBubbles.innerHTML = "";
        inspector.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
        updateHighlight();
        write_log_clear(
            logAirBubbles,
            result.data?.deleted
                ? "✅ Đã xóa đường hàn; giữ lại vùng bọt khí."
                : "ℹ️ Không có đường hàn đã lưu; giữ lại vùng bọt khí.",
        );
    } catch (error) {
        write_log_clear(logAirBubbles, `❌ Xóa đường hàn thất bại: ${error.message}`);
    } finally {
        deleteWeldSeamButton.disabled = false;
    }
});

judgmentButton?.addEventListener("click", async () => {
    const inspector = getInspector();
    const regions = inspector?.rectangles || [];
    if (!selected || selected.product_id < 0 || selected.frame_id < 0 || selected.items_id < 0) {
        write_log_clear(logAirBubbles, "Chưa chọn đầy đủ sản phẩm, frame và item.");
        return;
    }
    if (!regions.length) {
        write_log_clear(logAirBubbles, "Hãy vẽ và lưu ít nhất một vùng bọt khí.");
        return;
    }
    write_log_clear(logAirBubbles, "⏳ Đang phán định bọt khí đường hàn...");
    try {
        const payload = {
            select: selected,
            boxes: regions,
            WidthCanvas: WIDTH_IMG_SHAPE,
        };
        if (inspector.weld_data?.polygon) {
            payload.weld_polygon = inspector.weld_data.polygon;
        }
        if (inspector.weld_reference_id) {
            payload.weld_reference_id = inspector.weld_reference_id;
        }

        const result = await postData("/law_regulation/air_bubbles/run_model", payload);
        if (!result?.ok) {
            write_log_clear(logAirBubbles, result?.message || "Phán định thất bại.");
            return;
        }
        const data = result.data || {};
        const objects = data.objects || [];
        inspector.removeBoxs();
        inspector.appendBoxes(objects);
        canvasManager.clearShapeCanvas();
        inspector.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);

        // Render bảng phán định OK/NG vào table-cof-air-bubbles
        renderAirBubblesResultTable(data);

        if (data.status === "DETECT_ONLY" || data.has_weld_reference === false) {
            write_log_clear(
                logAirBubbles,
                `⚠️ ${data.message || "Thiếu polygon đường hàn; chưa thể phán định OK/NG."} Nhấn “Xác định đường hàn” rồi chạy lại để phán định.`,
            );
        } else {
            write_log_clear(
                logAirBubbles,
                data.is_ok
                    ? "Phán định OK: Không phát hiện bọt khí."
                    : `Phán định NG: ${data.message || `Phát hiện ${objects.length} bọt khí.`}`,
            );
        }
    } catch (error) {
        write_log_clear(logAirBubbles, `Lỗi phán định: ${error.message}`);
    }
});

export async function event_transition_items() {
    boxContentAirBubbles.innerHTML = "";
    obj_region_air_bubbles_canvas.reset();
    canvasManager.clearShapeCanvas();
    const inspector = getInspector();

    // Nếu inspector đã có weld_reference_id từ Master nhưng chưa nạp weld_data toạ độ, tải từ server
    if (inspector?.weld_reference_id && !inspector?.weld_data) {
        try {
            const res = await fetchGet(`/law_regulation/air_bubbles/weld_reference/${inspector.weld_reference_id}`);
            if (res?.ok && res.data) {
                inspector.setWeldData(res.data);
                renderWeldSeamInfoTable(res.data);
            }
        } catch (err) {
            console.warn("Không tải được tham chiếu đường hàn:", err);
        }
    } else if (inspector?.weld_data) {
        renderWeldSeamInfoTable(inspector.weld_data);
    }

    inspector?.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
    updateHighlight();
    write_log_clear(
        logAirBubbles,
        "Vẽ hai điểm để tạo vùng bọt khí. Hoặc nhấn 'Xác định đường hàn' để nhận diện đường hàn.",
    );
}

clearButton?.addEventListener("click", () => {
    const inspector = getInspector();
    inspector?.clear();
    obj_region_air_bubbles_canvas.reset();
    canvasManager.clearShapeCanvas();
    boxContentAirBubbles.innerHTML = "";
    inspector?.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
    updateHighlight();
    write_log_clear(logAirBubbles, "Đã xóa các vùng bọt khí trên frame hiện tại (Bản ghi đường hàn vẫn được giữ nguyên).");
});

closeButton?.addEventListener("click", () => {
    canvasManager.clearShapeCanvas();
    canvasManager.clearPreviewCanvas();
    canvasManager.setTool(null);
    boxContentAirBubbles.innerHTML = "";
    panner_region_air_bubbles.classList.remove("active");
    refesh_btn();
    get_obj_product()?.clearHighlight(scroll_container);
    setNameEventActivate(null);
});
