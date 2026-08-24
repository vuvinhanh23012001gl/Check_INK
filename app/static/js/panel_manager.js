export function openOptionPanel(panel) {
    // Mở một panel cấp cao và đóng panel đang mở trong vùng show-option.
    document.querySelectorAll(".show-option > .paner").forEach((item) => {
        item.classList.remove("active");
    });
    panel.classList.add("active");
}