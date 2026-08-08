
import { ModelRectangle } from '../model/model_rectangle.js';
import * as draw from "../utills/draw.js";

export class EndChippingInspector {
    static NAME = "EndChippingInspector";

    constructor(cropRoi = null,threshold = 0 ) {
        /** @type {ModelRectangle|null} Khung vùng chính dùng để cắt ảnh */
        this.cropRoi = cropRoi;
        /** @type {number} Ngưỡng thresholdNG */
        this.threshold = threshold; 
    }

    // ==========================================
    // 1. QUẢN LÝ KHUNG CẮT ẢNH (CROP ROI)
    // ==========================================
    setCropRoi(modelRectangle) {
        if (!(modelRectangle instanceof ModelRectangle)) {
            console.error("Đối tượng thêm vào phải là Instance của ModelRectangle");
            return false;
        }
        this.cropRoi = modelRectangle;
        return true;
    }

    getCropRoi() {
        return this.cropRoi;
    }

    removeCropRoi() {
        if (this.cropRoi) {
            this.cropRoi = null;
            return true;
        }
        return false;
    }

    // ==========================================
    // 2. QUẢN LÝ CẤU HÌNH NGƯỠNG (THRESHOLD)
    // ==========================================
    getThreshold() {
        return this.threshold ?? 0;
    }

    /**
     * Cập nhật ngưỡng thresholdNG
     * @param {number} thresholdVal 
     */
    setThreshold(thresholdVal) {
        this.threshold = Number(thresholdVal) || 0;
    }

    /**
     * Tương thích dữ liệu đầu vào khi truyền từ config
     * @param {number|Object|Array} config 
     */
    appendThresholds(config) {
        if (config === null || config === undefined) return;

        if (typeof config === 'number') {
            this.threshold = config;
        } else if (Array.isArray(config)) {
            const first = config[0];
            this.threshold = typeof first === 'object' ? (first?.thresholdNG ?? 0) : (Number(first) || 0);
        } else if (typeof config === 'object') {
            this.threshold = config.thresholdNG ?? 0;
        }
    }

    clearThresholds() {
        this.threshold = 0;
        return true;
    }

    // ==========================================
    // 3. TÍNH TOÁN & TƯƠNG TÁC (INTERACTION)
    // ==========================================
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

    findClickedArea(px, py) {
        const clickX = Number(px);
        const clickY = Number(py);

        if (Number.isNaN(clickX) || Number.isNaN(clickY)) return null;

        if (this.cropRoi) {
            const bounds = this.#getBounds(this.cropRoi);
            if (bounds && clickX >= bounds.x && clickX <= bounds.x + bounds.width &&
                clickY >= bounds.y && clickY <= bounds.y + bounds.height) {
                return this.cropRoi;
            }
        }

        return null;
    }

    isPointOnRoiBorder(px, py, offset = 5) {
        if (!this.cropRoi) return false;

        const bounds = this.#getBounds(this.cropRoi);
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
    drawAll(canvasManager, roiColor = "#00E6FF", fontSize = 12) {
        canvasManager.clearShapeCanvas();

        if (this.cropRoi) {
            const bounds = this.#getBounds(this.cropRoi);
            if (bounds) {
                this.#renderBox(
                    canvasManager,
                    bounds,
                    this.cropRoi.name || "Crop Area",
                    roiColor,
                    fontSize,
                    "rgba(0, 230, 255, 0.1)"
                );
            }
        }
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
    toDict() { if (!this.cropRoi) { return null; } return { ...this.cropRoi.toDict(), threshold: Number(this.threshold) || 0 }; }

    static fromDict(fullDict) {
        if (!fullDict){
            console.log("Tạo mới");
            return new EndChippingInspector();
        }
        console.log("EndChippingInspector FULLDICT",fullDict);
        let model_rectangle = ModelRectangle.fromDict(fullDict);
        let threshold = fullDict?.threshold || 0;
        console.log("Ngưỡng",threshold);
        console.log("Tạo lớp EndChippingInspector");
        return new EndChippingInspector(model_rectangle,threshold);
    }
}

