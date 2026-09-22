
import { MeasurementItemsInspector } from "./measurement_items_inspector.js";
import { SlitItemInspector } from "./slit_item_inspector.js";
import { ArmSensorItemInspector } from "./arm_sensor_item_inspector.js";
import { ArmCoverItemInspector } from "./arm_cover_item_inspector.js";
import { BorderFilmInspector } from "./border_film_inspector.js";
import { PermeableMembraneInspector } from "./permeable_membrane_inspector.js";
import { HoleItemInspector } from "./hole_item_inspector.js";
import { ScratchedPipeItemInspector } from "./scratched_pipe_inspector.js";
import { EndChippingInspector } from "./end_chipping_item_inspector.js";
import { ForeignObjectInspector } from "./foreign_object_item_inspector.js";
import { AirBubblesItemInspector } from "./air_bubbles_item_inspector.js";


export class ItemsInspector {
    static TYPE_MEASUREMENT = MeasurementItemsInspector.NAME;
    static TYPE_SLIT = SlitItemInspector.NAME;
    static TYPE_ARM_SENSOR = ArmSensorItemInspector.NAME;
    static TYPE_ARM_COVER = ArmCoverItemInspector.NAME;
    static TYPE_BORDER_FILM = BorderFilmInspector.NAME;
    static TYPE_PERMEABLE_MEMBRANE = PermeableMembraneInspector.NAME;
    static TYPE_HOLE = HoleItemInspector.NAME;
    static TYPE_SCRATCHED_PIPE = ScratchedPipeItemInspector.NAME;
    static TYPE_END_CHIPPING = EndChippingInspector.NAME;
    static TYPE_FOREIGN_OBJECT = ForeignObjectInspector.NAME;
    static TYPE_AIR_BUBBLES = AirBubblesItemInspector.NAME;
    
