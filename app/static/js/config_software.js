const btn_config_software = document.getElementById("btn-open-software-config");
const btn_close_settings = document.getElementById("close-settings");
const overlay_config_software = document.getElementById("overlay_config_software");
 

btn_config_software.addEventListener("click",function(){
    console.log("Bạn vừa nhấn vào config software");
    overlay_config_software.style.display = "flex";

});

btn_close_settings.addEventListener("click",function(){
    console.log("Bạn vừa nhấn thoát config software");
    overlay_config_software.style.display = "none";
});
