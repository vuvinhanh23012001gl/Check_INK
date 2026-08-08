
import { ModelRectangle } from '../model/model_rectangle.js'; // Thay đổi đường dẫn cho đúng với dự án của bạn
import * as draw from "../utills/draw.js";

export class PermeableMembraneInspector {
    static NAME = "MembraneInspector";

    constructor(rectangle =  null,polygons = null) {
        /** @type {ModelRectangle|null} Đối tượng ROI duy nhất */
        this.rectangle = rectangle;

        /** @type {Array} Danh sách lưu các tập hợp polygon nhận được từ AI */
        this.polygons = polygons ;
    }

    // ==========================================
    // 1. QUẢN LÝ ROI CỦA MÀNG THẤM (RECTANGLE)
    // ==========================================
    setMembrane(modelRect) {
        if (!(modelRect instanceof ModelRectangle)) {
            console.error("Đối tượng thêm vào không phải là Instance của ModelRectangle");
            return false;
        }
        this.rectangle = modelRect;
        return true;
    }

    getMembrane() {
        return this.rectangle;
    }

    removeMembrane() {
        if (this.rectangle) {
            this.rectangle = null;
            this.removePolygons(); // Xóa sạch dữ liệu polygon khi xóa ROI
            return true;
        }
        return false;
    }

    // ==========================================
    // 2. QUẢN LÝ DANH SÁCH POLYGONS (TƯƠNG TỰ BOXS)
    // ==========================================
    getPolygons() {
        return this.polygons;
    }

    appendPolygons(polygonData) {
        if (!polygonData) return;
        if (Array.isArray(polygonData)) {
            this.polygons.push(...polygonData);
        } else if (typeof polygonData === 'object') {
            this.polygons.push(polygonData);
        }
    }

    removePolygons() {
        if (this.polygons && this.polygons.length > 0) {
            this.polygons = [];
            return true;
        }
        return false;
    }

    /**
     * Helper tiện ích để nạp kết quả trả về từ API Backend vào danh sách `polygons`
     */
    setDetectResult(polygonBorder = [], polygonInner = [], imgWidthReal = 2048, canvasWidth = 800) {
        if (polygonBorder && polygonBorder.length > 0) {
            this.appendPolygons({
                type: 'border',
                label: 'Border Membrane',
                points: polygonBorder,
                imgWidthReal: imgWidthReal,
                canvasWidth: canvasWidth,
                color: "#00FF7F" // Xanh lá
            });
        }

        if (polygonInner && polygonInner.length > 0) {
            this.appendPolygons({
                type: 'inner',
                label: 'Inner Membrane',
                points: polygonInner,
                imgWidthReal: imgWidthReal,
                canvasWidth: canvasWidth,
                color: "#FF3B30" // Đỏ
            });
        }
    }

    // ==========================================
    // 3. TÍNH TOÁN & TƯƠNG TÁC (INTERACTION)
    // ==========================================
    findClickedMembrane(px, py) {
        if (!this.rectangle) return null;

        const clickX = Number(px);
        const clickY = Number(py);

        const rx = Number(this.rectangle.x);
        const ry = Number(this.rectangle.y);
        const rw = Number(this.rectangle.width);
        const rh = Number(this.rectangle.height);

        if (Number.isNaN(rx) || Number.isNaN(ry) || Number.isNaN(rw) || Number.isNaN(rh)) {
            return null;
        }

        if (clickX >= rx && clickX <= rx + rw && clickY >= ry && clickY <= ry + rh) {
            return this.rectangle;
        }

        return null;
    }

    isPointOnMembraneBorder(px, py, offset = 5) {
        if (!this.rectangle) return false;

        const rect = this.rectangle;

        const x = Math.min(rect.xStart, rect.xEnd);
        const y = Math.min(rect.yStart, rect.yEnd);
        const width = Math.abs(rect.xEnd - rect.xStart);
        const height = Math.abs(rect.yEnd - rect.yStart);

        return (
            (Math.abs(py - y) <= offset && px >= x - offset && px <= x + width + offset) ||
            (Math.abs(py - (y + height)) <= offset && px >= x - offset && px <= x + width + offset) ||
            (Math.abs(px - x) <= offset && py >= y - offset && py <= y + height + offset) ||
            (Math.abs(px - (x + width)) <= offset && py >= y - offset && py <= y + height + offset)
        );
    }

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

