from .inference_unet import InferenceUnet
import numpy as np
import cv2
from skimage.morphology import skeletonize

class PredictionUnet:
    
    def __init__(self,infeUnet:InferenceUnet):
        self.infeUnet = infeUnet


    def run(self,img):
        mask = self.infeUnet.predict(img)
        mask_clean = self.clean_mask_opening(mask,self.infeUnet.config.kernel) # Loc nhieu xung quanh, lam sach mask
        polygon  = self.find_polygons(mask_clean,self.infeUnet.config.epsilon_ratio,self.infeUnet.config.min_area)  #Chinh lai duong polygon
        self.draw_polygons(img,polygon)
        self.show_mask(mask_clean)
        img, lines = self.extract_perpendicular_lines(
            img,
            polygon,
            step=1,
            line_length=20
        )

        img = self.draw_perpendicular_lines(img, lines)
        self.show_img(img)
        return  mask_clean ,polygon
        


    def clean_mask_opening(self, mask, kernel_size=3, iterations=1):
        """
            Làm sạch mask bằng phép Morphology Opening (Erosion + Dilation)
            Parameters:
                mask (np.ndarray): Ảnh mask nhị phân (0 hoặc 255)
                kernel_size (int): Kích thước kernel (ví dụ: 3 → kernel 3x3)
                iterations (int): Số lần lặp phép morphology
            Returns:
                np.ndarray: Mask đã được làm sạch
        """
        mask = mask.astype(np.uint8)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        mask_clean = cv2.morphologyEx(
                mask,
                cv2.MORPH_OPEN,
                kernel,
                iterations=iterations
            )
        return mask_clean
    

    def show_mask(self, mask, window_name="Mask"):
        """
        Hiển thị mask đơn giản
        """
        mask = mask.astype(np.uint8)
        cv2.imshow(window_name, mask)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    def show_img(self,image, window_name="Image"):
        cv2.imshow(window_name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()



    
    def find_polygons(
        self,
        mask,
        epsilon_ratio=0.002,
        min_area=100
    ):
        """
        Tìm tất cả polygon trong mask.

        Parameters
        ----------
        mask : np.ndarray
            Mask nhị phân (0 hoặc 255)

        epsilon_ratio : float
            Tỷ lệ xấp xỉ polygon

        min_area : int
            Diện tích tối thiểu của contour

        Returns
        -------
        list[np.ndarray]
            Danh sách polygon
        """
        mask = mask.astype(np.uint8)
        contours, hierarchy = cv2.findContours(
            mask,
            cv2.RETR_TREE,          # Lấy cả contour ngoài và trong
            cv2.CHAIN_APPROX_NONE
        )
        polygons = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area:
                continue
            epsilon = epsilon_ratio * cv2.arcLength(cnt, True)
            poly = cv2.approxPolyDP(
                cnt,
                epsilon,
                True
            )
            polygons.append(poly)
        return polygons
    
    def draw_polygons(
        self,
        image,
        polygons,
        color=(0,255,0),
        thickness=2
    ):
        for poly in polygons:
            cv2.polylines(
                image,
                [poly],
                True,
                color,
                thickness
            )

        return image
    
    def extract_perpendicular_lines(
        self,
        image,
        polygons,
        step=1,
        line_length=30
    ):
        """
        Trích các đường vuông góc (normal lines) từ polygon theo bước sampling
        """

        h, w = image.shape[:2]
        lines = []

        for poly in polygons:
            pts = poly.reshape(-1, 2)
            n = len(pts)

            if n < 3:
                continue

            for i in range(0, n, step):

                # lấy điểm trước - hiện tại - sau (giảm nhiễu)
                p_prev = pts[i - 1]
                p_next = pts[(i + 1) % n]

                # tangent vector ổn định hơn
                dx = p_next[0] - p_prev[0]
                dy = p_next[1] - p_prev[1]

                norm = np.sqrt(dx * dx + dy * dy) + 1e-6

                tx = dx / norm
                ty = dy / norm

                # vector vuông góc
                nx = -ty
                ny = tx

                # điểm trung tâm
                cx, cy = pts[i]

                # 2 đầu đoạn vuông góc
                x1 = int(cx - nx * line_length)
                y1 = int(cy - ny * line_length)
                x2 = int(cx + nx * line_length)
                y2 = int(cy + ny * line_length)

                # check trong image
                if (0 <= x1 < w and 0 <= x2 < w and
                    0 <= y1 < h and 0 <= y2 < h):

                    lines.append(((x1, y1), (x2, y2)))

        return image, lines
    
    def draw_perpendicular_lines(
        self,
        image,
        lines,
        color=(0, 0, 255),
        thickness=1
    ):
        """
        Vẽ các đường vuông góc đã được extract
        Parameters:
            image: ảnh gốc
            lines: list[((x1,y1),(x2,y2))]
        """

        for (p1, p2) in lines:
            cv2.line(image, p1, p2, color, thickness)

        return image