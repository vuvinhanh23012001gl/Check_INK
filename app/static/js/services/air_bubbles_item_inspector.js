import { ModelRectangle } from "../model/model_rectangle.js";


export class AirBubblesItemInspector {
    static NAME = "AirBubblesItemInspector";

    constructor(rectangles = []) {
        this.rectangles = Array.isArray(rectangles) ? rectangles : [];
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
        this.rectangles = [];
    }

    appendBoxes(boxes) {
        if (!this.boxs) this.boxs = [];
        if (Array.isArray(boxes)) this.boxs.push(...boxes);
        else if (boxes) this.boxs.push(boxes);
    }

    removeBoxs() {
        this.boxs = [];
    }

    drawAll(canvasManager, color = "#00A6FF") {
        canvasManager.clearShapeCanvas();
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
            context.save();
            context.strokeStyle = color;
            context.lineWidth = 2;
            context.strokeRect(x, y, width, height);
            context.fillStyle = color;
            context.font = "bold 12px Arial";
            context.fillText(
                `${object.class_name || "air_bubble"} (${((object.confidence || 0) * 100).toFixed(1)}%)`,
                x + 4,
                y + 14,
            );
            context.restore();
        }
    }

    toDict() {
        if (!this.rectangles.length) return null;
        const result = {};
        for (const rectangle of this.rectangles) {
            result[String(rectangle.id)] = rectangle.toDict();
        }
        return result;
    }

    static fromDict(data) {
        if (!data || typeof data !== "object") return new AirBubblesItemInspector();
        const rectangles = Object.entries(data).map(([id, rectangle]) => {
            const model = ModelRectangle.fromDict(rectangle);
            model.id = Number(rectangle?.id ?? id);
            return model;
        }).filter(rectangle => rectangle.isValid());
        return new AirBubblesItemInspector(rectangles);
    }
}
