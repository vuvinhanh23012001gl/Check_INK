import { FilmBorder } from '../model/model_film_border.js'; 
import * as draw from "../utills/draw.js";
export class BorderFilmInspector {
    static NAME = "BorderFilmInspector"
    
    constructor() {
        // Quản lý danh sách các đường kiểm định biên (Border Lines)
        this.lines = [];
        this.polygons = []; // Danh sách các điểm polygon
        this.line_current = null;
    }
    
    clearAll() {
            this.line_current = null;
            this.lines = [];
            this.polygons = [];
            return { status: true, message: "Đã xóa toàn bộ dữ liệu thành công." };
    }

    getPolygons() {
        return this.polygons;
    }
    
    setPolygons(polygons) {
        this.polygons = Array.isArray(polygons) ? polygons : [];
    }

    /**
     * Thêm một đối tượng đường biên vào danh sách
     * Nếu trùng id_line thì sẽ ghi đè phần tử cũ
     * @param {FilmBorder} lineModel 
     */
    addLine(lineModel) {
        if (!(lineModel instanceof FilmBorder)) {
            console.error("Đối tượng thêm vào không phải là Instance của FilmBorder");
            return false;
        }
        // Kiểm tra xem id_line đã tồn tại chưa
        const index = this.lines.findIndex(item => item.id_line === lineModel.id_line);
        if (index !== -1) {
            // Nếu đã tồn tại, tiến hành cập nhật/ghi đè
            this.lines[index] = lineModel;
        } else {
            // Nếu chưa, thêm mới vào mảng
            this.lines.push(lineModel);
        }
        return true;
    }

    /**
     * Tìm kiếm xem tọa độ click (px, py) có nằm trên đoạn thẳng hoặc gần 2 đầu mút hay không
     * Ưu tiên đường vẽ sau cùng (layer trên cùng)
     * @param {number} px - Tọa độ X khi click
     * @param {number} py - Tọa độ Y khi click
     * @param {number} [tolerance=10] - Sai số cho phép (pixel)
     * @returns {FilmBorder|null}
     */
    findClickedLine(px, py, tolerance = 10) {
        if (!Array.isArray(this.lines) || this.lines.length === 0) {
            return null;
        }

        const clickX = Number(px);
        const clickY = Number(py);

        // Vòng lặp ngược để ưu tiên layer trên cùng
        for (let i = this.lines.length - 1; i >= 0; i--) {
            const line = this.lines[i];
            
            const xStart = Number(line.xStart);
            const yStart = Number(line.yStart);
            const xEnd = Number(line.xEnd);
            const yEnd = Number(line.yEnd);

            if (Number.isNaN(xStart) || Number.isNaN(yStart) || Number.isNaN(xEnd) || Number.isNaN(yEnd)) {
                continue;
            }

            // --- Kiểm tra click gần Điểm Đầu (xStart, yStart) ---
            const distToStart = Math.hypot(clickX - xStart, clickY - yStart);
            if (distToStart <= tolerance) {
                return line;
            }

            // --- Kiểm tra click gần Điểm Cuối (xEnd, yEnd) ---
            const distToEnd = Math.hypot(clickX - xEnd, clickY - yEnd);
            if (distToEnd <= tolerance) {
                return line;
            }
            
            // --- Kiểm tra va chạm với phần thân đoạn thẳng ---
            const isHitLine = draw.isPointOnLineSegment(
                xStart, yStart, 
                xEnd, yEnd, 
                clickX, clickY, 
                tolerance
            );
            
            if (isHitLine) {
                return line; 
            }
        }
        
        return null;
    }

    /**
     * Lấy ra một line dựa vào id_line
     * @param {string|number} id_line 
     * @returns {FilmBorder|undefined}
     */
    getLine(id_line) {
        return this.lines.find(item => item.id_line === id_line);
    }

    /**
     * Xóa một line khỏi danh sách bằng id_line
     * @param {string|number} id_line 
     * @returns {boolean} true nếu xóa thành công, false nếu không tìm thấy
     */
    removeLine(id_line) {
        const index = this.lines.findIndex(item => item.id_line === id_line);
        if (index !== -1) {
            this.lines.splice(index, 1); // Xóa 1 phần tử tại vị trí index
            return true;
        }
        return false;
    }

    /**
     * Trả về toàn bộ mảng danh sách các đường thẳng
     * @returns {FilmBorder[]}
     */
    getAllLines() {
        return this.lines;
    }

    /**
     * Kiểm tra toàn bộ các đường thẳng trong danh sách xem có hợp lệ không
     * @returns {{isValid: boolean, allErrors: Object}}
     */
    validateAll() {
        const report = { isValid: true, allErrors: {} };

        this.lines.forEach(lineInstance => {
            // Đã cập nhật theo tên hàm mới của FilmBorder
            const validation = lineInstance.validateBorderWidths(); 
            if (!validation.isValid) {
                report.isValid = false;
                // Gom lỗi theo id_line
                report.allErrors[lineInstance.id_line] = validation.errors;
            }
        });

        return report;
    }

    /**
     * Xuất mảng hiện tại thành cấu trúc Object Dict tổng hợp
     * @returns {Object} { id1: {data1}, id2: {data2} }
     */
    toDict() {
        const fullDict = {};
        this.lines.forEach(lineInstance => {
            Object.assign(fullDict, lineInstance.toDict());
        });
        return fullDict;
    }

