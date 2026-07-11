console.log("Vào File Arm Sensor Tool");

import {scroll_container,canvasManager,WIDTH_IMG_SHAPE}from "../common_value.js"
import {additional_events,obj_region_arm_sensor_canvas,boxContentMeasureSlitWidth,get_obj_product,selected
} from "./common_value_tool.js"   
import {RectangleDrawer} from "../canvas/rectangel_drawer_canvas.js"




additional_events.set("arm_sensor_tool", event_transition_items);
const btn_judment_arm_sensor = document.getElementById("btn-judment-arm-sensor");
const log_arm_sensor = document.getElementById("log-arm-sensor");

 

obj_region_arm_sensor_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT,func_callback_click_on_rect);
obj_region_arm_sensor_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_RIGHT_RECT,func_callback_click_mouse_right_into_line);
obj_region_arm_sensor_canvas.on(RectangleDrawer.NAME_EVENT_WHEN_CLICK_ON_RECT_HAVE_ALREADY,func_callback_click_on_line_have_aready);


function func_callback_click_on_rect(data){
    console.log("click vào khung",data);
    

}
function func_callback_click_mouse_right_into_line(data){
    
}
function func_callback_click_on_line_have_aready(){

}
function event_transition_items(){

}