import {fetchGet} from "../utills/api.js"
import {scroll_container,canvasManager}from "../common_value.js"
import {getValue} from "../utills/logic.js"
import {panner_measure_weld_width,obj_measure_weld_width_canvas,
    additional_events,set_obj_product} from "./common_value_tool.js"
import {Product} from "../model/model_product.js"
import { ItemsInspector } from "../services/items_inspector.js"
const panner_adjust_master = document.getElementById("panner-adjust-master");
const header_adjust_master = document.getElementById("header-ul-li-adjustment-master");
const btn_measure_weld_width = document.getElementById("btn-measure-weld-width");

let current_frame_box = null;
let selected =  {
        product_id: -1,
        frame_id: -1,
        items_id: -1
}




btn_measure_weld_width.addEventListener("click",()=>{
    console.log("--------Vào Tool nhận diện khoảng cách đường line-------");
    panner_measure_weld_width.classList.add("active");
    btn_measure_weld_width.classList.add("active");
    canvasManager.setTool(obj_measure_weld_width_canvas);


   

});

header_adjust_master.addEventListener("click",async ()=>{
    console.log("--------Bạn đã nhấn vào thay đổi master--------");
    console.log("Bạn vừa click vào hiệu chuẩn kích thước");
    panner_adjust_master.classList.add("active");
    let head_data_master = await  fetchGet("/law_regulation");
    console.log("head_data_master",head_data_master);
    let data_point =  head_data_master?.data?.data_point;
    selected.product_id = head_data_master?.data?.product?._id;
    console.log("ID sản phẩm đang chọn là :",selected.product_id);
    let data_master = head_data_master?.data?.data_master;
    console.log("Data master",data_master);
    let actual_wid_img = head_data_master?.data?.wid_img;
    let actual_hei_img = head_data_master?.data?.hei_img;
    create_img_items_dimesion_calibration(data_point);
    create_object_need(head_data_master?.data?.tree?.data);

});

function create_object_need(tree){
    // try {
        const product = Product.fromDict(tree);
        const product_json = JSON.stringify(tree);
        // console.log("product_json",product_json);
        // console.log("product",product);
        set_obj_product(product);
    // }
    // catch (err) {
    //     console.error(err.message);
    // }
}


function create_img_items_dimesion_calibration(points_and_box){
        // console.log("Data create_img_items",data?.data);
        // console.log("data đúng của product");
        // console.log("points_and_box",points_and_box);
        let index_frame = 0;
        let build_tree = {};
        for (const boxs in points_and_box){
            // console.log("boxs",boxs);
            // console.log("Số Frame ID hiện tại bằng",count_frame_id);
            let index_items = 0;
            let result_create_box = create_box(boxs,index_frame);
            let div_img_box = result_create_box.div_img_box;
            let div_box_frame = result_create_box.div_box_frame;
            index_frame++;
            for (const items in points_and_box[boxs]){
                // console.log("data nhan dc la",points_and_box[boxs][items]);
                // console.log("dsaddsdsadsds123",items,points_and_box[boxs][items]);
                let data_point =  points_and_box[boxs][items];
                create_items_img(items,index_items,data_point,div_img_box,boxs);
                index_items++;
            }
        }
}



function create_items_img(id, index ,data_point = null, frame_box =null, frame_id =  null){
    const img_text = document.createElement("div");
    img_text.className = "img-text";
    img_text.textContent = `Ảnh ${index}`;
    const img_img = document.createElement("img");
    img_img.className = "img_show_point";
    const img_item = document.createElement("div");
    if (data_point==null) {img_img.src = "../static/img/plus.png";img_item.dataset.has_icon_add_new = true;} else {img_img.src = `${data_point.path_img_point}?v=${Math.random()}`;}
    img_item.className = "img-item";
    img_item.dataset.id = id;
    img_item.appendChild(img_img);
    img_item.appendChild(img_text);
    if(!frame_box){console.log("Lỗi hoặc không có sản phẩm");return;}
    frame_box.appendChild(img_item);
        img_item.addEventListener("click",()=>{
            canvasManager.clearShapeCanvas();
            canvasManager.show_img_items(img_img);
            scroll_container.querySelectorAll(".box-frame").forEach(frame => {
                frame.querySelectorAll(".img-item").forEach(items => {
                items.classList.remove("active");
                });
            });  
              
            // let x = getValue(data_point?.x);
            // let y = getValue(data_point?.y);
            // let z = getValue(data_point?.z);
            // coordinate_items_now.x = x;
            // coordinate_items_now.y = y;
            // coordinate_items_now.z = z;

            // console.log("coordinate x",x);
            // console.log("coordinate y",y);
            // console.log("coordinate z",z);
            // console.log("frame_box",frame_box);
            img_item.classList.add("active");
            current_frame_box = frame_box;
            selected.items_id = Number(img_item.dataset.id);  
            selected.frame_id = Number(frame_id);
            if (typeof additional_events.onFrameChange === "function") {
                    additional_events.onFrameChange(selected.product_id ,selected.frame_id, selected.items_id,"weld_width_tool");
            }
            console.log(`Point đang click frame: ${selected.frame_id} id: ${selected.items_id}`);
            return;
    });
 }
 
function create_box(box_id,index){
    console.log(`Tạo box ID= ${box_id},Index:${index}`);
    const div_box_frame = document.createElement("div");
    div_box_frame.className = "box-frame";
    div_box_frame.dataset.frameId = box_id; 
    const div_text_box_frame =  document.createElement("div");
    div_text_box_frame.textContent = `Ảnh sản phẩm thứ ${index}`;
    div_text_box_frame.className = "text_inf_frame";
    const div_img_box =  document.createElement("div");
    div_img_box.className = "img-box";
    div_box_frame.addEventListener("click", () => {
        scroll_container.querySelectorAll(".box-frame").forEach(frame => {frame.classList.remove("box-frame-selected");});
        selected.frame_id = div_box_frame.dataset.frameId;
        div_box_frame.classList.add("box-frame-selected");
        console.log("Click vào frame thứ:", selected.frame_id);
        current_frame_box = div_img_box; // lưu frame hiện tại đang click


    });
    div_box_frame.appendChild(div_text_box_frame);
    div_box_frame.appendChild(div_img_box);
    scroll_container.appendChild(div_box_frame);
    return {div_img_box,div_box_frame}
}

