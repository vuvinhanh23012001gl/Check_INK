import { Frame } from "./model_frame.js";
import { ItemsInspector } from "../services/items_inspector.js";

export class Product {
    constructor(product_id = null) {
        this.product_id = product_id;
        this.arr_frames = [];
    }
    
    addFrame(frame) {
        this.arr_frames.push(frame);
    }

    getFrame(frame_id) {
        return this.arr_frames.find(
            frame => String(frame.frame_id) === String(frame_id)
        );
    }

    toDict() {
        const framesDict = {};
        for (const frame of this.arr_frames) {
            // Bỏ qua các frame rác có ID âm hoặc -1
            if (Number(frame.frame_id) < 0 || String(frame.frame_id) === "-1") {
                continue;
            }
            Object.assign(framesDict, frame.toDict());
        }
        return {
            [this.product_id]: framesDict
        };
    }

    static fromDict(data) {
        if (!data) {
            throw new Error("Dữ liệu Product bị null hoặc undefined");
        }
        if (typeof data !== "object") {
            throw new Error(
                `Dữ liệu Product phải là object, nhận được ${typeof data}`
            );
        }
        const keys = Object.keys(data);
        if (keys.length === 0) {
            throw new Error("Không tìm thấy Product ID");
        }
        const product_id = keys[0];
        const product = new Product(product_id);
        const framesData = data[product_id];
        if (framesData === null || framesData === undefined) {
            throw new Error(
                `Product '${product_id}' không chứa dữ liệu Frame`
            );
        }
        for (const [frame_id, frameData] of Object.entries(framesData)) {
            // try {
                const frame = Frame.fromDict({
                    [frame_id]: frameData
                });
                if (!frame) {
                    throw new Error("Frame trả về null");
                }
                product.addFrame(frame);
            // } catch (err) {
            //     throw new Error(
            //         `Lỗi khi đọc Frame '${frame_id}': ${err.message}`
            //     );
            // }
        }
        return product;
    }
    

    find_item_object_corresponding(frame_id, item_id , type){
        // Chặn không tìm hoặc tạo cho ID âm hoặc -1
        if (Number(frame_id) < 0 || Number(item_id) < 0 || String(frame_id) === "-1" || String(item_id) === "-1") {
            return null;
        }
        let obj_frame_iD = this.getFrame(frame_id);
        if (!obj_frame_iD){
            obj_frame_iD = new Frame(String(frame_id));
            this.addFrame(obj_frame_iD);
        }
        let obj_items_inspector = obj_frame_iD.getItemById(item_id);
        if (!obj_items_inspector){
            obj_items_inspector = new ItemsInspector(String(item_id));
            obj_frame_iD.addItem(obj_items_inspector);
        }
        let obj_type  = obj_items_inspector.getInspector(type);
        if (!obj_type){return null;}
        return obj_type;  // trả về đối tượng inspector tương ứng
    }

    get_item_object(frame_id, item_id){
        // Chặn không tạo Frame/Item cho ID âm hoặc -1
        if (Number(frame_id) < 0 || Number(item_id) < 0 || String(frame_id) === "-1" || String(item_id) === "-1") {
            return null;
        }
        let obj_frame_iD = this.getFrame(frame_id);
        if (!obj_frame_iD){
            obj_frame_iD = new Frame(String(frame_id));
            this.addFrame(obj_frame_iD);
        }
        let obj_items_inspector = obj_frame_iD.getItemById(item_id);
        if (!obj_items_inspector) {
            obj_items_inspector = new ItemsInspector(String(item_id));
            obj_frame_iD.addItem(obj_items_inspector);
        }
        return obj_items_inspector;
    }

    get_item_inspector(frame_id, item_id){
        return this.get_item_object(frame_id, item_id);
    }

    find_line_object_corresponding(frame_id, item_id , type, line_id){
       let obj_type = this.find_item_object_corresponding(frame_id, item_id , type);
       if (!obj_type){console.log("Không tìm thấy type tương ứng");return null};
      //  console.log("obj_type",obj_type);
       let obj_line = obj_type.getMeasurementByLineId(line_id);
      //  console.log("obj_line",obj_line);
       return obj_line;
    }


    getAllInspectors(type) {
        const inspectors = [];
        for (const frame of this.arr_frames) {
            for (const item of frame.arr_items) {
                const objInspector = item.getInspector(type);

                if (objInspector) {
                    inspectors.push({
                        frame_id: frame.frame_id,
                        item_id: item.items_id,
                        inspector: objInspector
                    });
                }
            }
        }
        return inspectors;
    }

    hasInspectorData(inspectors, frame_id, item_id, propertyName) {
        const obj = inspectors.find(
            item => String(item.frame_id) === String(frame_id) && String(item.item_id) === String(item_id)
        );
        if (!obj || !obj.inspector) {
            // console.warn(`[Inspector] Không tìm thấy dữ liệu cho Frame: ${frame_id}, Item: ${item_id}`);
            return false;
        }
        const data = obj.inspector[propertyName];
        if (data === undefined || data === null) {
            console.warn(`[Inspector] Thuộc tính '${propertyName}' không tồn tại trên Item: ${item_id}`);
            return false;
        }
        if (Array.isArray(data)) {
            const isValid = data.length > 0;
            console.log(`[Inspector Check] '${propertyName}' (Array) -> Valid: ${isValid}`);
            return isValid;
        }
        if (typeof data === "object") {
            if (typeof data.isValid === "function") {
                const isValid = data.isValid();
                console.log(`[Inspector Check] '${propertyName}' (isValid()) -> Valid: ${isValid}`);
                return isValid;
            }
            const isValid = Object.keys(data).length > 0;
            console.log(`[Inspector Check] '${propertyName}' (Object) -> Valid: ${isValid}`);
            return isValid;
        }
        console.warn(`[Inspector] Kiểu dữ liệu không hợp lệ cho '${propertyName}':`, typeof data);
        return false;
    }

    highlightItems(container, type, propertyName, className = "active_hightlight") {
        const inspectors = this.getAllInspectors(type);
        console.log("Dữ liệu để chuyển Items màu xanh",inspectors);
        container.querySelectorAll(".box-frame").forEach(frame => {
            const frame_id = frame.dataset.frameId;
            frame.querySelectorAll(".img-item").forEach(item => {
                const item_id = item.dataset.id;
                const text = item.querySelector(".img-text");
                item.classList.remove(className);
                text?.classList.remove(className);
                if (this.hasInspectorData(inspectors, frame_id, item_id, propertyName)) {
                    item.classList.add(className);
                    text?.classList.add(className);
                }
            });
        });
    }

    clearHighlight(container, className = "active_hightlight") {
        if (!container) return;
        container.querySelectorAll(".box-frame").forEach(frame => {
            frame.querySelectorAll(".img-item").forEach(item => {
                const text = item.querySelector(".img-text");
                item.classList.remove(className);
                text?.classList.remove(className);
            });
        });
    }
    clearAllInspectors() {
        for (const frame of this.arr_frames) {
            if (frame && typeof frame.clearAllInspectors === "function") {
                frame.clearAllInspectors();
            }
        }
    }
}
