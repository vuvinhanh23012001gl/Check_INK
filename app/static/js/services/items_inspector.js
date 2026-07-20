

// import { MeasurementItemsInspector } from "./measurement_items_inspector.js";
// import { SlitItemInspector } from "./slit_item_inspector.js";
// import { ArmSensorItemInspector } from "./arm_sensor_item_inspector.js";
// import { ArmCoverItemInspector } from "./arm_cover_item_inspector.js";
// import { BorderFilmInspector } from "./border_film_inspector.js";
// import {PermeableMembraneInspector} from "./permeable_membrane_inspector.js"
// export class ItemsInspector {
//     static TYPE_MEASUREMENT = MeasurementItemsInspector.NAME;
//     static TYPE_SLIT = SlitItemInspector.NAME;
//     static TYPE_ARM_SENSOR = ArmSensorItemInspector.NAME;
//     static TYPE_ARM_COVER = ArmCoverItemInspector.NAME;
//     static TYPE_BORDER_FILM = BorderFilmInspector.NAME; // Đã định nghĩa tĩnh thành công

//     constructor(
//         items_id,
//         measurement_items,
//         slit_item,
//         arm_sensor_item,
//         arm_cover_item,
//         border_film_item // Bổ sung tham số thứ 6 vào constructor
//     ) {
//         this.items_id = items_id;

//         this.inspectors = {
//             [ItemsInspector.TYPE_MEASUREMENT]: measurement_items || null,
//             [ItemsInspector.TYPE_SLIT]: slit_item || null,
//             [ItemsInspector.TYPE_ARM_SENSOR]: arm_sensor_item || null,
//             [ItemsInspector.TYPE_ARM_COVER]: arm_cover_item || null,
//             [ItemsInspector.TYPE_BORDER_FILM]: border_film_item || null, // Đã tích hợp vào danh sách inspectors
//         };
//     }

//     getInspector(type) {
//         return this.inspectors[type] || null;
//     }

//     getMeasurementItems() {
//         return this.getInspector(ItemsInspector.TYPE_MEASUREMENT);
//     }

//     getSlitItems() {
//         return this.getInspector(ItemsInspector.TYPE_SLIT);
//     }

//     getArmSensorItems() {
//         return this.getInspector(ItemsInspector.TYPE_ARM_SENSOR);
//     }

//     getArmCoverItems() {
//         return this.getInspector(ItemsInspector.TYPE_ARM_COVER);
//     }

//     /**
//      * Lấy thực thể inspector quản lý đường biên màng phim
//      * @returns {BorderFilmInspector|null}
//      */
//     getBorderFilmItems() {
//         return this.getInspector(ItemsInspector.TYPE_BORDER_FILM);
//     }

//     toDict() {
//         const categoriesDict = {};

//         for (const [key, inspectorInstance] of Object.entries(this.inspectors)) {
//             if (!inspectorInstance) continue;

//             const categoryName = inspectorInstance.name || key;

//             categoriesDict[categoryName] =
//                 typeof inspectorInstance.toDict === "function"
//                     ? inspectorInstance.toDict()
//                     : {};
//         }

//         return {
//             [this.items_id]: categoriesDict,
//         };
//     }

//     setInspector(type, instance) {
//         this.inspectors[type] = instance;
//     }

//     setMeasurementItems(measurement_items) {
//         this.setInspector(
//             ItemsInspector.TYPE_MEASUREMENT,
//             measurement_items
//         );
//     }

//     setSlitItems(slit_item) {
//         this.setInspector(
//             ItemsInspector.TYPE_SLIT,
//             slit_item
//         );
//     }

//     setArmSensorItems(arm_sensor_item) {
//         this.setInspector(
//             ItemsInspector.TYPE_ARM_SENSOR,
//             arm_sensor_item
//         );
//     }

//     setArmCoverItems(arm_cover_item) {
//         this.setInspector(
//             ItemsInspector.TYPE_ARM_COVER,
//             arm_cover_item
//         );
//     }

//     /**
//      * Cập nhật thực thể BorderFilmInspector
//      * @param {BorderFilmInspector} border_film_item 
//      */
//     setBorderFilmItems(border_film_item) {
//         this.setInspector(
//             ItemsInspector.TYPE_BORDER_FILM,
//             border_film_item
//         );
//     }

//     static fromDict(items_id, categories) {
//         if (!categories) {
//             return new ItemsInspector(
//                 items_id,
//                 null,
//                 null,
//                 null,
//                 null,
//                 null // Giá trị mặc định cho tham số thứ 6
//             );
//         }

