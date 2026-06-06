import * as draw from "../utills/draw.js";

const NUMBER_OF_POINTS_ON_A_ATRAIGHT_LINE =  2 ;
const DISTANCE_DEFINE_IS_POINT_IN_LINE_SEGMENT = 20;


export class DimesionalCalibrationDraw {
    constructor() {
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
        
    }
    
    draw_defined_line_segment(canvasManager){
        if (this.isLineDefined()){
            this.isDrawing = false;
            this.start = {
                x: -1,
                y: -1
            };
            console.log(this.defined_line_segment.xStart,
                                                            this.defined_line_segment.yStart,
                                                            this.defined_line_segment.xEnd,
                                                            this.defined_line_segment.yEnd)
            canvasManager.clearShapeCanvas();
                // Vẽ điểm đầu
            draw.drawPoint(
                canvasManager.ctxShape,
                this.defined_line_segment.xStart,
                this.defined_line_segment.yStart
            );

            // Vẽ điểm cuối
            draw.drawPoint(
                canvasManager.ctxShape,
                this.defined_line_segment.xEnd,
                this.defined_line_segment.yEnd
            );
            draw.drawTransparentLine(canvasManager.ctxShape,this.defined_line_segment.xStart,
                                                            this.defined_line_segment.yStart,
                                                            this.defined_line_segment.xEnd,
                                                            this.defined_line_segment.yEnd);
    }
    }

    onClick(pos, canvasManager) {
        if (this.isLineDefined()){
            return;
        }
        console.log(
            "[Dimetional Calibration] Click:",
            pos.x,
            pos.y
        );
        
        this.cout_click++;
            let status_check_point_in_line = draw.isPointOnLineSegment(this.defined_line_segment.xStart,
                                                                        this.defined_line_segment.yStart,
                                                                        this.defined_line_segment.xEnd,
                                                                        this.defined_line_segment.yEnd,pos.x,pos.y,
                                                                        DISTANCE_DEFINE_IS_POINT_IN_LINE_SEGMENT);

           console.log("status_check_point_in_line",status_check_point_in_line);
           if (status_check_point_in_line){
                this.cout_click--;
                console.log("Bạn đã click vào line vừa vẽ");
                return;
           }
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
                // reset 
                this.isDrawing = false;
                this.cout_click = 0;
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
                this.reset() 
                canvasManager.clearShapeCanvas();
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


}