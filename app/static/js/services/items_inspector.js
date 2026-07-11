import { MeasurementItemsInspector } from "../services/measurement_items_inspector.js";
import { SlitItemInspector } from "./slit_item_inspector.js";
export class ItemsInspector {
    static TYPE_MEASUREMENT = MeasurementItemsInspector.NAME;
    static TYPE_SLIT = SlitItemInspector.NAME;

    constructor(items_id, measurement_items,slit_item) {
        this.items_id = items_id;
    
        this.inspectors = {
            [ItemsInspector.TYPE_MEASUREMENT]: measurement_items ||null,
            [ItemsInspector.TYPE_SLIT]: slit_item || null,
        };

    }

    getInspector(type) {
        return this.inspectors[type] || null;
    }

    getMeasurementItems() {
        return this.getInspector(ItemsInspector.TYPE_MEASUREMENT);
    }

    getSlitItems() {
        return this.getInspector(ItemsInspector.TYPE_SLIT);
    }
 

    toDict() {
        const categoriesDict = {};

        for (const [key, inspectorInstance] of Object.entries(this.inspectors)) {
            if (!inspectorInstance) continue;

            const categoryName = inspectorInstance.name || key;

            categoriesDict[categoryName] =
                typeof inspectorInstance.toDict === "function"
                    ? inspectorInstance.toDict()
                    : {};
        }

        return {
            [this.items_id]: categoriesDict
        };
    }

    setInspector(type, instance) {
        this.inspectors[type] = instance;
    }

    setMeasurementItems(measurement_items) {
        this.setInspector(ItemsInspector.TYPE_MEASUREMENT, measurement_items);
    }
    setSlitItems(slit_item) {
        this.setInspector(ItemsInspector.TYPE_SLIT, slit_item);
    }
   

    static fromDict(items_id, categories) {
            if (!categories) return new ItemsInspector(items_id, null, null);
            const measurementData = categories[ItemsInspector.TYPE_MEASUREMENT] || categories["measurement"]; // Dự phòng key string
            const measurementInstance = measurementData 
                ? MeasurementItemsInspector.fromDict(measurementData) 
                : null;
            const slitData = categories[ItemsInspector.TYPE_SLIT] || categories["slit"]; // Dự phòng key là "slit"
            let slitInstance = null;
            if (slitData) {
                slitInstance = new SlitItemInspector();
                slitInstance.fromDict(slitData); // Hàm từ bài trước nạp dữ liệu từ Object dict vào mảng
            }
            return new ItemsInspector(
                items_id,
                measurementInstance,
                slitInstance
            );
        }
}