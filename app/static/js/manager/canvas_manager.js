export class CanvasManager {

    constructor(coordinate,
        wrapCanvasId,video_product,
        width = 1280,
        height = 960
    ) {

        this.width = width;
        this.height = height;

        this.currentTool = null;

        this.cImg = document.getElementById("canvasImage");
        this.ctxImg = this.cImg.getContext("2d");

        this.cShape = document.getElementById("canvasShape");
        this.ctxShape = this.cShape.getContext("2d");

        this.cPrev = document.getElementById("canvasPreview");
        this.ctxPrev = this.cPrev.getContext("2d");

        this.coordinate = document.getElementById(coordinate);;
        this.wrapCanvas =  document.getElementById(wrapCanvasId);
        this.video_product = video_product;
    }

    setTool(tool){
        this.currentTool = tool;
    } 

    initEvent(){
        this.cPrev.addEventListener("click",this.handleCanvasClick.bind(this));
        this.cPrev.addEventListener("mousemove", this.handleMouseMove.bind(this));
        this.cPrev.addEventListener("dblclick", this.handleCanvasDoubleClick.bind(this));
        this.cPrev.addEventListener("mousedown",this.handleMouseDown.bind(this));
        this.cPrev.addEventListener("mouseup",this.handleMouseUp.bind(this));
        this.cPrev.addEventListener("contextmenu",this.handleRightClick.bind(this));

    }

    show_img_items(img){
        this.video_product.style.display = "none";
        this.setWrapCanvasVisible(true);
        this.clearAllCanvas();
        this.resizeAllCanvas();
        this.drawImageContain(this.ctxImg,this.cImg,img);
    }

    handleRightClick(event){
        event.preventDefault();
        const pos =this.getMousePosition( this.cPrev,event);
        this.currentTool?.onMouseRightClick(
            pos,
            this
        );
    }
    handleMouseUp(event){
        const pos =this.getMousePosition( this.cPrev,event);
        this.currentTool?.onMouseUp(
            pos,
            this
        );
    }
    handleCanvasClick(event){
        const pos  =this.getMousePosition(this.cPrev, event);
        this.currentTool?.onClick(pos,this);
            
        
    }
    handleMouseMove(event){
            const pos =
                this.getMousePosition(
                    this.cPrev,
                    event
                );

            this.coordinate.innerHTML =
                `Pixel: ${pos.x}, ${pos.y}`;

            this.currentTool?.onMouseMove(
                pos,
                this
            );
    }
    handleCanvasDoubleClick(event){
            const pos =
            this.getMousePosition(
                this.cPrev,
                event
            );
            this.currentTool?.onDoubleClick(
                pos,
                this
            );
    }

    handleMouseDown(event){
            const pos =
                this.getMousePosition(
                    this.cPrev,
                    event
                );

            this.currentTool?.onMouseDown(
                pos,
                this
            );
    }

    resizeAllCanvas() {
        this.wrapCanvas.style.width =
            this.width + "px";
        this.wrapCanvas.style.height =
            this.height + "px";
        const rect =
            this.wrapCanvas.getBoundingClientRect();
        const dpr = 1;
        [this.cImg, this.cShape, this.cPrev]
        .forEach(canvas => {
            canvas.width =
                Math.round(rect.width * dpr);
            canvas.height =
                Math.round(rect.height * dpr);
            canvas.style.width =
                rect.width + "px";
            canvas.style.height =
                rect.height + "px";
            canvas.getContext("2d")
                .setTransform(
                    dpr, 0, 0,
                    dpr, 0, 0
                );
        });
    }

    clearAllCanvas() {
        this.ctxImg.clearRect(
            0, 0,
            this.cImg.width,
            this.cImg.height
        );
        this.ctxShape.clearRect(
            0, 0,
            this.cShape.width,
            this.cShape.height
        );
        this.ctxPrev.clearRect(
            0, 0,
            this.cPrev.width,
            this.cPrev.height
        );
    }
    
    setWrapCanvasVisible(isVisible) {
        this.wrapCanvas.style.display =
            isVisible ? "block" : "none";
    }


    drawImageContain(ctx, canvas, img) {
        const cw = canvas.width;
        const ch = canvas.height;
        const iw = img.naturalWidth;
        const ih = img.naturalHeight;
        if (!iw || !ih) {
            console.warn("Image chưa load xong!");
            return;
        }
        const scale =
            Math.min(cw / iw, ch / ih);
        const nw = iw * scale;
        const nh = ih * scale;
        const dx = (cw - nw) / 2;
        const dy = (ch - nh) / 2;
        ctx.clearRect(0, 0, cw, ch);
        ctx.drawImage(
            img,
            dx,
            dy,
            nw,
            nh
        );
    }

    getMousePosition(canvas, event) {
        const rect =
            canvas.getBoundingClientRect();
        const scaleX =
            canvas.width / rect.width;
        const scaleY =
            canvas.height / rect.height;

        let x =
            Math.floor(event.offsetX * scaleX);

        let y =
            Math.floor(event.offsetY * scaleY);

        x = Math.max(
            0,
            Math.min(x, this.width)
        );

        y = Math.max(
            0,
            Math.min(y, this.height)
        );
        return { x, y };
    }
    clearImageCanvas() {
    this.ctxImg.clearRect(
        0,
        0,
        this.cImg.width,
        this.cImg.height
        );
    }

    clearShapeCanvas() {
        this.ctxShape.clearRect(
            0,
            0,
            this.cShape.width,
            this.cShape.height
        );
    }

    clearPreviewCanvas() {
        this.ctxPrev.clearRect(
            0,
            0,
            this.cPrev.width,
            this.cPrev.height
        );
    }


}