//         // Measurement
//         const measurementData =
//             categories[ItemsInspector.TYPE_MEASUREMENT] ||
//             categories["measurement"];

//         const measurementInstance = measurementData
//             ? MeasurementItemsInspector.fromDict(measurementData)
//             : null;

//         // Slit
//         const slitData =
//             categories[ItemsInspector.TYPE_SLIT] ||
//             categories["slit"];

//         let slitInstance = null;
//         if (slitData) {
//             slitInstance = new SlitItemInspector();
//             slitInstance.fromDict(slitData);
//         }

//         // Arm Sensor
//         const armSensorData =
//             categories[ItemsInspector.TYPE_ARM_SENSOR] ||
//             categories["armsensor"] ||
//             categories["arm_sensor"];

//         let armSensorInstance = null;
//         if (armSensorData) {
//             armSensorInstance = new ArmSensorItemInspector();
//             armSensorInstance.fromDict(armSensorData);
//         }

//         // Arm Cover
//         const armCoverData =
//             categories[ItemsInspector.TYPE_ARM_COVER] ||
//             categories["armcover"] ||
//             categories["arm_cover"];

//         let armCoverInstance = null;
//         if (armCoverData) {
//             armCoverInstance = new ArmCoverItemInspector();
//             armCoverInstance.fromDict(armCoverData);
//         }

//         // Border Film (BỔ SUNG)
//         const borderFilmData =
//             categories[ItemsInspector.TYPE_BORDER_FILM] ||
//             categories["borderfilm"] ||
//             categories["border_film"];

//         let borderFilmInstance = null;
//         if (borderFilmData) {
//             borderFilmInstance = new BorderFilmInspector();
//             borderFilmInstance.fromDict(borderFilmData);
//         }

//         return new ItemsInspector(
//             items_id,
//             measurementInstance,
//             slitInstance,
//             armSensorInstance,
//             armCoverInstance,
//             borderFilmInstance // Đóng gói vào đối tượng trả về
//         );
//     }
// }

import { MeasurementItemsInspector } from "./measurement_items_inspector.js";
import { SlitItemInspector } from "./slit_item_inspector.js";
import { ArmSensorItemInspector } from "./arm_sensor_item_inspector.js";
import { ArmCoverItemInspector } from "./arm_cover_item_inspector.js";
import { BorderFilmInspector } from "./border_film_inspector.js";
import { PermeableMembraneInspector } from "./permeable_membrane_inspector.js"; // Import thành công

export class ItemsInspector {
    static TYPE_MEASUREMENT = MeasurementItemsInspector.NAME;
    static TYPE_SLIT = SlitItemInspector.NAME;
    static TYPE_ARM_SENSOR = ArmSensorItemInspector.NAME;
    static TYPE_ARM_COVER = ArmCoverItemInspector.NAME;
    static TYPE_BORDER_FILM = BorderFilmInspector.NAME;
    static TYPE_PERMEABLE_MEMBRANE = PermeableMembraneInspector.NAME; // Định nghĩa thuộc tính tĩnh cho Membrane

