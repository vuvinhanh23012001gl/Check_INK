
// export const scroll_content = document.getElementById("scroll-content");
import {SocketModel} from "./model/model_socket.js"
import { CanvasManager } from "./manager/canvas_manager.js"
import { VideoManager } from "./manager/video_manager.js"


    
//import socket 
export const SocketLog = new SocketModel("log");
export const SocketData = new SocketModel("data");
SocketLog.connect();
SocketData.connect();

 
const WIDTH_IMG_SHAPE = 1365.33;
const HEIGH_IMG_SHAPE = 1024;



export const scroll_container = document.querySelector(".scroll-container");
export const video_product = document.getElementById("video-product");

export const videoManager = new VideoManager(video_product);
export const canvasManager = new CanvasManager("coordinate","wrap-canvas",video_product,WIDTH_IMG_SHAPE,HEIGH_IMG_SHAPE);
canvasManager.initEvent();



    
       
      
        
    













const COM_KEY = "com_connected";
export function set_com_connection(isConnected) {
    sessionStorage.setItem(COM_KEY, isConnected ? "true" : "false");
}

export function get_com_connection() {
    if (sessionStorage.getItem(COM_KEY) === null) {
        sessionStorage.setItem(COM_KEY, "false");
    }
    return sessionStorage.getItem(COM_KEY) === "true";
}


const CAMERA_KEY = "camera_connected";
export function set_camera_connection(isConnected) {
    sessionStorage.setItem(CAMERA_KEY, isConnected ? "true" : "false");
}

export function get_camera_connection() {
    if (sessionStorage.getItem(CAMERA_KEY) === null) {
        sessionStorage.setItem(CAMERA_KEY, "false");
    }
    return sessionStorage.getItem(CAMERA_KEY) === "true";
}




export function active_sceen_show_video(){
        video_product.style.width = `${WIDTH_IMG_SHAPE}px`;
        video_product.style.height = `${HEIGH_IMG_SHAPE}px`;  
        video_product.style.objectFit = "contain";   
        video_product.style.display = "flex";
        canvasManager.setWrapCanvasVisible(false);
}

export function show_video_product(){
    canvasManager.video_product.style.display = "block";
    videoManager.connect();
    canvasManager.setWrapCanvasVisible(false);
}

