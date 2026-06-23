import { MeasurementItemsInspector } from "../services/measurement_items_inspector.js";

export class ItemsInspector {

    static TYPE_MEASUREMENT = "measurement";

    constructor(items_id, measurement_items) {
        this.items_id = items_id;

        this.inspectors = {
            [ItemsInspector.TYPE_MEASUREMENT]: measurement_items,
        };
    }
    getInspector(type) {
        return this.inspectors[type] || null;
    }

    getMeasurementItems() {
        return this.getInspector(ItemsInspector.TYPE_MEASUREMENT);
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
    static fromDict(items_id, categories) {
        return new ItemsInspector(
            items_id,
            categories[ItemsInspector.TYPE_MEASUREMENT]
                ? MeasurementItemsInspector.fromDict(
                    categories[ItemsInspector.TYPE_MEASUREMENT]
                )
                : null
        );
    }
}