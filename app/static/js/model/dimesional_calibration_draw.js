import * as draw from "../utills/draw.js";

const NUMBER_OF_POINTS_ON_A_ATRAIGHT_LINE =  2 ;
const DISTANCE_DEFINE_IS_POINT_IN_LINE_SEGMENT = 50;

export class DimesionalCalibrationDraw {
    static NAME_EVENT_WHEN_CLICK_ON_LINE = "EVENT_CLICK_ON_LINE"
    static NAME_EVENT_WHEN_CLICK_RIGHT_MOUSE_BTN = "NAME_EVENT_WHEN_CLICK_RIGHT_MOUSE_BTN"
    static  NAME_EVENT_CHECK_LINE_EXIS = "NAME_EVENT_CHECK_LINE_EXIS"
    constructor() {
        this.callbacks = {}; 
        this.defined_line_segment = {
            xStart:-1,
            yStart:-1,
            xEnd:-1,
            yEnd:-1, 
        };
      
        this.isDrawing = false;
        
        this.cout_click = 0
        this.start = {
            x: -1,
            y: -1
        };
        

        this.has_line_of_frame = false;

         
    }
    on(eventName, callback) {
        //đăng kí sự kiện
        if (!this.callbacks[eventName]) {
            this.callbacks[eventName] = [];
        }

        this.callbacks[eventName].push(callback);
    }

    emit(eventName, data = null) {
        // Khi co su kien thi dán phần này vào
        if (!this.callbacks[eventName]) {
            return;
        }
        this.callbacks[eventName].forEach(callback => {
            callback(data);
        });
    }
    
    draw_defined_line_segment(
        canvasManager,
        text = null,
        color = "#FFE680"
    ) {
        if (!this.isLineDefined()) {
            return;
        }

        this.isDrawing = false;
        this.start = {
            x: -1,
            y: -1
        };

        const ctx = canvasManager.ctxShape;

        const {
            xStart,
            yStart,
            xEnd,
            yEnd
        } = this.defined_line_segment;

        canvasManager.clearShapeCanvas();

        // Vẽ điểm đầu
        draw.drawPoint(
            ctx,
            xStart,
            yStart
        );

        // Vẽ điểm cuối
        draw.drawPoint(
            ctx,
            xEnd,
            yEnd
        );

        // Vẽ line
        draw.drawTransparentLine(
            ctx,
            xStart,
            yStart,
            xEnd,
            yEnd
        );

        // Nếu không có text thì chỉ vẽ line
        if (!text) {
            return;
        }

        const midX = (xStart + xEnd) / 2;
        const midY = (yStart + yEnd) / 2;

        let angle = Math.atan2(
            yEnd - yStart,
            xEnd - xStart
        );

        // Tránh chữ bị ngược
        if (angle > Math.PI / 2 || angle < -Math.PI / 2) {
            angle += Math.PI;
        }

        ctx.save();

        ctx.translate(midX, midY);
        ctx.rotate(angle);

        ctx.font = "16px Arial";
        ctx.fillStyle = color;
        ctx.textAlign = "center";
        ctx.textBaseline = "bottom";

        // Text nằm cách line 8px
        ctx.fillText(text, 0, -8);

        ctx.restore();
    }

    onClick(pos, canvasManager) {
            let status_check_point_in_line = draw.isPointOnLineSegment(this.defined_line_segment.xStart,
                                                                        this.defined_line_segment.yStart,
                                                                        this.defined_line_segment.xEnd,
                                                                        this.defined_line_segment.yEnd,pos.x,pos.y,
                                                                        DISTANCE_DEFINE_IS_POINT_IN_LINE_SEGMENT);

           console.log("CLick On Line",status_check_point_in_line);
           if (status_check_point_in_line){
                this.cout_click--;
                this.emit(
                    DimesionalCalibrationDraw.NAME_EVENT_WHEN_CLICK_ON_LINE,
                    this.defined_line_segment
                );
                return;
           }
        // kiểm tra thuộc line hay chưa
        this.emit(DimesionalCalibrationDraw.NAME_EVENT_CHECK_LINE_EXIS,this.defined_line_segment);
        console.log("Sản phẩm đã tồn tại trong dữ liệu chưa",this.has_line_of_frame); //  this.emit(DimesionalCalibrationDraw.NAME_EVENT_CHECK_LINE_EXIS,this.defined_line_segment); sẽ thay đổi biến này.
        if (this.has_line_of_frame) return;
        
        console.log( "[Dimetional Calibration] Click:",pos.x,pos.y);
        this.cout_click++;
        
        

           if (this.cout_click === 1 ) {
                this.start.x = pos.x;
                this.start.y = pos.y;
                this.isDrawing = true;
                draw.drawPoint(canvasManager.ctxShape, pos.x, pos.y)
            }
            else if (this.cout_click === NUMBER_OF_POINTS_ON_A_ATRAIGHT_LINE) {
                draw.drawPoint(canvasManager.ctxShape, pos.x, pos.y)
                canvasManager.clearPreviewCanvas();
                draw.drawTransparentLine(canvasManager.ctxShape,this.start.x,this.start.y, pos.x,pos.y);
                this.defined_line_segment = {
                        xStart: this.start.x ,
                        yStart: this.start.y,
                        xEnd:pos.x,
                        yEnd:pos.y, 
                };
                this.isDrawing = false;
                this.start = {
                    x: -1,
                    y: -1
                };
              
            }
    }

