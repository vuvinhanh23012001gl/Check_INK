import { Frame } from "./model_frame.js";
// const dictdata = {
//   "1": {
//     "0": {
//       "0": {
//         "measurement": {
//           "1": {
//             "name_line": "Weld A",
//             "level1": 10,
//             "level2": 20,
//             "level3": 30,
//             "level4": 40,
//             "level5": 50,
//             "xStart": 100,
//             "yStart": 200,
//             "xEnd": 300,
//             "yEnd": 400
//           },
//           "2": {
//             "name_line": "Weld B",
//             "level1": 15,
//             "level2": 25,
//             "level3": 35,
//             "level4": 45,
//             "level5": 55,
//             "xStart": 150,
//             "yStart": 250,
//             "xEnd": 350,
//             "yEnd": 450
//           }
//         }
//       }
//     },
//     "1": {
//       "0": {
//         "measurement": {
//           "3": {
//             "name_line": "Weld C",
//             "level1": 5,
//             "level2": 10,
//             "level3": 15,
//             "level4": 20,
//             "level5": 25,
//             "xStart": 50,
//             "yStart": 60,
//             "xEnd": 70,
//             "yEnd": 80
//           }
//         }
//       }
//     }
//   }
// };

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
            frame => frame.frame_id === frame_id
        );
    }

    toDict() {
        const framesDict = {};

        for (const frame of this.arr_frames) {
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
            try {
                const frame = Frame.fromDict({
                    [frame_id]: frameData
                });
                if (!frame) {
                    throw new Error("Frame trả về null");
                }
                product.addFrame(frame);
            } catch (err) {
                throw new Error(
                    `Lỗi khi đọc Frame '${frame_id}': ${err.message}`
                );
            }
        }
        return product;
    }

    find_item_object_corresponding(frame_id, item_id , type){
        let obj_frame_iD = this.getFrame(frame_id);
        if (!obj_frame_iD){console.log("Không tìm thấy đối Obj Frame");return null;}
        let obj_items_inspector = obj_frame_iD.getItemById(item_id);
        // console.log("obj_items_inspector",obj_items_inspector);
        if (!obj_items_inspector){console.log("Không tìm thấy đối Obj Item inspector");return null;}
          let obj_type  = obj_items_inspector.getInspector(type);
          if (!obj_type){console.log(`Với type:${type} không có dữ liệu`);return null;}
          //console.log("obj_type",obj_type);
          return obj_type  //trả về đối tượng MeasurementItemsInspector bằng cấp với type
    }

    get_item_object(frame_id, item_id){
        let obj_frame_iD = this.getFrame(frame_id);
        if (!obj_frame_iD){console.log("Không tìm thấy đối Obj Frame");return null;}
        let obj_items_inspector = obj_frame_iD.getItemById(item_id);
        return obj_items_inspector;
    }

    get_item_inspector(frame_id, item_id){
        let obj_frame_iD = this.getFrame(frame_id);
        if (!obj_frame_iD){console.log("Không tìm thấy đối Obj Frame");return null;}
        let obj_items_inspector = obj_frame_iD.getItemById(item_id);
        return obj_items_inspector;
    }

    find_line_object_corresponding(frame_id, item_id , type, line_id){
       let obj_type = this.find_item_object_corresponding(frame_id, item_id , type);
       if (!obj_type){console.log("Không tìm thấy type tương ứng");return null};
      //  console.log("obj_type",obj_type);
       let obj_line = obj_type.getMeasurementByLineId(line_id);
      //  console.log("obj_line",obj_line);
       return obj_line;
    }

}

// ItemsInspector.TYPE_MEASUREMENT

// import {ItemsInspector} from "../services/items_inspector.js";
// import { Measurement } from "../model/model_measurement.js";
// import {MeasurementItemsInspector} from "../services/measurement_items_inspector.js"
// const restored = Product.fromDict(dictdata);
// // console.log("-------------------------------------");
// //Lấy đối tượng Frame

// // let Frame_ID = restored.getFrame("0");   // cái này chính là Object Frame
// // console.log("Object Frame Find",Frame_ID);   

// // console.log("Số phần tử item inspector",Frame_ID.getItemCount());
// // console.log("Lấy item tại index thứ 0",getItemCount());

// // restored.find_item_object_corresponding("1","0","measurement");
// restored.find_line_object_corresponding("1","0","measurement",0);