    /**
     * Nạp dữ liệu hàng loạt từ một Object Dict tổng hợp vào mảng
     * @param {Object} fullDict - Dữ liệu đầu vào dạng { id1: {data1}, id2: {data2} }
     */
    fromDict(fullDict) {
        if (!fullDict || typeof fullDict !== 'object') return;

        // Reset lại danh sách cũ
        this.lines = [];

        Object.keys(fullDict).forEach(id_line => {
            const singleLineDict = { [id_line]: fullDict[id_line] };
            // Đã đổi sang FilmBorder.fromDict
            const lineInstance = FilmBorder.fromDict(singleLineDict);
            
            if (lineInstance) {
                this.lines.push(lineInstance);
            }
        });
    }

    /**
     * Tạo ID tiếp theo cho đường thẳng vẽ mới
     * @returns {number}
     */
    generateNextId() {
        if (!Array.isArray(this.lines) || this.lines.length === 0) {
            return 0;
        }
        const currentIds = this.lines.map(item => Number(item.id_line));
        const validIds = currentIds.filter(id => !Number.isNaN(id));
        if (validIds.length === 0) {
            return 0;
        }
        const maxId = Math.max(...validIds);
        return maxId + 1;
    }

    /**
     * Vẽ toàn bộ các đường biên lên canvas dựa trên cấu trúc canvasManager
     * @param {Object} canvasManager - Đối tượng quản lý canvas
     * @param {string} [color="#FFE680"] - Màu sắc của nét vẽ và chữ
     * @param {number} [fontSize=14] - Kích thước chữ hiển thị tên đường
     */
    drawAll(canvasManager, color = "#FFE680", fontSize = 14) {
        if (this.lines.length === 0) {
            canvasManager.clearShapeCanvas();
            return;
        }

        canvasManager.clearShapeCanvas();

        this.lines.forEach((lineInstance) => {
            const { xStart, yStart, xEnd, yEnd, nameLine } = lineInstance;

            if (
                xStart === undefined || yStart === undefined || 
                xEnd === undefined || yEnd === undefined
            ) {
                console.error("Đường thẳng thiếu tọa độ, bỏ qua:", lineInstance);
                return;
            }

            this.line_current = {
                xStart: Number(xStart),
                yStart: Number(yStart),
                xEnd: Number(xEnd),
                yEnd: Number(yEnd)
            };

            this.#renderSingleLineWorkflow(
                canvasManager, 
                nameLine || "", 
                color, 
                fontSize
            );
        });
    }

    /**
     * Quy trình vẽ chi tiết cho một đường thẳng và text xoay theo đường thẳng đó (Private)
     */
    #renderSingleLineWorkflow(canvasManager, text, color, fontSize = 14) {
        const ctx = canvasManager.ctxShape;
        const { xStart, yStart, xEnd, yEnd } = this.line_current;

        ctx.save();
        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        
        draw.drawPoint(ctx, xStart, yStart);
        draw.drawPoint(ctx, xEnd, yEnd);
        draw.drawTransparentLine(ctx, xStart, yStart, xEnd, yEnd);
        ctx.restore();

        const midX = (xStart + xEnd) / 2;
        const midY = (yStart + yEnd) / 2;
        let angle = Math.atan2(yEnd - yStart, xEnd - xStart);

        if (angle > Math.PI / 2) {
            angle -= Math.PI;
        } else if (angle < -Math.PI / 2) {
            angle += Math.PI;
        }

        ctx.save();
        ctx.translate(midX, midY);
        ctx.rotate(angle);
        ctx.font = `bold ${fontSize}px Arial`;
        ctx.fillStyle = color;
        ctx.textAlign = "center";
        ctx.textBaseline = "bottom"; 
        ctx.fillText(text, 0, -2); 
        ctx.restore();
    }
    
    /**
     * Tìm đường thẳng dựa trên tọa độ chính xác (có sai số tolerance nhỏ)
     */
    findLineByCoordinate(xStart, yStart, xEnd, yEnd, tolerance = 0.5) {
        for (let i = this.lines.length - 1; i >= 0; i--) {
            const measurement = this.lines[i];
            if (!measurement) continue;

            const matchStart = Math.abs(Number(measurement.xStart) - Number(xStart)) <= tolerance;
            const matchYStart = Math.abs(Number(measurement.yStart) - Number(yStart)) <= tolerance;
            const matchXEnd = Math.abs(Number(measurement.xEnd) - Number(xEnd)) <= tolerance;
            const matchYEnd = Math.abs(Number(measurement.yEnd) - Number(yEnd)) <= tolerance;

            if (matchStart && matchYStart && matchXEnd && matchYEnd) {
                return { status: true, data: measurement };
            }
        }

        return {
            status: false,
            data: this.generateNextId()
        };
    }

    /**
     * Vẽ các vùng đa giác (Polygons) vùng loại trừ / vùng kiểm tra
     */
    drawPolygons(canvasManager, polygons, imageWidth, displayWidth, color = "#00FF00", lineWidth = 2) {
        if (!Array.isArray(polygons)) return;
        // Nếu dữ liệu là [[[x,y]], [[x,y]], ...]
        if (
            polygons.length > 0 &&
            polygons[0].length === 1 &&
            polygons[0][0].length === 2
        ) {
            polygons = [polygons.map(p => p[0])];
        }

        const ctx = canvasManager.ctxShape;
        const scale = displayWidth / imageWidth;

        ctx.save();
        ctx.strokeStyle = color;
        ctx.lineWidth = lineWidth;

        polygons.forEach(polygon => {

            if (polygon.length < 2) return;

            ctx.beginPath();

            polygon.forEach(([x, y], index) => {
                x *= scale;
                y *= scale;

                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });

            ctx.closePath();
            ctx.stroke();
        });

        ctx.restore();
    }
}