    constructor(
        items_id,
        measurement_items,
        slit_item,
        arm_sensor_item,
        arm_cover_item,
        border_film_item,
        permeable_membrane_item,
        hole_item,
        scratched_pipe_item,
        end_chipping_item,
        foreign_object_item = null,
        air_bubbles_item = null
    ) {
        this.items_id = items_id;

        this.inspectors = {
            [ItemsInspector.TYPE_MEASUREMENT]: measurement_items || null,
            [ItemsInspector.TYPE_SLIT]: slit_item || null,
            [ItemsInspector.TYPE_ARM_SENSOR]: arm_sensor_item || null,
            [ItemsInspector.TYPE_ARM_COVER]: arm_cover_item || null,
            [ItemsInspector.TYPE_BORDER_FILM]: border_film_item || null,
            [ItemsInspector.TYPE_PERMEABLE_MEMBRANE]: permeable_membrane_item || null,
            [ItemsInspector.TYPE_HOLE]: hole_item || null,
            [ItemsInspector.TYPE_SCRATCHED_PIPE]: scratched_pipe_item || null,
            [ItemsInspector.TYPE_END_CHIPPING]: end_chipping_item || null, // Tích hợp EndChipping vào danh sách inspectors
            [ItemsInspector.TYPE_FOREIGN_OBJECT]: foreign_object_item || null,
            [ItemsInspector.TYPE_AIR_BUBBLES]: air_bubbles_item || null,
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

    /**
     * Lấy thực thể inspector quản lý Hole
     * @returns {HoleItemInspector|null}
     */
    getHoleItems() {
        return this.getInspector(ItemsInspector.TYPE_HOLE);
    }

    /**
     * Lấy thực thể inspector quản lý Scratched Pipe
     * @returns {ScratchedPipeItemInspector|null}
     */
    getScratchedPipeItems() {
        return this.getInspector(ItemsInspector.TYPE_SCRATCHED_PIPE);
    }

    /**
     * Lấy thực thể inspector quản lý End Chipping
     * @returns {EndChippingInspector|null}
     */
    getEndChippingItems() {
        return this.getInspector(ItemsInspector.TYPE_END_CHIPPING);
    }

    getForeignObjectItems() {
        return this.getInspector(ItemsInspector.TYPE_FOREIGN_OBJECT);
    }

    getAirBubblesItems() {
        return this.getInspector(ItemsInspector.TYPE_AIR_BUBBLES);
    }

    toDict() {
        const categoriesDict = {};
        for (const [key, inspectorInstance] of Object.entries(this.inspectors)) {
            console.log("key",key,"inspectorInstance",inspectorInstance);
            console.log("----------------------------");
            if (!inspectorInstance) continue;
            let dict_data = inspectorInstance.toDict();
            if (!dict_data || Object.keys(dict_data).length === 0) {
                continue;
            }
            categoriesDict[key] = dict_data;
            console.log("categoriesDict[key]",categoriesDict[key]);
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

    /**
     * Cập nhật thực thể HoleItemInspector
     * @param {HoleItemInspector} hole_item 
     */
    setHoleItems(hole_item) {
        this.setInspector(
            ItemsInspector.TYPE_HOLE,
            hole_item
        );
    }

    /**
     * Cập nhật thực thể ScratchedPipeItemInspector
     * @param {ScratchedPipeItemInspector} scratched_pipe_item 
     */
    setScratchedPipeItems(scratched_pipe_item) {
        this.setInspector(
            ItemsInspector.TYPE_SCRATCHED_PIPE,
            scratched_pipe_item
        );
    }

    /**
     * Cập nhật thực thể EndChippingInspector
     * @param {EndChippingInspector} end_chipping_item 
     */
    setEndChippingItems(end_chipping_item) {
        this.setInspector(
            ItemsInspector.TYPE_END_CHIPPING,
            end_chipping_item
        );
    }

    setForeignObjectItems(foreign_object_item) {
        this.setInspector(ItemsInspector.TYPE_FOREIGN_OBJECT, foreign_object_item);
    }

    setAirBubblesItems(air_bubbles_item) {
        this.setInspector(
            ItemsInspector.TYPE_AIR_BUBBLES,
            air_bubbles_item
        );
    }
    clearInspectors() {
        for (const type of Object.keys(this.inspectors)) {
            this.inspectors[type] = null;
        }
    }
    static fromDict(items_id, categories) {
        //  console.log("items_id",items_id,"categories",categories);
        if (!categories) {
            return new ItemsInspector(
                items_id,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null
            );
        }

        // Measurement
        const measurementData = categories[ItemsInspector.TYPE_MEASUREMENT];
        const measurementInstance = measurementData? MeasurementItemsInspector.fromDict(measurementData): null;

        // Slit
        const slitData = categories[ItemsInspector.TYPE_SLIT] 
        let slitInstance = null;
        if (slitData) {
            slitInstance = new SlitItemInspector();
            slitInstance.fromDict(slitData);
        }
             // Border Film
        const borderFilmData = categories[ItemsInspector.TYPE_BORDER_FILM]
        let borderFilmInstance = null;
        if (borderFilmData) {
            borderFilmInstance = new BorderFilmInspector();
            borderFilmInstance.fromDict(borderFilmData);
        }


        // Arm Sensor
        const armSensorData = categories[ItemsInspector.TYPE_ARM_SENSOR]
        let armSensorInstance = null;
        if (armSensorData) {
            console.log(`Có dữ liệu armSensorInstance tại ${items_id}`,armSensorData);
            armSensorInstance = ArmSensorItemInspector.fromDict(armSensorData);
            console.log("Đối tượng armCoverInstance",armSensorInstance);
        }

        // Arm Cover
        const armCoverData = categories[ItemsInspector.TYPE_ARM_COVER]
        let armCoverInstance = null;
        if (armCoverData) {
            console.log(`Có dữ liệu armCoverData tại ${items_id}`,armCoverData);
            armCoverInstance = ArmCoverItemInspector.fromDict(armCoverData);
            console.log("Đối tượng armCoverInstance",armCoverInstance);
        }


        // Permeable Membrane
        const permeableMembraneData = categories[ItemsInspector.TYPE_PERMEABLE_MEMBRANE]
        let permeableMembraneInstance = null;
        if (permeableMembraneData) {
            console.log(`Có dữ liệu permeableMembraneData tại ${items_id}`,permeableMembraneData);
            permeableMembraneInstance = PermeableMembraneInspector.fromDict(permeableMembraneData);
            console.log("Đối tượng PermeableMembraneInspector",permeableMembraneInstance);
        }

        // Hole
        const holeData = categories[ItemsInspector.TYPE_HOLE] 
        let holeInstance = null;
        if (holeData) {
            console.log(`Có dữ liệu holeData tại ${items_id}`,holeData);
            holeInstance = HoleItemInspector.fromDict(holeData);
            console.log("Đối tượng holeInstance",holeInstance);
        }

        // Scratched Pipe
        const scratchedPipeData = categories[ItemsInspector.TYPE_SCRATCHED_PIPE];
        let scratchedPipeInstance = null;
        if (scratchedPipeData) {
            console.log(`Có dữ liệu scratchedPipeData tại ${items_id}`,scratchedPipeData);
            scratchedPipeInstance = ScratchedPipeItemInspector.fromDict(scratchedPipeData);
            console.log("Đối tượng scratchedPipeInstance",scratchedPipeInstance);
        }

        // End Chipping
        const endChippingData = categories[ItemsInspector.TYPE_END_CHIPPING] 
        let endChippingInstance = null;
        if (endChippingData) {
            console.log(`Có dữ liệu endChippingData tại ${items_id}`,endChippingData);
            endChippingInstance = EndChippingInspector.fromDict(endChippingData);
            console.log("Đối tượng endChippingInstance",endChippingInstance);
        }

        const foreignObjectData = categories[ItemsInspector.TYPE_FOREIGN_OBJECT];
        const foreignObjectInstance = foreignObjectData
            ? ForeignObjectInspector.fromDict(foreignObjectData)
            : null;

        const airBubblesData = categories[ItemsInspector.TYPE_AIR_BUBBLES];
        const airBubblesInstance = airBubblesData
            ? AirBubblesItemInspector.fromDict(airBubblesData)
            : null;

        return new ItemsInspector(
            items_id,
            measurementInstance,
            slitInstance,
            armSensorInstance,
            armCoverInstance,
            borderFilmInstance,
            permeableMembraneInstance,
            holeInstance,
            scratchedPipeInstance,
            endChippingInstance,
            foreignObjectInstance,
            airBubblesInstance
        );
    }
}