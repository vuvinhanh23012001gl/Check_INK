import { Measurement } from "../model/model_measurement.js";
import * as draw from "../utills/draw.js";

export class MeasurementItemsInspector {
    constructor() {
        this.arr_measure = [];
        this.polygons = []; //danh sach cac diem polygon
    }
    static fromDict(data) {
        const manager = new MeasurementItemsInspector();
        for (const [lineId, value] of Object.entries(data)) {
            const measurement = Measurement.fromDict(lineId, value);
            manager.arr_measure.push(measurement);
        }
        return manager;
    }
    
    getPolygons() {
        return this.polygons;
    }
    setPolygons(polygons) {
        this.polygons = Array.isArray(polygons) ? polygons : [];
    }

    getMeasurementByLineId(lineId) {
        return this.arr_measure.find(
            measure => measure.lineId === lineId
        ) || null;
    }
    addMeasurement(measurement) {
        if (!(measurement instanceof Measurement)) {
            throw new Error("measurement phải là instance của Measurement");
        }
        const checkExist = this.findLineByCoordinate(
            measurement.xStart, 
            measurement.yStart, 
            measurement.xEnd, 
            measurement.yEnd
        );
        if (checkExist.status) {
            console.warn("Đoạn thẳng có tọa độ này đã tồn tại, không thể add thêm!");
            return { status: false, message: "Duplicate coordinates found" };
        }
        this.arr_measure.push(measurement);
        return { status: true, message: "Measurement added successfully" };
    }

    toDict() {
        const combinedDict = this.arr_measure.reduce((acc, m) => {
            return { ...acc, ...m.toDict() };
        }, {});
        return combinedDict
    }

    generateLineId() {
        const allIds = [];
        for (const measurement of this.arr_measure) {
            if (measurement && measurement.lineId !== undefined) {
                allIds.push(Number(measurement.lineId));
            }
        }
        return allIds.length ? Math.max(...allIds) + 1 : 0;
    }
    
    getAllLineIds() {
        // lấy danh sách các id
        return this.arr_measure
            .filter(m => m && m.lineId !== undefined)
            .map(m => Number(m.lineId));
    }

    findLineByCoordinate(xStart, yStart, xEnd, yEnd) {
        for (const measurement of this.arr_measure) {
            if (measurement) {
                if (
                    measurement.xStart === xStart &&
                    measurement.yStart === yStart &&
                    measurement.xEnd === xEnd &&
                    measurement.yEnd === yEnd
                ) {
                    return {
                        status: true,
                        data: measurement
                    };
                }
            }
        }
        return {
            status: false,
            data: this.generateLineId()
        };
    }


    updateLineById(id, line_current) {
        let measurementToUpdate = null;

        for (const measurement of this.arr_measure) {
            if (measurement && Number(measurement.lineId) === Number(id)) {
                measurementToUpdate = measurement;
                break; 
            }
        }

        if (!measurementToUpdate) {
            return {
                status: false,
                message: "Line not found or no measurements available",
                data: this.generateLineId()
            };
        }

        measurementToUpdate.xStart = Number(line_current?.xStart ?? 0);
        measurementToUpdate.yStart = Number(line_current?.yStart ?? 0);
        measurementToUpdate.xEnd = Number(line_current?.xEnd ?? 0);
        measurementToUpdate.yEnd = Number(line_current?.yEnd ?? 0);

        if (line_current?.name_line !== undefined) {
            measurementToUpdate.nameLine = line_current.name_line;
        }

        if (line_current?.level1 !== undefined) measurementToUpdate.level1 = Number(line_current.level1);
        if (line_current?.level2 !== undefined) measurementToUpdate.level2 = Number(line_current.level2);
        if (line_current?.level3 !== undefined) measurementToUpdate.level3 = Number(line_current.level3);
        if (line_current?.level4 !== undefined) measurementToUpdate.level4 = Number(line_current.level4);
        if (line_current?.level5 !== undefined) measurementToUpdate.level5 = Number(line_current.level5);

        return {
            status: true,
            data: {
                id: Number(measurementToUpdate.lineId),
                name_line: measurementToUpdate.nameLine,
                ...measurementToUpdate
            }
        };
    }

