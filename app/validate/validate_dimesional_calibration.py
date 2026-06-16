class ValidateDimesionalCalibration:
    @staticmethod
    def validate_product_data_pure_python(data: dict) -> tuple[bool, str | dict]:
            """
            Validate dữ liệu bằng Python thuần.
            Output: (True, cleaned_data) hoặc (False, error_message)
            """
            if not isinstance(data, dict):
                return False, "Dữ liệu gốc phải là một Dictionary"
                
            cleaned_data = {}
            required_fields = {
                "lineName": str, "realityMM": (int, float), "captureCount": int,
                "xStart": int, "yStart": int, "xEnd": int, "yEnd": int,
                "coordinateX": (int, float), "coordinateY": (int, float), 
                "coordinateZ": (int, float), "id_item": int
            }
            
            try:
                for product_id, frames in data.items():
                    cleaned_data[str(product_id)] = {}
                    if not isinstance(frames, dict):
                        return False, f"Product {product_id}: Dữ liệu các Frame phải là dict"
                        
                    for frame_id, frame_content in frames.items():
                        if "calculation_parameters" not in frame_content:
                            return False, f"Product {product_id} - Frame {frame_id}: Thiếu key 'calculation_parameters'"
                
                        params = frame_content["calculation_parameters"]
                        if not isinstance(params, dict):
                            return False, f"Product {product_id} - Frame {frame_id}: 'calculation_parameters' phải là dict"
                            
                        validated_params = {}
                        for field, expected_type in required_fields.items():
                            if field not in params:
                                return False, f"Product {product_id} - Frame {frame_id}: Thiếu trường '{field}'"
                                
                            val = params[field]
                            
                            # SỬA TẠI ĐÂY: Chỉ ép kiểu chuỗi số khi trường đó KHÔNG PHẢI là str
                            if isinstance(val, str) and expected_type != str:
                                try:
                                    val = float(val) if (expected_type == (int, float) or expected_type == float) else int(val)
                                except ValueError:
                                    return False, f"Product {product_id} - Frame {frame_id}: Trường '{field}' không thể ép kiểu sang số"
                                    
                            if not isinstance(val, expected_type):
                                return False, f"Product {product_id} - Frame {frame_id}: Trường '{field}' sai kiểu dữ liệu"
                                
                            validated_params[field] = val
                            
                        cleaned_data[str(product_id)][str(frame_id)] = {
                            "calculation_parameters": validated_params
                        }  
                return True, cleaned_data
            except Exception as e:
                return False, f"Lỗi hệ thống khi validate: {str(e)}"