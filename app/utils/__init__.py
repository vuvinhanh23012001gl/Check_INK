from .folder import Folder
from .opencv_tool import Tool_OpenCv2
from .logic import Logic
from .aggregate_function import Aggregate
from .queue_fuc import Queue_All




obj_queue =  Queue_All()
SIZE_QUEUE_MANAGE_LOG = 500
name_queue_manage  = "manage"
obj_queue.create_queue(name_queue_manage,SIZE_QUEUE_MANAGE_LOG)


type_capture = "CaptureProduct"
log_capture = "log_CaptureProduct"
log_home = "log_Home"
log_calibration = "log_calibration"




datatype_Home = "data_output_judment"
data_output_judment =  "data_output_judment"
datatype_Calibration = "data_calibration"



SIZE_QUEUE_LOG_SEND_CLIENT = 500
name_queue_log_client  = "log_client"
obj_queue.create_queue(name_queue_log_client,SIZE_QUEUE_LOG_SEND_CLIENT)

#Queue này dùng để chụp lấy ảnh  từ chụp
SIZE_QUEUE_IMG_CAPTURE = 500
name_queue_process_capture  = "process_capture"
obj_queue.create_queue(name_queue_process_capture,SIZE_QUEUE_IMG_CAPTURE)



SIZE_QUEUE_DATA_SEND_CLIENT = 500
name_queue_data_client  = "data_send_client"
obj_queue.create_queue(name_queue_data_client,SIZE_QUEUE_DATA_SEND_CLIENT)

SIZE_QUEUE_IMG_CALIBRATION = 201
name_queue_img_calibration  = "queue_calibration"
obj_queue.create_queue(name_queue_img_calibration,SIZE_QUEUE_IMG_CALIBRATION)
