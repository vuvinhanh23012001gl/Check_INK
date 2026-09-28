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

const btn_software_information = document.getElementById("get_infor_software");
const software_information_overlay = document.getElementById("software-information-overlay");
const software_information_content = document.getElementById("software-information-content");
const btn_exit_software_information = document.getElementById("btn_exit_infor_software");

function renderInformationGroup(title, items, includeDetails = false) {
    const section = document.createElement("section");
    section.className = "software-information-group";

    const heading = document.createElement("h3");
    heading.textContent = title;
    section.appendChild(heading);

    items.forEach((item) => {
        const entry = document.createElement("div");
        entry.className = "software-information-entry";

        const label = document.createElement("strong");
        label.textContent = item.label;
        entry.appendChild(label);

        if (item.path) {
            const path = document.createElement("code");
            path.textContent = item.path;
            entry.appendChild(path);
        }

        if (item.message) {
            const message = document.createElement("p");
            message.textContent = item.message;
            entry.appendChild(message);
        }

        if (includeDetails && item.value !== undefined) {
            const value = document.createElement("span");
            value.textContent = String(item.value);
            entry.appendChild(value);
        }

        section.appendChild(entry);
    });

    software_information_content.appendChild(section);
}

function showSoftwareInformation() {
    software_information_overlay.hidden = false;
    software_information_content.replaceChildren();
    fetch("/software/information")
        .then((response) => {
            if (!response.ok) throw new Error("Không thể tải thông tin phần mềm");
            return response.json();
        })
        .then((data) => {
            renderInformationGroup("Nhóm 1: Đường dẫn mô hình", data.models);
            renderInformationGroup("Nhóm 2: Đường dẫn output phán định", data.outputs);
            const software_labels = {
                name: "Tên phần mềm",
                version: "Phiên bản",
                author: "Tác giả",
                company: "Công ty",
                description: "Mô tả",
                build_date: "Ngày xây dựng",
                license: "Giấy phép",
            };
            renderInformationGroup(
                "Nhóm 3: Thông tin phần mềm",
                Object.entries(data.software).map(([key, value]) => ({
                    label: software_labels[key] || key,
                    value,
                })),
                true
            );
        })
        .catch((error) => {
            const message = document.createElement("p");
            message.textContent = error.message;
            software_information_content.replaceChildren(message);
        });
}

function hideSoftwareInformation() {
    software_information_overlay.hidden = true;
}

btn_software_information.addEventListener("click", showSoftwareInformation);
btn_exit_software_information.addEventListener("click", hideSoftwareInformation);
