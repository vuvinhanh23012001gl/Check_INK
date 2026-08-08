
import { ModelRectangle } from '../model/model_rectangle.js'; // Thay đổi đường dẫn cho đúng với dự án của bạn
import * as draw from "../utills/draw.js";
import { EndChippingInspector } from './end_chipping_item_inspector.js';

export class ArmCoverItemInspector {
    static NAME = "CoverSensorInspector";

    constructor(rectangle = null, boxs = null) {
        this.rectangle = rectangle;
        this.boxs = (Array.isArray(boxs) && boxs.length > 0) ? boxs : null;
    }

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
        if (this.boxs) {
            this.boxs = [];
            return true;
        }
        return false;
    }

    /**
     * Thiết lập/Cập nhật đối tượng ModelRectangle duy nhất
     * @param {ModelRectangle} modelRect 
     * @returns {boolean}
     */
    setRectangle(modelRect) {
        if (!(modelRect instanceof ModelRectangle)) {
            console.error("Đối tượng thêm vào không phải là Instance của ModelRectangle");
            return false;
        }
        this.rectangle = modelRect;
        return true;
    }

    /**
     * Lấy ra đối tượng ModelRectangle hiện tại
     * @returns {ModelRectangle|null}
     */
    getRectangle() {
        return this.rectangle;
    }

    /**
     * Xóa đối tượng ModelRectangle hiện tại bằng cách đặt về null
     * Đồng thời tự động xóa cả danh sách boxs
     * @returns {boolean}
     */
    removeRectangle() {
        if (this.rectangle) {
            this.rectangle = null;
            this.removeBoxs();
            return true;
        }
        return false;
    }

    /**
     * Tìm xem tọa độ click (px, py) có nằm bên trong hình chữ nhật hay không
     * @param {number} px 
     * @param {number} py 
     * @returns {ModelRectangle|null}
     */
    findClickedRectangle(px, py) {
        if (!this.rectangle) {
            return null;
        }

        const clickX = Number(px);
        const clickY = Number(py);

        const rx = Number(this.rectangle.x);
        const ry = Number(this.rectangle.y);
        const rw = Number(this.rectangle.width);
        const rh = Number(this.rectangle.height);

        if (Number.isNaN(rx) || Number.isNaN(ry) || Number.isNaN(rw) || Number.isNaN(rh)) {
            return null;
        }

        // Kiểm tra va chạm hộp (AABB) cho đối tượng duy nhất
        if (clickX >= rx && clickX <= rx + rw && clickY >= ry && clickY <= ry + rh) {
            return this.rectangle;
        }

        return null;
    }

    /**
     * Kiểm tra xem đối tượng duy nhất có hợp lệ không
     */
    validateAll() {
        const report = { isValid: true, allErrors: {} };

        if (this.rectangle && typeof this.rectangle.validateRectangle === "function") {
            const validation = this.rectangle.validateRectangle();
            if (!validation.isValid) {
                report.isValid = false;
                report.allErrors[this.rectangle.id_rect] = validation.errors;
            }
        }

        return report;
    }

    /**
     * Xuất đối tượng hiện tại thành cấu trúc Object Dict tổng hợp
     */
    toDict() {
        if (!this.rectangle) return null;
        return this.rectangle.toDict();
    }

    /**
     * Nạp dữ liệu từ một Object Dict tổng hợp vào đối tượng duy nhất
     */
    static fromDict(fullDict) {
        if (!fullDict){
            console.log("Tạo mới");
            return new ArmCoverItemInspector();
        }
        console.log("ARM CORVER FULLDICT",fullDict);
        let model_rectangle = ModelRectangle.fromDict(fullDict);
        console.log("Tạo lớp ARM cover");
        return new ArmCoverItemInspector(model_rectangle);

    }
        /**
     * Vẽ hình chữ nhật cảm biến duy nhất lên canvas
     */
    drawAllRectangles(canvasManager, color = "#00E6FF", fontSize = 12) {
        canvasManager.clearShapeCanvas();

        if (!this.rectangle) return;

        const rect = this.rectangle;

        const x = Math.min(rect.xStart, rect.xEnd);
        const y = Math.min(rect.yStart, rect.yEnd);
        const width = Math.abs(rect.xEnd - rect.xStart);
        const height = Math.abs(rect.yEnd - rect.yStart);

        this.#renderSingleRectWorkflow(
            canvasManager,
            { x, y, width, height },
            rect.name || "",
            color,
            fontSize
        );
    }

    /**
     * Kiểm tra tọa độ xem có nằm trên đường viền của hình chữ nhật không
     */
    isPointOnRectangleBorder(px, py, offset = 5) {
        if (!this.rectangle) return false;

        const rect = this.rectangle;

        const x = Math.min(rect.xStart, rect.xEnd);
        const y = Math.min(rect.yStart, rect.yEnd);
        const width = Math.abs(rect.xEnd - rect.xStart);
        const height = Math.abs(rect.yEnd - rect.yStart);

        return (
            // Cạnh trên
            (Math.abs(py - y) <= offset && px >= x - offset && px <= x + width + offset) ||
            // Cạnh dưới
            (Math.abs(py - (y + height)) <= offset && px >= x - offset && px <= x + width + offset) ||
            // Cạnh trái
            (Math.abs(px - x) <= offset && py >= y - offset && py <= y + height + offset) ||
            // Cạnh phải
            (Math.abs(px - (x + width)) <= offset && py >= y - offset && py <= y + height + offset)
        );
    }

    /**
     * Quy trình vẽ chi tiết cho một hình chữ nhật kèm text
     */
    #renderSingleRectWorkflow(canvasManager, coords, text, color, fontSize) {
        const ctx = canvasManager.ctxShape;
        const { x, y, width, height } = coords;

        ctx.save();
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, width, height);
        
        ctx.fillStyle = "rgba(0, 230, 255, 0.1)";
        ctx.fillRect(x, y, width, height);
        ctx.restore();

        ctx.save();
        ctx.font = `bold ${fontSize}px Arial`;
        ctx.fillStyle = color;
        ctx.textAlign = "left";
        ctx.textBaseline = "top";
        ctx.fillText(text, x + 4, y + 4);
        ctx.restore();
    }

    /**
     * Vẽ toàn bộ các đối tượng đã nhận diện trực tiếp từ `this.boxs` lên Canvas
     * @param {CanvasManager} canvasManager - Đối tượng quản lý Canvas vẽ
     * @param {string} [color="#FF3B30"] - Màu sắc đường viền vẽ (mặc định đỏ)
     * @param {number} [fontSize=12] - Cỡ chữ của nhãn (mặc định 12)
     */
    drawDetectedObjects(canvasManager, color = "#FF3B30", fontSize = 12) {
        if (!this.boxs || this.boxs.length === 0) {
            console.warn("Không có dữ liệu trong this.boxs để vẽ.");
            return;
        }

        // Lặp qua từng phần tử trong danh sách this.boxs để vẽ
        this.boxs.forEach((detectData) => {
            if (!detectData) return;

            const x1 = detectData.x1;
            const y1 = detectData.y1;
            const x2 = detectData.x2;
            const y2 = detectData.y2;
            const className = detectData.className;
            const confidence = detectData.confidence;
            const imgWidthReal = detectData.imgWidthReal || 2048;
            const canvasWidth = detectData.canvasWidth;
            const classId = detectData.classId !== undefined ? detectData.classId : 99;

            const scale = canvasWidth / imgWidthReal;
            const x1_canvas = x1 * scale;
            const y1_canvas = y1 * scale;
            const x2_canvas = x2 * scale;
            const y2_canvas = y2 * scale;

            const label = `${className || ''} (${((confidence || 0) * 100).toFixed(1)}%)`;

            const detectedRect = new ModelRectangle(
                classId,
                label,
                x1_canvas,
                y1_canvas,
                x2_canvas,
                y2_canvas
            );

            const x = Math.min(detectedRect.xStart, detectedRect.xEnd);
            const y = Math.min(detectedRect.yStart, detectedRect.yEnd);
            const width = Math.abs(detectedRect.xEnd - detectedRect.xStart);
            const height = Math.abs(detectedRect.yEnd - detectedRect.yStart);

            this.#renderSingleRectWorkflow(
                canvasManager,
                { x, y, width, height },
                detectedRect.name,
                color,
                fontSize
            );
        });
    }
}