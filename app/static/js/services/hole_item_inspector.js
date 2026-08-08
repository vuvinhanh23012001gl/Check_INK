

import { ModelRectangle } from '../model/model_rectangle.js';
import * as draw from "../utills/draw.js";

export class HoleItemInspector {
    static NAME = "HoleItemInspector";

    constructor(rectangle = null, boxs = []) {
        /** @type {ModelRectangle|null} Khung vùng chính dùng để cắt ảnh (Crop Region of Interest) */
        this.rectangle = rectangle;
        /** @type {Array} Danh sách các đối tượng/lỗ phát hiện được từ AI */
        this.boxs = boxs;
    }

    // ==========================================
    // 1. QUẢN LÝ KHUNG CẮT ẢNH (CROP ROI / RECTANGLE)
    // ==========================================
    setRectangle(modelRectangle) {
        if (!(modelRectangle instanceof ModelRectangle)) {
            console.error("Đối tượng thêm vào phải là Instance của ModelRectangle");
            return false;
        }
        this.rectangle = modelRectangle;
        return true;
    }

    getRectangle() {
        return this.rectangle;
    }

    removeRectangle() {
        if (this.rectangle) {
            this.rectangle = null;
            this.removeBoxs(); // Tự động dọn dẹp luôn danh sách boxs khi xóa ROI/Rectangle
            return true;
        }
        return false;
    }

    // ==========================================
    // 2. QUẢN LÝ DANH SÁCH BBOX DỰ ĐOÁN (BOXS)
    // ==========================================
    /**
     * Lấy danh sách các đối tượng nhận diện (boxes)
     * @returns {Array}
     */
    getBoxs() {
        return this.boxs;
    }

    /**
     * Cập nhật/Thêm mới danh sách các đối tượng nhận diện (boxes)
     * @param {Array|Object} boxes 
     */
    appendBoxes(boxes) {
        if (!boxes) return;
        if (Array.isArray(boxes)) {
            this.boxs.push(...boxes);
        } else if (typeof boxes === 'object') {
            this.boxs.push(boxes);
        }
    }

    /**
     * Xóa danh sách các boxes
     * @returns {boolean}
     */
    removeBoxs() {
        if (this.boxs && this.boxs.length > 0) {
            this.boxs = [];
            return true;
        }
        return false;
    }

    // ==========================================
    // 3. TÍNH TOÁN & TƯƠNG TÁC (INTERACTION)
    // ==========================================
    /**
     * Lấy tọa độ chuẩn {x, y, width, height} của bất kỳ ModelRectangle nào
     */
    #getBounds(rect) {
        if (!rect) return null;

        const x1 = rect.xStart !== undefined ? rect.xStart : rect.x;
        const y1 = rect.yStart !== undefined ? rect.yStart : rect.y;
        const x2 = rect.xEnd !== undefined ? rect.xEnd : (x1 + rect.width);
        const y2 = rect.yEnd !== undefined ? rect.yEnd : (y1 + rect.height);

