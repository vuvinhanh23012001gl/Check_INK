# from pathlib import Path
# import sys
# sys.path.append(str(Path(__file__).resolve().parents[3]))


from app.config import PATH_FEATUERES_CFG_CAM 
import stapipy as st
import cv2
import numpy as np
import threading
import time 
import os

class Camera():

    DISPLAY_RESIZE_FACTOR = 1.0
    ERRO_TIMEOUT = "ErroTimeOutCapture"
    TIMEOUT_WAIT_NEW_FRAME  = 10     # số giây để reconnect lại
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

        # Viết chụp ảnh triger bằng Camera
        self.nodemap = None
        self.trigger_software = None
        self.trigger_mode = False

        self.init()

        
    def display_captured_image(self, img, window_name="Captured Image", wait_time=2000):
        """
        Hiển thị ảnh sau khi chụp bằng OpenCV.
        :param img: Khung hình (numpy array) cần hiển thị.
        :param window_name: Tên của cửa sổ hiển thị.
        :param wait_time: Thời gian hiển thị ảnh tính bằng mili-giây (ms). 
                          Nếu truyền 0, cửa sổ sẽ giữ nguyên cho đến khi nhấn phím bất kỳ.
        """
        if img is None:
            print("Không có ảnh để hiển thị (img is None)")
            return False
        
        try:
            # Tạo cửa sổ có thể thay đổi kích thước nếu ảnh quá lớn
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.imshow(window_name, img)
            
            print(f"Đang hiển thị ảnh trong {wait_time/1000} giây...")
            cv2.waitKey(wait_time)
            
            # Đóng cửa sổ sau khi hết thời gian chờ
            cv2.destroyWindow(window_name)
            return True
        except Exception as e:
            print("Lỗi khi hiển thị ảnh:", e)
            return False
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
            # nodemap = self.st_device.remote_port.nodemap  #cu
            self.nodemap = self.st_device.remote_port.nodemap
            if os.path.exists(PATH_FEATUERES_CFG_CAM):
                print("Tìm thấy file mô hình")
                featurebag = st.create_featurebag()
                featurebag.store_file_to_bag(PATH_FEATUERES_CFG_CAM)
                featurebag.load(self.nodemap, verify=True)
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
            

    def enable_software_trigger(self):
        try:
            try:
                self.set_enumeration(
                    "TriggerSelector",
                    "FrameStart"
                )
            except:
                self.set_enumeration(
                    "TriggerSelector",
                    "ExposureStart"
                )
            self.set_enumeration(
                "TriggerMode",
                "On"
            )
            self.set_enumeration(
                "TriggerSource",
                "Software"
            )
            self.trigger_software = st.PyICommand(
                self.nodemap.get_node(
                    "TriggerSoftware"
                )
            )
            self.trigger_mode = True
            print("Software Trigger Enabled")
            return True
        except Exception as e:
            print("Enable Trigger Error:", e)
            return False 
        
    def disable_software_trigger(self):
        try:
            self.set_enumeration(
                "TriggerMode",
                "Off"
            )
            self.trigger_mode = False
            print("Software Trigger Disabled")
        except Exception as e:
            print("Disable Trigger Error:", e)


    def send_trigger(self):
        if not self.trigger_mode:
            return False
        try:
            self.trigger_software.execute()
            return True
        except Exception as e:
            print("Trigger Error:", e)
            return False
        
    def set_enumeration(self, enum_name, entry_name):
        enum_node = st.PyIEnumeration(
            self.nodemap.get_node(enum_name)
        )
        entry_node = st.PyIEnumEntry(
            enum_node[entry_name]
        )
        enum_node.set_entry_value(entry_node)

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
        try:
            self.disable_software_trigger()
            print("[Release] Trigger thành công.")
        except:
            print("[Release] Trigger thất bại.")

        # 4. Reset state nội bộ
        self._image = None
        self._captured_image = None
        self._capture_one = False
        self._capture_event.clear()

        print("---Release camera thành công -- ")


    def capture_once(self, timeout=1):
        with self._lock_capture:
            self._captured_image = None
            self._capture_one = True
        self._capture_event.clear()
        if self.trigger_mode:
            if not self.send_trigger():
                self._capture_one = False
                return False, "TriggerError"
        ok = self._capture_event.wait(timeout)
        if not ok:
            self._capture_one = False
            print("Capture Error image timeout")
            return False, Camera.ERRO_TIMEOUT
        return True, self._captured_image
    


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
    

    def capture_image_trigger(self, folder_path, image_name, timeout=2):
        """
        Bật trigger -> chụp 1 ảnh -> lưu ảnh -> tắt trigger
        Return:
            (status, image, path_or_error)
            Success:
                True, img, image_path
            Fail:
                False, None, error_message
        """
        try:
            os.makedirs(folder_path, exist_ok=True)
            image_path = os.path.join(
                folder_path,
                image_name
            )
            print("Enable Trigger...")
            status_open_trigger = self.enable_software_trigger()
            if not status_open_trigger:
                return False, None, "EnableTriggerFail"
            with self._lock_capture:
                self._captured_image = None
                self._capture_one = True
            self._capture_event.clear()
            print("Send Trigger...")
            status_send_trigger = self.send_trigger()
            if not status_send_trigger:
                self._capture_one = False
                return False, None, "SendTriggerFail"
            ok = self._capture_event.wait(timeout)
            if not ok:
                self._capture_one = False
                return False, None, Camera.ERRO_TIMEOUT
            if self._captured_image is None:
                return False, None, "ImageIsNone"
            img = self._captured_image.copy()
            if os.path.isfile(image_path):
                os.remove(image_path)
            save_status = cv2.imwrite(image_path, img)
            if not save_status:
                return False, None, "SaveImageFail"
            print("Save Image OK:", image_path)
            return True, img, image_path
        except Exception as e:
            print("capture_image_trigger error:", e)
            return False, None, str(e)
        finally:
            try:
                self.disable_software_trigger()
                print("Disable Trigger OK")
            except Exception as e:
                print("Disable Trigger Error:", e)
        

    
    # def open_trigger(self):
    #     # Ham nay vi du để bật mode trigger
    #     status_open_trigger = self.enable_software_trigger()
    #     send_trigger = self.send_trigger()
    #     ok, img = self.capture_once(timeout=2)
    #     print("status_open_trigger",status_open_trigger,"send_trigger",send_trigger)
    #     if ok:
    #         cv2.imwrite("test.jpg", img)

# c1 = Camera()
# while True:
#     img = c1.image
#     if img is not None:
#         # c1.open_trigger()
#         cv2.imshow("image", img)
#     if c1.camera_lost:
#         print("Main: reconnect camera")
#         c1.release()
#         time.sleep(1)
#         c1.refesh_data()
#         c1.init()
#     if cv2.waitKey(1) & 0xFF == 27:
#         break
