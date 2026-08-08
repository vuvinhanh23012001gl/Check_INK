

import { ModelRectangle } from '../model/model_rectangle.js';
import * as draw from "../utills/draw.js";

export class ScratchedPipeItemInspector {
    static NAME = "ScratchedPipeItemInspector";

    constructor(rectangle = null,boxes = []) {
        /** @type {ModelRectangle|null} Khung chữ nhật chính */
        this.rectangle = rectangle;

        /** @type {Array<ModelRectangle>} Danh sách các hộp/đối tượng phát hiện được (Box / Sub-items) */
        this.boxes = boxes;
    }

    // ==========================================
    // 1. QUẢN LÝ KHUNG CHỮ NHẬT CHÍNH (RECTANGLE)
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
            return true;
        }
        return false;
    }

    // ==========================================
    // 2. QUẢN LÝ DANH SÁCH BỘ DỊCH / BOXES (SUB-ITEMS)
    // ==========================================
    /**
     * Thêm một Box/đối tượng phát hiện vào danh sách
     */
    addBox(detectData) {
        if (!detectData) {
            console.error("Đối tượng thêm vào phải là Instance của ModelRectangle");
            return false;
        }
        this.boxes.push(detectData);
        return true;
    }

    /**
     * Lấy danh sách tất cả các Boxes
     */
    getBoxes() {
        return this.boxes;
    }

    /**
     * Lấy Box theo chỉ số Index
     */
    getBoxAt(index) {
        if (index >= 0 && index < this.boxes.length) {
            return this.boxes[index];
        }
        return null;
    }

    clearBoxes() {
        this.boxes = [];
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
     * Kiểm tra điểm click (px, py) có nằm trong Rectangle chính hoặc bất kỳ Box nào không.
     * Ưu tiên trả về Box phát hiện được trước, nếu không sẽ trả về Rectangle chính.
     */
    findClickedArea(px, py, checkSubItems = true) {
        const clickX = Number(px);
        const clickY = Number(py);

        if (Number.isNaN(clickX) || Number.isNaN(clickY)) return null;

        // 1. Kiểm tra va chạm với các Boxes trước (nếu bật checkSubItems)
        if (checkSubItems && this.boxes.length > 0) {
            for (let i = this.boxes.length - 1; i >= 0; i--) { // Duyệt ngược để lấy box nằm trên cùng
                const box = this.boxes[i];
                const bounds = this.#getBounds(box);
                if (bounds && clickX >= bounds.x && clickX <= bounds.x + bounds.width &&
                    clickY >= bounds.y && clickY <= bounds.y + bounds.height) {
                    return box;
                }
            }
        }

        // 2. Kiểm tra va chạm với Rectangle chính
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
     * Kiểm tra điểm click có nằm trên viền của Rectangle chính hoặc Box nào không
     */
    isPointOnRoiBorder(px, py, offset = 5) {
        const checkBorder = (rect) => {
            if (!rect) return false;
            const bounds = this.#getBounds(rect);
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
        };

        // Kiểm tra Rectangle chính
        if (checkBorder(this.rectangle)) return true;

        // Kiểm tra danh sách Boxes
        for (const box of this.boxes) {
            if (checkBorder(box)) return true;
        }

        return false;
    }

    // ==========================================
    // 4. RENDERING & DRAWING
    // ==========================================
    drawRectangle(canvasManager, roiColor = "#00E6FF", fontSize = 12) {
        canvasManager.clearShapeCanvas();

        if (!this.rectangle) return;

        const bounds = this.#getBounds(this.rectangle);
        if (bounds) {
            this.#renderBox(
                canvasManager,
                bounds,
                this.rectangle.name || "Main Rectangle",
                roiColor,
                fontSize,
                "rgba(0, 230, 255, 0.1)"
            );
        }
    }

    /**
     * Vẽ một hình chữ nhật nhận diện vết trầy xước từ AI / Detector truyền trực tiếp
     */
    drawScratchedItem(canvasManager, color = "#FF3B30", fontSize = 12) {
        // Kiểm tra nếu danh sách boxes rỗng hoặc không tồn tại thì dừng
        if (!this.boxes || this.boxes.length === 0) return;

        // Duyệt qua từng box trong mảng this.boxes
        this.boxes.forEach((detectData) => {
            if (!detectData) return;

            const {
                x1, y1, x2, y2,
                className = "",
                confidence = 0,
                imgWidthReal = 2048,
                canvasWidth,
                classId = 99
            } = detectData;

            // Quy đổi tỷ lệ Scale
            const scale = canvasWidth ? (canvasWidth / imgWidthReal) : 1;
            const label = className ? `${className} (${(confidence * 100).toFixed(1)}%)` : '';

            // Tạo đối tượng hình chữ nhật theo tọa độ sau khi scale
            const detectedRect = new ModelRectangle(
                classId,
                label,
                x1 * scale,
                y1 * scale,
                x2 * scale,
                y2 * scale
            );

            const bounds = this.#getBounds(detectedRect);
            if (!bounds) return;

            // Render box lên canvas
            this.#renderBox(
                canvasManager,
                bounds,
                detectedRect.name,
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
        if(!this.rectangle)return null;
        return this.rectangle.toDict();
    }

    static fromDict(fullDict) {
        if (!fullDict || typeof fullDict !== 'object') return;
        if (fullDict.rectangle) {
            this.rectangle = ModelRectangle.fromDict(fullDict.rectangle);
        } else {
            this.rectangle = null;
        }

        // Restore danh sách Boxes
        if (Array.isArray(fullDict.boxes)) {
            this.boxes = fullDict.boxes.map(itemDict => ModelRectangle.fromDict(itemDict));
        } else {
            this.boxes = [];
        }
    }
    static fromDict(fullDict) {
        if (!fullDict){
            console.log("Tạo mới");
            return new ScratchedPipeItemInspector();
        }
        let model_rectangle = ModelRectangle.fromDict(fullDict);
        return new ScratchedPipeItemInspector(model_rectangle);
    }
}