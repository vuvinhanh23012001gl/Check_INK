import { MeasurementItemsInspector } from "./measurement_items_inspector.js";
import { Measurement } from "./model_measurement.js";
const inspector = new MeasurementItemsInspector("items_id_1");
const m = new Measurement(
    "id_line_1",
    "abc",
    1, 2, 3, 4, 7,
    10, 20, 30, 40
);
inspector.addMeasurement(m);
console.log(JSON.stringify(inspector.toDict(), null, 2));
const result = inspector.getMeasurement("id_line_1");
console.log("GET RESULT:", result);