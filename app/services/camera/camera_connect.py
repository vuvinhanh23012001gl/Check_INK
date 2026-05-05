# from pathlib import Path
# import sys
# sys.path.append(str(Path(__file__).resolve().parents[3]))


from app.storage.config import PATH_FEATUERES_CFG_CAM 
import stapipy as st
import cv2
import numpy as np
import threading
import time 
import os

class Camera():

    DISPLAY_RESIZE_FACTOR = 1.0
    ERRO_TIMEOUT = "ErroTimeOutCapture"
    TIMEOUT_WAIT_NEW_FRAME  = 1     # số giây để reconnect lại
    TIMEDELAY_TASK_THREAD_CAMERA = 0.1

    def __init__(self):

        self.camera_lost = False

        self.lock_connect =  threading.Lock()
        self._isConnect = False
        self._last_time = time.time()
        
        self.open_task_camera = True
        self.thread_camera = None
     
        self.st_device = None
        self.st_datastream = None
        self._image = None         # Image buffer
        self._lock = threading.Lock()

        self._lock_capture = threading.Lock()
        self._capture_event  = threading.Event()
        self._capture_one = False    # Flag to capture one image
        self._captured_image = None   # Captured image buffer

        self.init()

    def refesh_data(self):
            
            self.camera_lost = False
            self.lock_connect =  threading.Lock()
            self._isConnect = False

            self._last_time = time.time()
            self.open_task_camera = True
            self.thread_camera = None
        
            self.st_device = None
            self.st_datastream = None
            self._image = None         # Image buffer
            self._lock = threading.Lock()

            self._lock_capture = threading.Lock()
            self._capture_event  = threading.Event()
            self._capture_one = False    # Flag to capture one image
            self._captured_image = None   # Captured image buffer


    def init(self):
        try:
            print("--------- Init Camera -------")
            st.initialize()
            st_system = st.create_system()
            self.st_device = st_system.create_first_device()
            self.st_datastream = self.st_device .create_datastream()
            print('Device=', self.st_device.info.display_name)
            nodemap = self.st_device.remote_port.nodemap
            if os.path.exists(PATH_FEATUERES_CFG_CAM):
                print("Tìm thấy file mô hình")
                featurebag = st.create_featurebag()
                featurebag.store_file_to_bag(PATH_FEATUERES_CFG_CAM)
                featurebag.load(nodemap, verify=True)
                print("Camera config loaded compelete")
                self.create_task_camera()
                self.camera_lost = False
                print("--------- Init Camera thành công -------")
            else:
                print("Không tìm thấy file mô hình features.cfg")
                print("--------- Init Camera thất bại -------")
                
        except:
            self.camera_lost = True
            print("--------- Init Camera thất bại -------")
            


    def get_is_connect(self):
        with self.lock_connect:
            return self._isConnect   
        
    def set_is_connect(self, value: bool):
        with self.lock_connect:
            self._isConnect = value


    def create_task_camera(self):
        self.open_task_camera =  True
        self.thread_camera = threading.Thread(target=self.run,daemon=True)
        self.thread_camera.start()


    def release(self):
        print("--Release camera -- ")
        try:
            self.open_task_camera = False
            if self.thread_camera and self.thread_camera.is_alive():
                self.thread_camera.join()
            self.thread_camera = None
        except Exception as e:
            print("[Release] Stop thread error:", e)
        # 1. Ngắt callback + stop acquisition (DataStream)
        try:
            if self.st_datastream:
                try:
                    # Nếu SDK hỗ trợ unregister thì gọi
                    self.st_datastream.unregister_callback()
                except Exception:
                    pass

                try:
                    self.st_datastream.stop_acquisition()
                except Exception:
                    pass

                self.st_datastream = None
        except Exception as e:
            print("[Release] Datastream error:", e)
        # 2. Stop acquisition phía device (camera)
        try:
            if self.st_device:
                try:
                    self.st_device.acquisition_stop()
                except Exception:
                    pass
                self.st_device = None
        except Exception as e:
            print("[Release] Device error:", e)
        # 3. Terminate StApi (BẮT BUỘC)
        try:
            st.terminate()
            print("[Camera] StApi terminated")
        except Exception as e:
            print("[Release] StApi terminate error:", e)

        # 4. Reset state nội bộ
        self._image = None
        self._captured_image = None
        self._capture_one = False
        self._capture_event.clear()

        print("---Release camera thành công -- ")



    def capture_once(self,timeout = 1):
        """Chụp ảnh một lần trả về (True,ảnh) nếu chụp thành công ngược lại (False, "ErroTimeOutCapture")"""
        with self._lock_capture:
            self._captured_image = None
            self._capture_one = True
        self._capture_event.clear()
        ok = self._capture_event.wait(timeout)
        if not ok:
            print("Capture Error image timeout")
            return False,Camera.ERRO_TIMEOUT
        # cv2.imwrite("captured_image.jpg",self._captured_image)
        return True,self._captured_image
    


    def capture_image_path(self, path, timeout=1):
        """Trả về True nếu chụp & lưu ảnh thành công"""
        status_capture, img = self.capture_once(timeout=timeout)
        if not status_capture:
            return False
        if img is None:
            print("Capture error: image is None")
            return False
        try:
            if os.path.isfile(path):
                os.remove(path)
            ok = cv2.imwrite(path, img)
            if not ok:
                print("Save image failed:", path)
                return False
        except Exception as e:
            print("Exception while saving image:", e)
            return False
        return True



    @property
    def image(self):
        duplicate = None
        self._lock.acquire()
        if self._image is not None:
            duplicate = self._image.copy()
        self._lock.release()
        return duplicate
    



    def datastream_callback(self, handle=None, context=None):
        """
        Callback to handle events from DataStream.

        :param handle: handle that trigger the callback.
        :param context: user data passed on during callback registration.
        """
        st_datastream = handle.module
        if st_datastream:
            with st_datastream.retrieve_buffer() as st_buffer:
                # Check if the acquired data contains image data.
                if st_buffer.info.is_image_present:
                    # Create an image object.
                    st_image = st_buffer.get_image()

                    # Check the pixelformat of the input image.
                    pixel_format = st_image.pixel_format
                    pixel_format_info = st.get_pixel_format_info(pixel_format)

                    # Only mono or bayer is processed.
                    if not(pixel_format_info.is_mono or
                           pixel_format_info.is_bayer):
                        return

                    # Get raw image data.
                    data = st_image.get_image_data()

                    # Perform pixel value scaling if each pixel component is
                    # larger than 8bit. Example: 10bit Bayer/Mono, 12bit, etc.
                    if pixel_format_info.each_component_total_bit_count > 8:
                        nparr = np.frombuffer(data, np.uint16)
                        division = pow(2, pixel_format_info
                                       .each_component_valid_bit_count - 8)
                        nparr = (nparr / division).astype('uint8')
                    else:
                        nparr = np.frombuffer(data, np.uint8)

                    # Process image for display.
                    nparr = nparr.reshape(st_image.height, st_image.width, 1)

                    # Perform color conversion for Bayer.
                    if pixel_format_info.is_bayer:
                        bayer_type = pixel_format_info.get_pixel_color_filter()
                        if bayer_type == st.EStPixelColorFilter.BayerRG:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_RG2RGB)
                        elif bayer_type == st.EStPixelColorFilter.BayerGR:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_GR2RGB)
                        elif bayer_type == st.EStPixelColorFilter.BayerGB:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_GB2RGB)
                        elif bayer_type == st.EStPixelColorFilter.BayerBG:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_BG2RGB)

                    # Resize image and store to self._image.
                    nparr = cv2.resize(nparr, None,
                                       fx=Camera.DISPLAY_RESIZE_FACTOR,
                                       fy=Camera.DISPLAY_RESIZE_FACTOR)
                    self._lock.acquire()
                    self._image = nparr
                    self._lock.release()
                    self._last_time =  time.time()
                    self.set_is_connect(True)
                    with self._lock_capture:
                        if self._capture_one:
                            self._captured_image = nparr.copy()
                            self._capture_one = False
                            self._capture_event.set()

    
    def run(self):
        cb_func = self.datastream_callback
        self.st_datastream.register_callback(cb_func)
        self.st_datastream.start_acquisition()
        self.st_device.acquisition_start()
        print("---Camera thread started----")
        while self.open_task_camera:
            if time.time() - self._last_time > Camera.TIMEOUT_WAIT_NEW_FRAME:
                print("Camera LOST")
                self.set_is_connect(False)
                self.camera_lost = True
                break
            time.sleep(Camera.TIMEDELAY_TASK_THREAD_CAMERA)


    def get_device_info(self):
        if self.st_device is None:
            return None
        info = self.st_device.info
        print("===== DEVICE INFO =====")
        print("Display name        :", info.display_name)
        print("Model               :", info.model)
        print("Vendor              :", info.vendor)
        print("Serial number       :", info.serial_number)
        print("Device ID           :", info.device_id)
        print("TL type             :", info.tl_type)
        print("User defined name   :", info.user_defined_name)
        print("Version             :", info.version)
        print("Access status       :", info.access_status)
        print("Timestamp frequency :", info.timestamp_frequency)


    def get_device_info_dict(self):
        if self.st_device is None:
            return None
        info = self.st_device.info
        return {
            "display_name": info.display_name,
            "model": info.model,
            "vendor": info.vendor,
            "serial_number": info.serial_number,
            "device_id": info.device_id,
            "tl_type": info.tl_type,
            "user_defined_name": info.user_defined_name,
            "version": info.version,
            "access_status": info.access_status,
            "timestamp_frequency": info.timestamp_frequency,
        }
    
# c1 = Camera()
# while True:
#     img = c1.image
#     if img is not None:
#         cv2.imshow("image", img)
#     if c1.camera_lost:
#         print("Main: reconnect camera")
#         c1.release()
#         time.sleep(1)
#         c1.refesh_data()
#         c1.init()
#     if cv2.waitKey(1) & 0xFF == 27:
#         break