    getAllDictLine(){
        let arr_line = [];
        for (let object_line of this.arr_measure){
            arr_line.push(object_line.toDictForDraw());
        }
        return arr_line
    }


    
    findClickedLine(px, py, tolerance = 10) {
            const linesArray = this.getAllDictLine();
            for (let i = linesArray.length - 1; i >= 0; i--) {
                const line = linesArray[i];
                const isHit = draw.isPointOnLineSegment(
                    Number(line.xStart), Number(line.yStart), 
                    Number(line.xEnd), Number(line.yEnd), 
                    px, py, tolerance
                );
                if (isHit) return line;
            }
            return null;
    }

    draw_multiple_lines(canvasManager, color = "#FFE680",font_size = 5) {
            const linesArray = this.getAllDictLine();
            if (linesArray.length === 0) {
                canvasManager.clearShapeCanvas(); // Không có line nào thì xóa sạch canvas
                return;
            }
            canvasManager.clearShapeCanvas();
            linesArray.forEach((lineData) => {
                if (
                    lineData.xStart === undefined || 
                    lineData.yStart === undefined || 
                    lineData.xEnd === undefined || 
                    lineData.yEnd === undefined
                ) {
                    console.error("Đường thẳng thiếu tọa độ, bỏ qua:", lineData);
                    return;
                }
                this.line_current = {
                    xStart: Number(lineData.xStart),
                    yStart: Number(lineData.yStart),
                    xEnd: Number(lineData.xEnd),
                    yEnd: Number(lineData.yEnd)
                };
                this.#render_single_line_workflow(canvasManager,lineData.name_line || "",color,font_size);
            });
        }  
        #render_single_line_workflow(canvasManager, text, color, font_size =14) {
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
        
                // Tiến hành render chữ
                ctx.save();
                ctx.translate(midX, midY);
                ctx.rotate(angle);
                ctx.font = `bold ${font_size}px Arial`;
                ctx.fillStyle = color;
                ctx.textAlign = "center";
                ctx.textBaseline = "bottom"; 
                ctx.fillText(text, 0,-2);
                ctx.restore();
    }

    addMeasurementAdvance(measurement) {
            if (!(measurement instanceof Measurement)) {
                throw new Error("measurement phải là instance of Measurement");
            }


            const checkExist = this.findLineByCoordinate(
                measurement.xStart,
                measurement.yStart,
                measurement.xEnd,
                measurement.yEnd
            );

            if (checkExist.status) {
                const existing = checkExist.data;

                const line_current = {
                    xStart: measurement.xStart,
                    yStart: measurement.yStart,
                    xEnd: measurement.xEnd,
                    yEnd: measurement.yEnd,
                    name_line: measurement.nameLine,
                    level1: measurement.level1,
                    level2: measurement.level2,
                    level3: measurement.level3,
                    level4: measurement.level4,
                    level5: measurement.level5
                };

                return this.updateLineById(existing.lineId, line_current);
            }

            this.arr_measure.push(measurement);
            return {
                status: true,
                message: "Measurement added successfully",
                data: measurement
            };
        }
        extendMeasurements(measurements) {
            if (!Array.isArray(measurements)) {
                throw new Error("measurements phải là một mảng.");
            }
            if (!measurements.every(m => m instanceof Measurement)) {
                throw new Error("Tất cả phần tử phải là instance của Measurement.");
            }
            const results = [];
            const existingIds = new Set(this.getAllLineIds());
            for (const measurement of measurements) {
                const id = Number(measurement.lineId);
                if (existingIds.has(id)) {
                    results.push({
                        status: false,
                        message: `LineId ${id} đã tồn tại.`,
                        data: measurement
                    });
                    continue;
                }
                existingIds.add(id);
                results.push(this.addMeasurementAdvance(measurement));
            }
            return {
                status: true,
                message: `Đã xử lý ${measurements.length} Measurement.`,
                data: results
            };
        }

        deleteLineByCoordinateAdvance(xStart, yStart, xEnd, yEnd) {
            const checkExist = this.findLineByCoordinate(xStart, yStart, xEnd, yEnd);
            if (!checkExist.status) {
                return {
                    status: false,
                    message: "Không tìm thấy đoạn thẳng với tọa độ đã cho để xóa."
                };
            }
            const targetId = checkExist.data.lineId;
            const index = this.arr_measure.findIndex(m => m && m.lineId === targetId);
            if (index !== -1) {
                const deletedMeasurement = this.arr_measure.splice(index, 1)[0];
                return {
                    status: true,
                    message: "Xóa đoạn thẳng thành công.",
                    data: deletedMeasurement
                };
            }
            return { status: false, message: "Lỗi không xác định khi xóa." };
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