    isLineDefined() {
        return (
                this.defined_line_segment.xStart !== -1 &&
                this.defined_line_segment.yStart !== -1 &&
                this.defined_line_segment.xEnd !== -1 &&
                this.defined_line_segment.yEnd !== -1
            );
    }
    onDoubleClick(pos, canvasManager) {

        console.log(
            "[Dimetional Calibration] Double Click:",
            pos.x,
            pos.y
        );
    }


    onMouseRightClick(pos, canvasManager){
        console.log(
            "[Dimetional Calibration] Nhấn chuột phải",
            pos.x,
            pos.y
        );
         let status_check_point_in_line = draw.isPointOnLineSegment(this.defined_line_segment.xStart,
                                                                        this.defined_line_segment.yStart,
                                                                        this.defined_line_segment.xEnd,
                                                                        this.defined_line_segment.yEnd,pos.x,pos.y,
                                                                        DISTANCE_DEFINE_IS_POINT_IN_LINE_SEGMENT);
            if (status_check_point_in_line){
                this.reset();
                canvasManager.clearShapeCanvas();
                this.emit(
                    DimesionalCalibrationDraw.NAME_EVENT_WHEN_CLICK_RIGHT_MOUSE_BTN,this.defined_line_segment
                );
            }
        }


                          



    onMouseMove(pos, canvasManager) {
        // console.log(
        //     "[Dimetional Calibration] Mouse Move:",
        //     pos.x,
        //     pos.y
        // );
        if (this.isDrawing){
            canvasManager.clearPreviewCanvas();
            draw.drawTransparentLine(canvasManager.ctxPrev,this.start.x,this.start.y,pos.x,pos.y);
            
        }
    }

    onMouseDown(pos, canvasManager) {

        // this.isDrawing = true;

        // console.log(
        //     "[Dimetional Calibration]Mouse Down:",
        //     pos.x,
        //     pos.y
        // );
    }
    onMouseUp(pos, canvasManager) {

        // this.isDrawing = false;

        // console.log(
        //     "[Dimetional Calibration] Mouse Up:",
        //     pos.x,
        //     pos.y
        // );
    }

    reset() {
        this.isDrawing = false;
        this.cout_click = 0;
        this.start = {
            x: -1,
            y: -1
        };
        this.defined_line_segment = {
            xStart: -1,
            yStart: -1,
            xEnd: -1,
            yEnd: -1
        };
        }
redraw_the_line_with_the_text(
    canvasManager,
    text,
    color = "#00FF00"
) {
    if (!this.isLineDefined()) {
        return;
    }

    const ctx = canvasManager.ctxShape;

    canvasManager.clearShapeCanvas();

    const {
        xStart,
        yStart,
        xEnd,
        yEnd
    } = this.defined_line_segment;

    draw.drawPoint(ctx, xStart, yStart);
    draw.drawPoint(ctx, xEnd, yEnd);

    draw.drawTransparentLine(
        ctx,
        xStart,
        yStart,
        xEnd,
        yEnd
    );

    const midX = (xStart + xEnd) / 2;
    const midY = (yStart + yEnd) / 2;

    let angle = Math.atan2(
        yEnd - yStart,
        xEnd - xStart
    );

    // Đảm bảo chữ không bị ngược
    if (angle > Math.PI / 2 || angle < -Math.PI / 2) {
        angle += Math.PI;
    }

    ctx.save();

    ctx.translate(midX, midY);
    ctx.rotate(angle);

    ctx.font = "16px Arial";
    ctx.fillStyle = color;
    ctx.textAlign = "center";
    ctx.textBaseline = "bottom";

    // -8 là khoảng cách text với line
    ctx.fillText(text, 0, -8);

    ctx.restore();
}
  

}