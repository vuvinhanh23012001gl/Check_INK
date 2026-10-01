/**
 * CONFIG SOFTWARE / PREFERENCES DIALOG CONTROLLER (UI ONLY)
 * Xử lý giao diện: Mở/đóng panel, chuyển tab Sidebar cây danh mục 2 cột,
 * tìm kiếm lọc danh mục, phím tắt Escape và giữ nguyên popup Thông tin phần mềm.
 */

// DOM Elements
const btn_config_software = document.getElementById("btn-open-software-config");
const btn_close_settings = document.getElementById("close-settings");
const btn_cancel_settings = document.getElementById("btn-pref-cancel");
const btn_apply_settings = document.getElementById("btn-pref-apply");
const btn_ok_settings = document.getElementById("save-settings");
const btn_defaults_settings = document.getElementById("btn-pref-defaults");
const overlay_config_software = document.getElementById("overlay_config_software");

// Header info elements
const pref_header_icon = document.getElementById("pref-header-icon");
const pref_header_title = document.getElementById("pref-header-title");
const pref_header_desc = document.getElementById("pref-header-desc");
const pref_search_input = document.getElementById("pref-search-input");
const pref_tree_menu = document.getElementById("pref-tree-menu");

// Category metadata for content header
const TAB_METADATA = {
    "tab-system-general": {
        icon: "🖥️",
        title: "System — General & View",
        desc: "Cấu hình các tham số vận hành chung, hiển thị và giao diện hệ thống",
    },
    "tab-system-logs": {
        icon: "📁",
        title: "System — Log & Retention",
        desc: "Cấu hình lưu trữ tệp tin nhật ký, hình ảnh phán định và bảng tính Excel",
    },
    "tab-camera-device": {
        icon: "📷",
        title: "Camera & Imaging — Device & Exposure",
        desc: "Thông số kỹ thuật camera công nghiệp, thời gian phơi sáng và FPS",
    },
    "tab-camera-trigger": {
        icon: "⚡",
        title: "Camera & Imaging — Trigger Mode",
        desc: "Cấu hình chế độ kích hoạt chụp bằng phần mềm hoặc tín hiệu xung phần cứng",
    },
    "tab-com-serial": {
        icon: "🔌",
        title: "Communication — Serial COM & Baudrate",
        desc: "Cài đặt thông số truyền thông cổng nối tiếp với bộ điều khiển PLC",
    },
    "tab-com-plc": {
        icon: "🦾",
        title: "Communication — PLC & IAI Limits",
        desc: "Giới hạn an toàn các trục tọa độ cánh tay robot công nghiệp IAI",
    },
    "tab-ai-weld": {
        icon: "🔍",
        title: "AI & Judgment — Weld Line & Skeleton",
        desc: "Tham số mô hình phân đoạn U-Net và giải thuật trích xuất tâm đường hàn",
    },
    "tab-ai-bubbles": {
        icon: "🫧",
        title: "AI & Judgment — Air Bubbles & Defects",
        desc: "Phán định lỗi bọt khí, dị vật nằm trên và ngoài đường hàn",
    },
    "tab-ai-film": {
        icon: "📐",
        title: "AI & Judgment — Film Border & Slit",
        desc: "Mô hình nhận diện màng thấm, viền film và kiểm tra khe hở slit",
    },
    "tab-storage-paths": {
        icon: "💾",
        title: "Storage & Files — Directory Paths",
        desc: "Quản lý phân vùng đĩa và đường dẫn thư mục lưu trữ hệ thống",
    },
    "tab-storage-cleanup": {
        icon: "🧹",
        title: "Storage & Files — Auto Cleanup",
        desc: "Tự động kiểm tra và dọn dẹp dung lượng đĩa tránh đầy bộ nhớ",
    },
    "tab-barcode-scanner": {
        icon: "🏷️",
        title: "Barcode & User — Scanner Settings",
        desc: "Cấu hình máy quét mã vạch sản phẩm qua cổng COM hoặc USB HID",
    },
    "tab-barcode-auth": {
        icon: "👤",
        title: "Barcode & User — User & Roles",
        desc: "Quản lý phân quyền thao tác và bảo vệ thông số chuẩn master",
    },
};

// ==========================================
// MỞ VÀ ĐÓNG MODAL
// ==========================================
function openConfigSoftware() {
    if (overlay_config_software) {
        overlay_config_software.style.display = "flex";
    }
}

function closeConfigSoftware() {
    if (overlay_config_software) {
        overlay_config_software.style.display = "none";
    }
}

if (btn_config_software) {
    btn_config_software.addEventListener("click", openConfigSoftware);
}

if (btn_close_settings) {
    btn_close_settings.addEventListener("click", closeConfigSoftware);
}

if (btn_cancel_settings) {
    btn_cancel_settings.addEventListener("click", closeConfigSoftware);
}

if (btn_ok_settings) {
    btn_ok_settings.addEventListener("click", closeConfigSoftware);
}

// Đóng modal khi nhấn phím Escape
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && overlay_config_software && overlay_config_software.style.display === "flex") {
        closeConfigSoftware();
    }
});

