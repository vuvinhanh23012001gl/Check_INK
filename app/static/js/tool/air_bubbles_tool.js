wimport { ModelRectangle } from "../model/model_rectangle.js";
import { canvasManager, scroll_container, WIDTH_IMG_SHAPE } from "../common_value.js";
import { RectangleDrawer } from "../canvas/rectangel_drawer_canvas.js";
import { AirBubblesItemInspector } from "../services/air_bubbles_item_inspector.js";
import { ItemsInspector } from "../services/items_inspector.js";
import { postData } from "../utills/api.js";
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
    write_log_clear(logAirBubbles, "Đang phán định bọt khí đường hàn...");
    try {
        const result = await postData("/law_regulation/air_bubbles/run_model", {
            select: selected,
            boxes: regions,
            WidthCanvas: WIDTH_IMG_SHAPE,
        });
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
        inspector.drawDetectedObjects(canvasManager);
        write_log_clear(
            logAirBubbles,
            data.is_ok
                ? "Phán định OK: Không phát hiện bọt khí."
                : `Phán định NG: Phát hiện ${objects.length} bọt khí.`,
        );
    } catch (error) {
        write_log_clear(logAirBubbles, `Lỗi phán định: ${error.message}`);
    }
});

export function event_transition_items() {
    boxContentAirBubbles.innerHTML = "";
    obj_region_air_bubbles_canvas.reset();
    canvasManager.clearShapeCanvas();
    const inspector = getInspector();
    inspector?.drawAll(canvasManager, COLOR_RECT_SHAPE_REGION_DETECT);
    updateHighlight();
    write_log_clear(
        logAirBubbles,
        "Vẽ hai điểm để tạo vùng. Chấp nhận xong có thể vẽ vùng tiếp theo.",
    );
}

clearButton?.addEventListener("click", () => {
    const inspector = getInspector();
    inspector?.clear();
    obj_region_air_bubbles_canvas.reset();
    canvasManager.clearShapeCanvas();
    boxContentAirBubbles.innerHTML = "";
    updateHighlight();
    write_log_clear(logAirBubbles, "Đã xóa tất cả vùng kiểm tra bọt khí.");
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