    constructor(
        items_id,
        measurement_items,
        slit_item,
        arm_sensor_item,
        arm_cover_item,
        border_film_item,
        permeable_membrane_item // Bổ sung tham số thứ 7 vào constructor
    ) {
        this.items_id = items_id;

        this.inspectors = {
            [ItemsInspector.TYPE_MEASUREMENT]: measurement_items || null,
            [ItemsInspector.TYPE_SLIT]: slit_item || null,
            [ItemsInspector.TYPE_ARM_SENSOR]: arm_sensor_item || null,
            [ItemsInspector.TYPE_ARM_COVER]: arm_cover_item || null,
            [ItemsInspector.TYPE_BORDER_FILM]: border_film_item || null,
            [ItemsInspector.TYPE_PERMEABLE_MEMBRANE]: permeable_membrane_item || null, // Tích hợp vào danh sách inspectors
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

    getArmSensorItems() {
        return this.getInspector(ItemsInspector.TYPE_ARM_SENSOR);
    }

    getArmCoverItems() {
        return this.getInspector(ItemsInspector.TYPE_ARM_COVER);
    }

    /**
     * Lấy thực thể inspector quản lý đường biên màng phim
     * @returns {BorderFilmInspector|null}
     */
    getBorderFilmItems() {
        return this.getInspector(ItemsInspector.TYPE_BORDER_FILM);
    }

    /**
     * Lấy thực thể inspector quản lý màng bán thấm
     * @returns {PermeableMembraneInspector|null}
     */
    getPermeableMembraneItems() {
        return this.getInspector(ItemsInspector.TYPE_PERMEABLE_MEMBRANE);
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
            [this.items_id]: categoriesDict,
        };
    }

    setInspector(type, instance) {
        this.inspectors[type] = instance;
    }

    setMeasurementItems(measurement_items) {
        this.setInspector(
            ItemsInspector.TYPE_MEASUREMENT,
            measurement_items
        );
    }

    setSlitItems(slit_item) {
        this.setInspector(
            ItemsInspector.TYPE_SLIT,
            slit_item
        );
    }

    setArmSensorItems(arm_sensor_item) {
        this.setInspector(
            ItemsInspector.TYPE_ARM_SENSOR,
            arm_sensor_item
        );
    }

    setArmCoverItems(arm_cover_item) {
        this.setInspector(
            ItemsInspector.TYPE_ARM_COVER,
            arm_cover_item
        );
    }

    /**
     * Cập nhật thực thể BorderFilmInspector
     * @param {BorderFilmInspector} border_film_item 
     */
    setBorderFilmItems(border_film_item) {
        this.setInspector(
            ItemsInspector.TYPE_BORDER_FILM,
            border_film_item
        );
    }

    /**
     * Cập nhật thực thể PermeableMembraneInspector
     * @param {PermeableMembraneInspector} permeable_membrane_item 
     */
    setPermeableMembraneItems(permeable_membrane_item) {
        this.setInspector(
            ItemsInspector.TYPE_PERMEABLE_MEMBRANE,
            permeable_membrane_item
        );
    }

    static fromDict(items_id, categories) {
        if (!categories) {
            return new ItemsInspector(
                items_id,
                null,
                null,
                null,
                null,
                null,
                null // Giá trị mặc định cho tham số thứ 7
            );
        }

        // Measurement
        const measurementData =
            categories[ItemsInspector.TYPE_MEASUREMENT] ||
            categories["measurement"];

        const measurementInstance = measurementData
            ? MeasurementItemsInspector.fromDict(measurementData)
            : null;

        // Slit
        const slitData =
            categories[ItemsInspector.TYPE_SLIT] ||
            categories["slit"];

        let slitInstance = null;
        if (slitData) {
            slitInstance = new SlitItemInspector();
            slitInstance.fromDict(slitData);
        }

        // Arm Sensor
        const armSensorData =
            categories[ItemsInspector.TYPE_ARM_SENSOR] ||
            categories["armsensor"] ||
            categories["arm_sensor"];

        let armSensorInstance = null;
        if (armSensorData) {
            armSensorInstance = new ArmSensorItemInspector();
            armSensorInstance.fromDict(armSensorData);
        }

        // Arm Cover
        const armCoverData =
            categories[ItemsInspector.TYPE_ARM_COVER] ||
            categories["armcover"] ||
            categories["arm_cover"];

        let armCoverInstance = null;
        if (armCoverData) {
            armCoverInstance = new ArmCoverItemInspector();
            armCoverInstance.fromDict(armCoverData);
        }

        // Border Film
        const borderFilmData =
            categories[ItemsInspector.TYPE_BORDER_FILM] ||
            categories["borderfilm"] ||
            categories["border_film"];

        let borderFilmInstance = null;
        if (borderFilmData) {
            borderFilmInstance = new BorderFilmInspector();
            borderFilmInstance.fromDict(borderFilmData);
        }

        // Permeable Membrane (Cấu trúc đồng bộ hoàn toàn với Arm Sensor)
        const permeableMembraneData =
            categories[ItemsInspector.TYPE_PERMEABLE_MEMBRANE] ||
            categories["permeablemembrane"] ||
            categories["permeable_membrane"] ||
            categories["membrane"];

        let permeableMembraneInstance = null;
        if (permeableMembraneData) {
            permeableMembraneInstance = new PermeableMembraneInspector();
            permeableMembraneInstance.fromDict(permeableMembraneData);
        }

        return new ItemsInspector(
            items_id,
            measurementInstance,
            slitInstance,
            armSensorInstance,
            armCoverInstance,
            borderFilmInstance,
            permeableMembraneInstance // Đóng gói vào đối tượng trả về
        );
    }
}