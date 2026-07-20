export class ModelRectangle {
    constructor(id = -1, name = "", xStart = -1, yStart = -1, xEnd = -1, yEnd = -1) {
    

        this.id = id;
        this.name = name;
        this.xStart = xStart;
        this.yStart = yStart;
        this.xEnd = xEnd;
        this.yEnd = yEnd;
        this.width = Math.abs(xEnd - xStart);
        this.height = Math.abs(yEnd - yStart);
    }

    updatePosition(xStart, yStart, xEnd, yEnd) {
        this.xStart = xStart;
        this.yStart = yStart;
        this.xEnd = xEnd;
        this.yEnd = yEnd;
        this.width = Math.abs(xEnd - xStart);
        this.height = Math.abs(yEnd - yStart);
    }

    toJSON() {
        return {
            id: this.id,
            name: this.name,
            xStart: this.xStart,
            yStart: this.yStart,
            xEnd: this.xEnd,
            yEnd: this.yEnd,
            width: this.width,
            height: this.height
        };
    }

    static fromJSON(data) {
        return new ModelRectangle(
            data.id,
            data.name,
            data.xStart,
            data.yStart,
            data.xEnd,
            data.yEnd
        );
    }
    validate() {
    const errors = [];

    if (!this.name || this.name.trim() === "") {
        errors.push({
            field: "name",
            rowName: "Tên hình",
            currentVal: this.name,
            expected: "Không được để trống"
        });
    }
    return {
        isValid: errors.length === 0,
        errors
    };
}
}