    // ==========================================
    // 4. VẼ VÀ HIỂN THỊ (CANVAS RENDERING)
    // ==========================================
    drawRectangle(canvasManager, colorRect = "#00E6FF", fontSize = 12) {
        if (this.rectangle) {
            const rect = this.rectangle;
            const x = Math.min(rect.xStart, rect.xEnd);
            const y = Math.min(rect.yStart, rect.yEnd);
            const width = Math.abs(rect.xEnd - rect.xStart);
            const height = Math.abs(rect.yEnd - rect.yStart);

            this.#renderSingleMembraneWorkflow(
                canvasManager,
                { x, y, width, height },
                rect.name || "",
                colorRect,
                fontSize
            );
        }
    }

    /**
     * Vẽ tất cả các polygon đã phát hiện từ `this.polygons` lên Canvas
     */
    drawPolygons(canvasManager, fontSize = 12) {
        if (!this.polygons || this.polygons.length === 0) return;

        const ctx = canvasManager.ctxShape;

        this.polygons.forEach((polyItem) => {
            if (!polyItem || !polyItem.points || polyItem.points.length === 0) return;

            const { points, imgWidthReal, canvasWidth, color, label } = polyItem;
            const scale = canvasWidth / (imgWidthReal || 2048);

            ctx.save();
            ctx.strokeStyle = color || "#FF3B30";
            ctx.fillStyle = color ? `${color}33` : "rgba(255, 59, 48, 0.2)"; // Bật alpha nền
            ctx.lineWidth = 2;

            ctx.beginPath();
            points.forEach((pt, idx) => {
                // pt có dạng [x, y] hoặc {x, y}
                const px = (Array.isArray(pt) ? pt[0] : pt.x) * scale;
                const py = (Array.isArray(pt) ? pt[1] : pt.y) * scale;

                if (idx === 0) {
                    ctx.moveTo(px, py);
                } else {
                    ctx.lineTo(px, py);
                }
            });
            ctx.closePath();
            ctx.fill();
            ctx.stroke();

            // Vẽ Nhãn (Label) ở điểm tọa độ đầu tiên của Polygon
            if (label && points.length > 0) {
                const firstPt = points[0];
                const lx = (Array.isArray(firstPt) ? firstPt[0] : firstPt.x) * scale;
                const ly = (Array.isArray(firstPt) ? firstPt[1] : firstPt.y) * scale;

                ctx.font = `bold ${fontSize}px Arial`;
                ctx.fillStyle = color || "#FF3B30";
                ctx.textAlign = "left";
                ctx.textBaseline = "bottom";
                ctx.fillText(label, lx + 4, ly - 4);
            }

            ctx.restore();
        });
    }

    #renderSingleMembraneWorkflow(canvasManager, coords, text, color, fontSize) {
        const ctx = canvasManager.ctxShape;
        const { x, y, width, height } = coords;

        ctx.save();
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, width, height);

        ctx.fillStyle = "rgba(0, 230, 255, 0.1)";
        ctx.fillRect(x, y, width, height);
        ctx.restore();

        if (text) {
            ctx.save();
            ctx.font = `bold ${fontSize}px Arial`;
            ctx.fillStyle = color;
            ctx.textAlign = "left";
            ctx.textBaseline = "top";
            ctx.fillText(text, x + 4, y + 4);
            ctx.restore();
        }
    }

    // ==========================================
    // 5. SERIALIZATION
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
            // Tương thích ngược với định dạng dict cũ
            const keys = Object.keys(fullDict);
            if (keys.length > 0 && keys[0] !== 'polygons') {
                const firstId = keys[0];
                const singleRectDict = { [firstId]: fullDict[firstId] };
                this.rectangle = ModelRectangle.fromDict(singleRectDict);
            }
        }

        if (Array.isArray(fullDict.polygons)) {
            this.polygons = fullDict.polygons;
        }
    }
    static fromDict(fullDict) {
        if (!fullDict){
            console.log("Tạo mới");
            return new PermeableMembraneInspector();
        }
        let model_rectangle = ModelRectangle.fromDict(fullDict);
        console.log("Tạo lớp PermeableMembraneInspector từ dữ liệu cũ");
        return new PermeableMembraneInspector(model_rectangle);
    }


}