import { ModelRectangle } from "../model/model_rectangle.js";


export class AirBubblesItemInspector {
    static NAME = "AirBubblesItemInspector";

    constructor(rectangles = [], weld_reference_id = null, weld_data = null) {
        this.rectangles = Array.isArray(rectangles) ? rectangles : [];
        this.weld_reference_id = weld_reference_id;
        this.weld_data = weld_data; // { polygon, skeleton, width, height }
        this.boxs = [];
    }

    setWeldData(weldData) {
        this.weld_data = weldData;
    }

    setWeldReferenceId(id) {
        this.weld_reference_id = id;
    }

    addRectangle(rectangle) {
        if (!(rectangle instanceof ModelRectangle)) return false;
        const index = this.rectangles.findIndex(item => item.id === rectangle.id);
        if (index >= 0) this.rectangles[index] = rectangle;
        else this.rectangles.push(rectangle);
        return true;
    }

    getNextId() {
        if (!this.rectangles.length) return 0;
        return Math.max(...this.rectangles.map(item => Number(item.id) || 0)) + 1;
    }

    findRectangleOnBorder(px, py, offset = 10) {
        for (let index = this.rectangles.length - 1; index >= 0; index--) {
            const rectangle = this.rectangles[index];
            const nearHorizontal = px >= rectangle.xStart - offset && px <= rectangle.xEnd + offset;
            const nearVertical = py >= rectangle.yStart - offset && py <= rectangle.yEnd + offset;
            if (
                (Math.abs(py - rectangle.yStart) <= offset && nearHorizontal) ||
                (Math.abs(py - rectangle.yEnd) <= offset && nearHorizontal) ||
                (Math.abs(px - rectangle.xStart) <= offset && nearVertical) ||
                (Math.abs(px - rectangle.xEnd) <= offset && nearVertical)
            ) return rectangle;
        }
        return null;
    }

    removeRectangle(id) {
        const index = this.rectangles.findIndex(item => item.id === id);
        if (index < 0) return false;
        this.rectangles.splice(index, 1);
        return true;
    }

    clear() {
        // Chỉ xóa vùng vẽ tay và các box bọt khí phát hiện; GIỮ NGUYÊN bản ghi đường hàn
        this.rectangles = [];
        this.boxs = [];
    }

    appendBoxes(boxes) {
        if (!this.boxs) this.boxs = [];
        if (Array.isArray(boxes)) this.boxs.push(...boxes);
        else if (boxes) this.boxs.push(boxes);
    }

    removeBoxs() {
        this.boxs = [];
    }

    drawWeldReference(canvasManager) {
        if (!this.weld_data) return;
        const context = canvasManager.ctxShape;
        const widthImg = this.weld_data.width || 2048;
        const canvasW = canvasManager.canvasWidth || 1024;
        const scale = canvasW / widthImg;

        const polygon = this.weld_data.polygon || [];
        const skeleton = this.weld_data.skeleton || [];

        context.save();

        // 1. Vẽ Polygon viền đường hàn (Màu xanh lá)
        if (Array.isArray(polygon) && polygon.length > 0) {
            context.strokeStyle = "#00E676";
            context.lineWidth = 2.5;
            context.fillStyle = "rgba(0, 230, 118, 0.08)";

            for (const poly of polygon) {
                if (!Array.isArray(poly) || poly.length < 3) continue;
                context.beginPath();
                context.moveTo(poly[0][0] * scale, poly[0][1] * scale);
                for (let i = 1; i < poly.length; i++) {
                    context.lineTo(poly[i][0] * scale, poly[i][1] * scale);
                }
                context.closePath();
                context.stroke();
                context.fill();
            }
        }

        // 2. Vẽ Skeleton các điểm tâm đường hàn (Màu vàng)
        if (Array.isArray(skeleton) && skeleton.length > 0) {
            context.fillStyle = "#FFD600";
            for (const pt of skeleton) {
                if (!Array.isArray(pt) || pt.length < 2) continue;
                context.beginPath();
                context.arc(pt[0] * scale, pt[1] * scale, 2.5, 0, Math.PI * 2);
                context.fill();
            }
        }

        context.restore();
    }

    drawAll(canvasManager, color = "#00A6FF") {
        canvasManager.clearShapeCanvas();

        // Vẽ tham chiếu đường hàn trước (nền)
        this.drawWeldReference(canvasManager);

        const context = canvasManager.ctxShape;
        for (const rectangle of this.rectangles) {
            context.save();
            context.strokeStyle = color;
            context.lineWidth = 2;
            context.strokeRect(
                rectangle.xStart,
                rectangle.yStart,
                rectangle.width,
                rectangle.height,
            );
            context.fillStyle = color;
            context.font = "bold 14px Arial";
            context.fillText(
                rectangle.name || `Bọt khí ${rectangle.id + 1}`,
                rectangle.xStart + 4,
                rectangle.yStart + 18,
            );
            context.restore();
        }

        // Nếu có bọt khí phát hiện, vẽ đè lên
        if (this.boxs && this.boxs.length > 0) {
            this.drawDetectedObjects(canvasManager);
        }
    }

    drawDetectedObjects(canvasManager, color = "#FF3B30") {
        if (!this.boxs?.length) return;
        const context = canvasManager.ctxShape;
        for (const object of this.boxs) {
            const bbox = object.bbox;
            if (!bbox) continue;
            const scale = (object.canvasWidth || canvasManager.canvasWidth || 1024)
                / (object.image_width || 2048);
            const x = bbox.x1 * scale;
            const y = bbox.y1 * scale;
            const width = (bbox.x2 - bbox.x1) * scale;
            const height = (bbox.y2 - bbox.y1) * scale;

            const boxColor = object.is_inside_weld === true
                ? "#FF1744"
                : object.is_inside_weld === false
                    ? "#FF6D00"
                    : "#1565C0";

            context.save();
            context.strokeStyle = boxColor;
            context.lineWidth = 2.5;
            context.strokeRect(x, y, width, height);

            context.fillStyle = boxColor;
            context.font = "bold 12px Arial";
            const locText = object.location_text ? ` [${object.location_text}]` : "";
            const confText = ` (${((object.confidence || 0) * 100).toFixed(1)}%)`;
            context.fillText(
                `${object.class_name || "Bọt khí"}${confText}${locText}`,
                x + 4,
                y + 14,
            );
            context.restore();
        }
    }

    toDict() {
        if (!this.rectangles.length && !this.weld_reference_id && !this.weld_data) return null;
        const result = {};
        for (const rectangle of this.rectangles) {
            result[String(rectangle.id)] = rectangle.toDict();
        }
        if (this.weld_reference_id) {
            result["weld_reference_id"] = this.weld_reference_id;
        }
        if (this.weld_data) {
            result["weld_data"] = this.weld_data;
        }
        return result;
    }

    static fromDict(data) {
        if (!data || typeof data !== "object") return new AirBubblesItemInspector();
        const rectangles = [];
        let weld_reference_id = null;
        let weld_data = null;

        for (const [key, value] of Object.entries(data)) {
            if (key === "weld_reference_id") {
                weld_reference_id = String(value);
            } else if (key === "weld_data") {
                weld_data = value;
            } else if (typeof value === "object" && value !== null) {
                const model = ModelRectangle.fromDict(value);
                model.id = Number(value?.id ?? key);
                if (model.isValid()) {
                    rectangles.push(model);
                }
            }
        }
        return new AirBubblesItemInspector(rectangles, weld_reference_id, weld_data);
    }
}