// ==========================================
// CHUYỂN TAB ĐIỀU HƯỚNG SIDEBAR
// ==========================================
function switchTab(tabId) {
    if (!tabId) return;

    // 1. Cập nhật active trong cây menu
    const allNodes = document.querySelectorAll(".pref-tree-node, .pref-tree-subitem");
    allNodes.forEach((node) => {
        if (node.getAttribute("data-tab") === tabId) {
            node.classList.add("active");
            // Mở nhóm cha nếu đang đóng
            const group = node.closest(".pref-tree-group");
            if (group) {
                const sublist = group.querySelector(".pref-tree-sublist");
                const arrow = group.querySelector(".pref-tree-arrow");
                if (sublist) sublist.classList.add("open");
                if (arrow) arrow.classList.add("expanded");
            }
        } else {
            node.classList.remove("active");
        }
    });

    // 2. Ẩn tất cả tab panels và hiển thị tab được chọn
    const allPanels = document.querySelectorAll(".pref-tab-panel");
    allPanels.forEach((panel) => {
        panel.style.display = "none";
    });

    const activePanel = document.getElementById(tabId);
    if (activePanel) {
        activePanel.style.display = "block";
    }

    // 3. Cập nhật header title & desc
    const meta = TAB_METADATA[tabId];
    if (meta) {
        if (pref_header_icon) pref_header_icon.textContent = meta.icon;
        if (pref_header_title) pref_header_title.textContent = meta.title;
        if (pref_header_desc) pref_header_desc.textContent = meta.desc;
    }
}

// Bắt sự kiện click vào các item cây menu
if (pref_tree_menu) {
    pref_tree_menu.addEventListener("click", (e) => {
        // Xử lý click vào mũi tên mở rộng / thu gọn
        const arrow = e.target.closest(".pref-tree-arrow");
        if (arrow) {
            e.stopPropagation();
            const group = arrow.closest(".pref-tree-group");
            const sublist = group ? group.querySelector(".pref-tree-sublist") : null;
            if (sublist) {
                const isOpen = sublist.classList.toggle("open");
                arrow.classList.toggle("expanded", isOpen);
            }
            return;
        }

        // Xử lý click vào node cha hoặc node con
        const item = e.target.closest(".pref-tree-node, .pref-tree-subitem");
        if (item) {
            const tabId = item.getAttribute("data-tab");
            if (tabId) {
                switchTab(tabId);
            } else {
                // Nếu click vào node cha không có tab riêng, mở sublist
                const group = item.closest(".pref-tree-group");
                const sublist = group ? group.querySelector(".pref-tree-sublist") : null;
                const nodeArrow = group ? group.querySelector(".pref-tree-arrow") : null;
                if (sublist) {
                    const isOpen = sublist.classList.toggle("open");
                    if (nodeArrow) nodeArrow.classList.toggle("expanded", isOpen);
                }
            }
        }
    });
}

// ==========================================
// TÌM KIẾM LỌC DANH MỤC TRONG SIDEBAR
// ==========================================
if (pref_search_input) {
    pref_search_input.addEventListener("input", (e) => {
        const query = e.target.value.trim().toLowerCase();
        const groups = document.querySelectorAll(".pref-tree-group");

        groups.forEach((group) => {
            let groupHasMatch = false;
            const parentNode = group.querySelector(".pref-tree-node");
            const subitems = group.querySelectorAll(".pref-tree-subitem");
            const sublist = group.querySelector(".pref-tree-sublist");
            const arrow = group.querySelector(".pref-tree-arrow");

            const parentText = parentNode ? parentNode.textContent.toLowerCase() : "";
            if (parentText.includes(query)) {
                groupHasMatch = true;
            }

            subitems.forEach((sub) => {
                const subText = sub.textContent.toLowerCase();
                if (subText.includes(query) || parentText.includes(query)) {
                    sub.style.display = "flex";
                    groupHasMatch = true;
                } else {
                    sub.style.display = query ? "none" : "flex";
                }
            });

            if (groupHasMatch || !query) {
                group.style.display = "block";
                if (query && sublist) {
                    sublist.classList.add("open");
                    if (arrow) arrow.classList.add("expanded");
                }
            } else {
                group.style.display = "none";
            }
        });
    });
}

// ==========================================
// CÁC NÚT TÁC VỤ GIAO DIỆN (UI FEEDBACK)
// ==========================================
if (btn_apply_settings) {
    btn_apply_settings.addEventListener("click", () => {
        const originText = btn_apply_settings.textContent;
        btn_apply_settings.textContent = "✔ Applied!";
        setTimeout(() => {
            btn_apply_settings.textContent = originText;
        }, 1200);
    });
}

if (btn_defaults_settings) {
    btn_defaults_settings.addEventListener("click", () => {
        const originText = btn_defaults_settings.textContent;
        btn_defaults_settings.textContent = "✔ Restored";
        setTimeout(() => {
            btn_defaults_settings.textContent = originText;
        }, 1200);
    });
}

// ==========================================
// THÔNG TIN PHẦN MỀM (GIỮ NGUYÊN TƯƠNG THÍCH)
// ==========================================
const btn_software_information = document.getElementById("get_infor_software");
const software_information_overlay = document.getElementById("software-information-overlay");
const software_information_content = document.getElementById("software-information-content");
const btn_exit_software_information = document.getElementById("btn_exit_infor_software");

function renderInformationGroup(title, items, includeDetails = false) {
    if (!software_information_content) return;
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
    if (!software_information_overlay || !software_information_content) return;
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
    if (software_information_overlay) {
        software_information_overlay.hidden = true;
    }
}

if (btn_software_information) {
    btn_software_information.addEventListener("click", showSoftwareInformation);
}

if (btn_exit_software_information) {
    btn_exit_software_information.addEventListener("click", hideSoftwareInformation);
}
