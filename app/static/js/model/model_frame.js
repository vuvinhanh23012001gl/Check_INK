import {ItemsInspector} from "../services/items_inspector.js";
import { Measurement } from "../model/model_measurement.js";
import {MeasurementItemsInspector} from "../services/measurement_items_inspector.js"

export class Frame{
    constructor(frame_id){
        this.frame_id = frame_id
        this.arr_items = []
    }

    addItem(itemInspector) {
        this.arr_items.push(itemInspector);
    }

    toDict() {
        const itemsDict = {};
        for (const item of this.arr_items) {
            Object.assign(itemsDict, item.toDict());
        }
        return {
            [this.frame_id]: itemsDict
        };
    }
        
    static fromDict(data) {
        const frame_id = Object.keys(data)[0];
        const frame = new Frame(frame_id);

        const itemsData = data[frame_id];

        for (const [items_id, categories] of Object.entries(itemsData)) {
            // console.log("categories",categories);
            // console.log("items_id",items_id);
            const item = ItemsInspector.fromDict(items_id, categories);
            // console.log("item",item);
            frame.addItem(item);
        }

        return frame;
    }

    getItemCount() {
        return this.arr_items.length;
    }

    getItem(index) {
        if (index < 0 || index >= this.arr_items.length) {
            return null;
        }
        return this.arr_items[index];
    }
    getItemById(item_id) {
    return this.arr_items.find(
        obj_item_inspector => obj_item_inspector.items_id == item_id
    ) || null;
}

}

// const m1 = new Measurement(
//     "line_1",
//     "Weld A",
//     10, 20, 30, 40, 50,
//     100, 200, 300, 400
// );
// const m2 = new Measurement(
//     "line_2",
//     "Weld B",
//     15, 25, 35, 45, 55,
//     150, 250, 350, 450
// );
// const measurementItems = new MeasurementItemsInspector();
// measurementItems.arr_measure.push(m1);
// measurementItems.arr_measure.push(m2);
// const item = new ItemsInspector(
//     "item_1",
//     measurementItems
// );
// const frame = new Frame("frame_1");
// frame.addItem(item);
// const dict = frame.toDict();
// console.log(JSON.stringify(dict, null, 2));
// const restored = Frame.fromDict(dict);
// console.log(restored);