        return {
            x: Math.min(x1, x2),
            y: Math.min(y1, y2),
            width: Math.abs(x2 - x1),
            height: Math.abs(y2 - y1)
        };
    }

    /**
     * Tìm xem tọa độ click (px, py) có nằm trong Rectangle hay không
     */
    findClickedArea(px, py) {
        const clickX = Number(px);
        const clickY = Number(py);

        if (Number.isNaN(clickX) || Number.isNaN(clickY)) return null;

        if (this.rectangle) {
            const bounds = this.#getBounds(this.rectangle);
            if (bounds && clickX >= bounds.x && clickX <= bounds.x + bounds.width &&
                clickY >= bounds.y && clickY <= bounds.y + bounds.height) {
                return this.rectangle;
            }
        }

        return null;
    }

    /**
     * Kiểm tra điểm click có nằm trên viền của khung Rectangle hay không
     */
    isPointOnRoiBorder(px, py, offset = 5) {
        if (!this.rectangle) return false;

        const bounds = this.#getBounds(this.rectangle);
        if (!bounds) return false;

        const { x, y, width, height } = bounds;
        const insideXBuffer = px >= x - offset && px <= x + width + offset;
        const insideYBuffer = py >= y - offset && py <= y + height + offset;

        return (
            (Math.abs(py - y) <= offset && insideXBuffer) ||            // Cạnh trên
            (Math.abs(py - (y + height)) <= offset && insideXBuffer) || // Cạnh dưới
            (Math.abs(px - x) <= offset && insideYBuffer) ||            // Cạnh trái
            (Math.abs(px - (x + width)) <= offset && insideYBuffer)     // Cạnh phải
        );
    }

    // ==========================================
    // 4. VẼ VÀ HIỂN THỊ (CANVAS RENDERING)
    // ==========================================
    /**
     * Vẽ khung Rectangle chính lên Canvas
     */
    drawAll(canvasManager, roiColor = "#00E6FF", fontSize = 12) {
        if (this.rectangle) {
            const bounds = this.#getBounds(this.rectangle);
            if (bounds) {
                this.#renderBox(
                    canvasManager,
                    bounds,
                    this.rectangle.name || "Crop Area",
                    roiColor,
                    fontSize,
                    "rgba(0, 230, 255, 0.1)"
                );
            }
        }
    }

    /**
     * Vẽ toàn bộ các đối tượng đã nhận diện trực tiếp từ `this.boxs` lên Canvas
     * @param {CanvasManager} canvasManager 
     * @param {string} [color="#FF3B30"] 
     * @param {number} [fontSize=12] 
     */
    drawDetectedObjects(canvasManager, color = "#FF3B30", fontSize = 12) {
        if (!this.boxs || this.boxs.length === 0) {
            console.warn("Không có dữ liệu trong this.boxs để vẽ.");
            return;
        }

        this.boxs.forEach((detectData) => {
            if (!detectData) return;

            const { x1, y1, x2, y2, className, confidence, canvasWidth } = detectData;
            const imgWidthReal = detectData.imgWidthReal || 2048;

            const scale = canvasWidth / imgWidthReal;
            const x1_canvas = x1 * scale;
            const y1_canvas = y1 * scale;
            const x2_canvas = x2 * scale;
            const y2_canvas = y2 * scale;

            const bounds = {
                x: Math.min(x1_canvas, x2_canvas),
                y: Math.min(y1_canvas, y2_canvas),
                width: Math.abs(x2_canvas - x1_canvas),
                height: Math.abs(y2_canvas - y1_canvas)
            };

            const label = `${className || ''} (${((confidence || 0) * 100).toFixed(1)}%)`;

            this.#renderBox(
                canvasManager,
                bounds,
                label,
                color,
                fontSize,
                "rgba(255, 59, 48, 0.15)"
            );
        });
    }

    #renderBox(canvasManager, coords, labelText, strokeColor, fontSize, fillColor) {
        const ctx = canvasManager.ctxShape;
        const { x, y, width, height } = coords;

        ctx.save();
        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, width, height);

        if (fillColor) {
            ctx.fillStyle = fillColor;
            ctx.fillRect(x, y, width, height);
        }
        ctx.restore();

        if (labelText) {
            ctx.save();
            ctx.font = `bold ${fontSize}px Arial`;
            ctx.fillStyle = strokeColor;
            ctx.textAlign = "left";
            ctx.textBaseline = "top";
            ctx.fillText(labelText, x + 4, y + 4);
            ctx.restore();
        }
    }

    // ==========================================
    // 5. SERIALIZATION (TO / FROM DICT)
    // ==========================================
    toDict() {
        if (!this.rectangle)return null;
        return this.rectangle.toDict();
    }

    static fromDict(fullDict) {
        if (!fullDict){
            console.log("Tạo mới");
            return new HoleItemInspector();
        }
        console.log("fullDict",fullDict);
        let model_rectangle = ModelRectangle.fromDict(fullDict);
        console.log("Tạo lớp HoleItemInspector");
        return new HoleItemInspector(model_rectangle);
    }
}