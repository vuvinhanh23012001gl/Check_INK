import stapipy as st
import cv2
import numpy as np
import threading
import os

from app.config import PATH_FEATUERES_CFG_CAM


class Camera:

    ERRO_TIMEOUT = "ErroTimeOutCapture"

    def __init__(self):

        self.st_device = None
        self.st_datastream = None
        self.nodemap = None

        self.trigger_software = None

        self._image = None
        self._lock = threading.Lock()

        self._capture_one = False
        self._captured_image = None

        self._lock_capture = threading.Lock()
        self._capture_event = threading.Event()

        self.init()

    def set_enumeration(self, enum_name, entry_name):

        enum_node = st.PyIEnumeration(
            self.nodemap.get_node(enum_name)
        )

        entry_node = st.PyIEnumEntry(
            enum_node[entry_name]
        )

        enum_node.set_entry_value(entry_node)

    def enable_software_trigger(self):

        try:
            self.set_enumeration(
                "TriggerSelector",
                "FrameStart"
            )
        except Exception:
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

        print("Software Trigger Enabled")

    def software_trigger(self):

        if self.trigger_software:
            self.trigger_software.execute()

    def init(self):

        print("--------- Init Camera -------")

        st.initialize()

        st_system = st.create_system()

        self.st_device = st_system.create_first_device()

        print(
            "Device =",
            self.st_device.info.display_name
        )

        self.st_datastream = (
            self.st_device.create_datastream()
        )

        self.nodemap = (
            self.st_device.remote_port.nodemap
        )

        if os.path.exists(PATH_FEATUERES_CFG_CAM):

            featurebag = st.create_featurebag()

            featurebag.store_file_to_bag(
                PATH_FEATUERES_CFG_CAM
            )

            featurebag.load(
                self.nodemap,
                verify=True
            )

            print(
                "Camera config loaded complete"
            )

        self.enable_software_trigger()

        self.st_datastream.register_callback(
            self.datastream_callback
        )

        self.st_datastream.start_acquisition()

        self.st_device.acquisition_start()

        print("Camera Ready")

    @property
    def image(self):

        with self._lock:

            if self._image is None:
                return None

            return self._image.copy()

    def datastream_callback(
        self,
        handle=None,
        context=None
    ):

        try:

            st_datastream = handle.module

            with st_datastream.retrieve_buffer() \
                    as st_buffer:

                if not st_buffer.info.is_image_present:
                    return

                st_image = st_buffer.get_image()

                pixel_format = (
                    st_image.pixel_format
                )

                pixel_info = (
                    st.get_pixel_format_info(
                        pixel_format
                    )
                )

                if not (
                    pixel_info.is_mono
                    or
                    pixel_info.is_bayer
                ):
                    return

                data = st_image.get_image_data()

                if (
                    pixel_info
                    .each_component_total_bit_count
                    > 8
                ):

                    img = np.frombuffer(
                        data,
                        np.uint16
                    )

                    division = pow(
                        2,
                        pixel_info
                        .each_component_valid_bit_count
                        - 8
                    )

                    img = (
                        img / division
                    ).astype(np.uint8)

                else:

                    img = np.frombuffer(
                        data,
                        np.uint8
                    )

                img = img.reshape(
                    st_image.height,
                    st_image.width,
                    1
                )

                if pixel_info.is_bayer:

                    bayer_type = (
                        pixel_info
                        .get_pixel_color_filter()
                    )

                    if (
                        bayer_type
                        ==
                        st.EStPixelColorFilter.BayerRG
                    ):

                        img = cv2.cvtColor(
                            img,
                            cv2.COLOR_BAYER_RG2RGB
                        )

                    elif (
                        bayer_type
                        ==
                        st.EStPixelColorFilter.BayerGR
                    ):

                        img = cv2.cvtColor(
                            img,
                            cv2.COLOR_BAYER_GR2RGB
                        )

                    elif (
                        bayer_type
                        ==
                        st.EStPixelColorFilter.BayerGB
                    ):

                        img = cv2.cvtColor(
                            img,
                            cv2.COLOR_BAYER_GB2RGB
                        )

                    elif (
                        bayer_type
                        ==
                        st.EStPixelColorFilter.BayerBG
                    ):

                        img = cv2.cvtColor(
                            img,
                            cv2.COLOR_BAYER_BG2RGB
                        )

                with self._lock:
                    self._image = img.copy()

                with self._lock_capture:

                    if self._capture_one:

                        self._captured_image = (
                            img.copy()
                        )

                        self._capture_one = False

                        self._capture_event.set()

        except Exception as e:

            print(
                "datastream_callback error:",
                e
            )

    def capture_once(
        self,
        timeout=2
    ):

        with self._lock_capture:

            self._captured_image = None

            self._capture_one = True

        self._capture_event.clear()

        self.software_trigger()

        ok = self._capture_event.wait(
            timeout
        )

        if not ok:

            self._capture_one = False

            return (
                False,
                Camera.ERRO_TIMEOUT
            )

        return (
            True,
            self._captured_image
        )

    def capture_image_path(
        self,
        path,
        timeout=2
    ):

        ok, img = self.capture_once(
            timeout
        )

        if not ok:
            return False

        return cv2.imwrite(path, img)

    def release(self):

        try:

            self.set_enumeration(
                "TriggerMode",
                "Off"
            )

        except Exception:
            pass

        try:

            self.st_device.acquisition_stop()

        except Exception:
            pass

        try:

            self.st_datastream.stop_acquisition()

        except Exception:
            pass

        try:

            st.terminate()

        except Exception:
            pass

        print("Camera Released")

cam = Camera()

while True:
    ok, img = cam.capture_once()
    if ok:
        cv2.imshow(
            "Capture",
            img
        )
    key = cv2.waitKey(0)

    if key == 27:
        break

cam.release()
cv2.destroyAllWindows()