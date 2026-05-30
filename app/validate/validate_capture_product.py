class ValidateCaptureProduct:
    @staticmethod
    def validate_erase_item_img(id,frame_id,point_id):
        try:
            id = int(id)
            frame_id = int(frame_id)
            point_id = int(point_id)
            return id >= 0 and point_id >= 0 and point_id >= 0
        except (ValueError, TypeError):
            return False
        
    @staticmethod
    def validate_erase_frame(id,frame_id):
        try:
            id = int(id)
            frame_id = int(frame_id)
            return id >= 0 and frame_id >= 0 
        except (ValueError, TypeError):
            return False