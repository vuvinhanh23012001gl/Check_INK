import { ModelSlit } from '../model/model_slit.js'; // Thay đổi đường dẫn cho đúng với dự án của bạn
import * as draw from "../utills/draw.js";
export class SlitItemInspector {
    static NAME = "SlitWeldInspector"
    constructor() {
        // Sử dụng Mảng (List) để quản lý danh sách các ModelSlit
        this.slits = [];
        this.polygons = []; //danh sach cac diem polygon
    }
          
    clearAll() {
            this.slits = [];
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
     * Thêm một đối tượng ModelSlit vào danh sách
     * Nếu trùng id_line thì sẽ ghi đè phần tử cũ
     * @param {ModelSlit} modelSlit 
     */

    addSlit(modelSlit) {
        if (!(modelSlit instanceof ModelSlit)) {
            console.error("Đối tượng thêm vào không phải là Instance của ModelSlit");
            return false;
        }
        // Kiểm tra xem id_line đã tồn tại chưa
        const index = this.slits.findIndex(item => item.id_line === modelSlit.id_line);
        if (index !== -1) {
            // Nếu đã tồn tại, tiến hành cập nhật/ghi đè
            this.slits[index] = modelSlit;
        } else {
            // Nếu chưa, thêm mới vào mảng
            this.slits.push(modelSlit);
        }
        return true;
    }

    /**
     * Tìm kiếm xem tọa độ click (px, py) có nằm trên đoạn thẳng nào không (Ưu tiên đường vẽ sau cùng)
     * @param {number} px - Tọa độ X khi click
     * @param {number} py - Tọa độ Y khi click
     * @param {number} [tolerance=10] - Sai số cho phép (pixel)
     * @returns {ModelSlit|null}
     */

    /**
     * Tìm kiếm xem tọa độ click (px, py) có nằm trên đoạn thẳng nào không (Ưu tiên đường vẽ sau cùng)
     * @param {number} px - Tọa độ X khi click
     * @param {number} py - Tọa độ Y khi click
     * @param {number} [tolerance=10] - Sai số cho phép (pixel)
     * @returns {ModelSlit|null}
     */
    /**
     * Tìm kiếm xem tọa độ click (px, py) có nằm trên đoạn thẳng hoặc gần 2 đầu mút hay không
     * @param {number} px - Tọa độ X khi click
     * @param {number} py - Tọa độ Y khi click
     * @param {number} [tolerance=10] - Sai số cho phép (pixel)
     * @returns {ModelSlit|null}
     */
    findClickedLine(px, py, tolerance = 10) {
        if (!Array.isArray(this.slits) || this.slits.length === 0) {
            return null;
        }

        const clickX = Number(px);
        const clickY = Number(py);

        // Vòng lặp ngược để ưu tiên layer trên cùng
        for (let i = this.slits.length - 1; i >= 0; i--) {
            const line = this.slits[i];
            
            const xStart = Number(line.xStart);
            const yStart = Number(line.yStart);
            const xEnd = Number(line.xEnd);
            const yEnd = Number(line.yEnd);

            if (Number.isNaN(xStart) || Number.isNaN(yStart) || Number.isNaN(xEnd) || Number.isNaN(yEnd)) {
                continue;
            }

            // --- BỔ SUNG: Kiểm tra click gần Điểm Đầu (xStart, yStart) ---
            const distToStart = Math.hypot(clickX - xStart, clickY - yStart);
            if (distToStart <= tolerance) {
                return line; // Trúng điểm đầu, trả về luôn
            }

            // --- BỔ SUNG: Kiểm tra click gần Điểm Cuối (xEnd, yEnd) ---
            const distToEnd = Math.hypot(clickX - xEnd, clickY - yEnd);
            if (distToEnd <= tolerance) {
                return line; // Trúng điểm cuối, trả về luôn
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
     * Lấy ra một ModelSlit dựa vào id_line
     * @param {string|number} id_line 
     * @returns {ModelSlit|undefined}
     */
    getSlit(id_line) {
        return this.slits.find(item => item.id_line === id_line);
    }

    /**
     * Xóa một ModelSlit khỏi danh sách bằng id_line
     * @param {string|number} id_line 
     * @returns {boolean} true nếu xóa thành công, false nếu không tìm thấy
     */
    removeSlit(id_line) {
        const index = this.slits.findIndex(item => item.id_line === id_line);
        if (index !== -1) {
            this.slits.splice(index, 1); // Xóa 1 phần tử tại vị trí index
            return true;
        }
        return false;
    }

    /**
     * Trả về toàn bộ mảng danh sách
     * @returns {ModelSlit[]}
     */
    getAllSlits() {
        return this.slits;
    }

    /**
     * Kiểm tra toàn bộ các phần tử trong danh sách xem có hợp lệ không
     * @returns {{isValid: boolean, allErrors: Object}}
     */
    validateAll() {
        const report = { isValid: true, allErrors: {} };

        this.slits.forEach(slitInstance => {
            const validation = slitInstance.validateSlitLevelsIncreasing();
            if (!validation.isValid) {
                report.isValid = false;
                // Gom lỗi theo id_line
                report.allErrors[slitInstance.id_line] = validation.errors;
            }
        });

        return report;
    }

    /**
     * Xuất mảng hiện tại thành cấu trúc Object Dict tổng hợp giống như yêu cầu của ModelSlit
     * @returns {Object} { id1: {data1}, id2: {data2} }
     */
    toDict() {
        const fullDict = {};
        this.slits.forEach(slitInstance => {
            Object.assign(fullDict, slitInstance.toDict());
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
        this.slits = [];

        Object.keys(fullDict).forEach(id_line => {
            const singleSlitDict = { [id_line]: fullDict[id_line] };
            const slitInstance = ModelSlit.fromDict(singleSlitDict);
            
            if (slitInstance) {
                this.slits.push(slitInstance);
            }
        });
    }

    /**
     * Vẽ toàn bộ các đường khe hở (slits) lên canvas dựa trên cấu trúc canvasManager
     * @param {Object} canvasManager - Đối tượng quản lý canvas
     * @param {string} [color="#FFE680"] - Màu sắc của nét vẽ và chữ
     * @param {number} [fontSize=14] - Kích thước chữ hiển thị tên đường
     */
    drawAllSlits(canvasManager, color = "#FFE680", fontSize = 14) {
        // 1. Kiểm tra danh sách slits hiện tại
        if (this.slits.length === 0) {
            canvasManager.clearShapeCanvas(); // Không có line nào thì xóa sạch canvas
            return;
        }

        // 2. Xóa canvas trước khi vẽ mới hoàn toàn
        canvasManager.clearShapeCanvas();

        // 3. Lặp qua từng instance ModelSlit trong mảng slits để vẽ
        this.slits.forEach((slitInstance) => {
            const { xStart, yStart, xEnd, yEnd, nameLine } = slitInstance;

            // Kiểm tra tọa độ hợp lệ (giống logic bài cũ của bạn)
            if (
                xStart === undefined || yStart === undefined || 
                xEnd === undefined || yEnd === undefined
            ) {
                console.error("Đường thẳng thiếu tọa độ, bỏ qua:", slitInstance);
                return;
            }

            // Gán dữ liệu tọa độ được ép kiểu Number vào thuộc tính tạm (nếu cần dùng ở luồng khác)
            this.line_current = {
                xStart: Number(xStart),
                yStart: Number(yStart),
                xEnd: Number(xEnd),
                yEnd: Number(yEnd)
            };

            // Gọi hàm render chi tiết cho từng đường slit
            this.#renderSingleSlitWorkflow(
                canvasManager, 
                nameLine || "", 
                color, 
                fontSize
            );
        });
    }
    generateNextId() {
        if (!Array.isArray(this.slits) || this.slits.length === 0) {
            return 0;
        }
        const currentIds = this.slits.map(item => Number(item.id_line));
        const validIds = currentIds.filter(id => !Number.isNaN(id));
        if (validIds.length === 0) {
            return 0;
        }
        const maxId = Math.max(...validIds);
        return maxId + 1;
    }

    /**
     * Quy trình vẽ chi tiết cho một đường thẳng và text xoay theo đường thẳng đó
     */
    #renderSingleSlitWorkflow(canvasManager, text, color, fontSize = 14) {
        const ctx = canvasManager.ctxShape;
        const { xStart, yStart, xEnd, yEnd } = this.line_current;

        // --- 1. Tiến hành vẽ 2 điểm mút và đường thẳng ---
        ctx.save();
        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        
        // Sử dụng lại thư viện draw của bạn
        draw.drawPoint(ctx, xStart, yStart);
        draw.drawPoint(ctx, xEnd, yEnd);
        draw.drawTransparentLine(ctx, xStart, yStart, xEnd, yEnd);
        ctx.restore();

        // --- 2. Tính toán trung điểm và góc để vẽ Text ---
        const midX = (xStart + xEnd) / 2;
        const midY = (yStart + yEnd) / 2;
        let angle = Math.atan2(yEnd - yStart, xEnd - xStart);

        // Đảo góc chữ nếu góc quay quá lớn để chữ không bị ngược/cắm đầu xuống đất
        if (angle > Math.PI / 2) {
            angle -= Math.PI;
        } else if (angle < -Math.PI / 2) {
            angle += Math.PI;
        }

        // --- 3. Tiến hành render chữ song song với line ---
        ctx.save();
        ctx.translate(midX, midY);
        ctx.rotate(angle);
        ctx.font = `bold ${fontSize}px Arial`;
        ctx.fillStyle = color;
        ctx.textAlign = "center";
        ctx.textBaseline = "bottom"; 
        ctx.fillText(text, 0, -2); // Cách đường line 2px lên phía trên
        ctx.restore();
    }
    
    findLineByCoordinate(xStart, yStart, xEnd, yEnd, tolerance = 0.5) {
        // Vòng lặp ngược để ưu tiên phần tử vẽ sau cùng (ở trên cùng)
        for (let i = this.slits.length - 1; i >= 0; i--) {
            const measurement = this.slits[i];
            if (!measurement) continue;

            // Tính độ lệch tuyệt đối giữa các tọa độ (đã ép kiểu Number)
            const matchStart = Math.abs(Number(measurement.xStart) - Number(xStart)) <= tolerance;
            const matchEnd = Math.abs(Number(measurement.yStart) - Number(yStart)) <= tolerance;
            const matchXEnd = Math.abs(Number(measurement.xEnd) - Number(xEnd)) <= tolerance;
            const matchYEnd = Math.abs(Number(measurement.yEnd) - Number(yEnd)) <= tolerance;

            if (matchStart && matchEnd && matchXEnd && matchYEnd) {
                return { status: true, data: measurement };
            }
        }

        return {
            status: false,
            data: this.generateNextId() // Hoặc generateLineId() tùy dự án của bạn
        };
    }
    drawPolygons(canvasManager, polygons, imageWidth, displayWidth, color = "#00FF00", lineWidth = 2) {
            if (!Array.isArray(polygons)) return;

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
                    index === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
                });

                ctx.closePath();
                ctx.stroke();
            });

            ctx.restore();
        }

}