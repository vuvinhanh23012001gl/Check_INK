import { EndChippingInspector } from "./end_chipping_item_inspector.js";
import { ModelRectangle } from "../model/model_rectangle.js";

export class ForeignObjectInspector extends EndChippingInspector {
    static NAME = "ForeignObjectInspector";

    /**
     * Quản lý rectangle, ngưỡng và cờ lưu ảnh train của vùng kiểm tra dị vật.
     *
     * @param {ModelRectangle|null} cropRoi Vùng rectangle kiểm tra.
     * @param {number} threshold Ngưỡng PatchCore trong khoảng từ 0 đến 1.
     * @param {boolean} saveRuntimeImages Có lưu ảnh runtime để train lại hay không.
     * @returns {ForeignObjectInspector} Inspector đã khởi tạo.
     * @throws {TypeError} Có thể phát sinh khi cập nhật ROI không phải ModelRectangle.
     */
    constructor(cropRoi = null, threshold = 0, saveRuntimeImages = false) {
        super(cropRoi, threshold, saveRuntimeImages);
    }

    /**
     * Khôi phục dữ liệu inspector dị vật từ cấu hình đã lưu.
     *
     * @param {object|null} data Dữ liệu rectangle, threshold và saveRuntimeImages.
     * @returns {ForeignObjectInspector} Inspector đã khôi phục hoặc inspector rỗng.
     * @throws {TypeError} Có thể phát sinh nếu dữ liệu rectangle sai định dạng.
     */
    static fromDict(data) {
        if (!data) return new ForeignObjectInspector();
        return new ForeignObjectInspector(
            ModelRectangle.fromDict(data),
            Number(data.threshold) || 0,
            data.saveRuntimeImages === true,
        );
    }
}