import os
import threading

import av
import cv2
import streamlit as st

from streamlit_webrtc import webrtc_streamer

from .challenge import LivenessChallenge


class LiveLivenessProcessor:

    def __init__(self):

        self.lock = threading.Lock()

        self.challenge = LivenessChallenge()

        self.latest_result = {
            "face_detected": False,
            "eye_aspect_ratio": None,
            "face_center": None,
            "blink_detected": False,
            "blink_count": 0,
            "head_left": False,
            "head_right": False,
            "challenge_passed": False,
        }

        self.landmarker = None

        self.initialized = False

        self.initialization_error = None

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------

    def reset(self):

        with self.lock:

            self.challenge.reset()

            self.latest_result = {
                "face_detected": False,
                "eye_aspect_ratio": None,
                "face_center": None,
                "blink_detected": False,
                "blink_count": 0,
                "head_left": False,
                "head_right": False,
                "challenge_passed": False,
            }

    # ---------------------------------------------------------
    # FIND MEDIAPIPE MODEL
    # ---------------------------------------------------------

    def find_model(self):

        candidates = [

            os.path.join(
                "models",
                "face_landmarker.task"
            ),

            os.path.join(
                "liveness",
                "face_landmarker.task"
            ),

            os.path.join(
                "data",
                "face_landmarker.task"
            ),

        ]

        for path in candidates:

            if os.path.exists(path):
                return path

        return None

    # ---------------------------------------------------------
    # INITIALIZE MEDIAPIPE
    # ---------------------------------------------------------

    def initialize(self):

        if self.initialized:
            return True

        try:

            import mediapipe as mp

            from mediapipe.tasks import python

            from mediapipe.tasks.python import vision

            model_path = self.find_model()

            if model_path is None:

                self.initialization_error = (
                    "face_landmarker.task was not found. "
                    "Put it inside E:\\interview-coach\\models"
                )

                return False

            base_options = (
                python.BaseOptions(
                    model_asset_path=model_path
                )
            )

            options = (
                vision.FaceLandmarkerOptions(
                    base_options=base_options,

                    running_mode=(
                        vision.RunningMode.IMAGE
                    ),

                    num_faces=1,

                    min_face_detection_confidence=0.5,

                    min_face_presence_confidence=0.5,

                    min_tracking_confidence=0.5,
                )
            )

            self.landmarker = (
                vision.FaceLandmarker
                .create_from_options(
                    options
                )
            )

            self.initialized = True

            return True

        except Exception as e:

            self.initialization_error = str(e)

            print(
                "MediaPipe initialization error:",
                e
            )

            return False

    # ---------------------------------------------------------
    # PROCESS FRAME
    # ---------------------------------------------------------

    def process_frame(self, frame):

        if not self.initialize():

            return frame

        try:

            image = frame.to_ndarray(
                format="bgr24"
            )

            rgb_image = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2RGB
            )

            import mediapipe as mp

            mp_image = mp.Image(
                image_format=(
                    mp.ImageFormat.SRGB
                ),
                data=rgb_image
            )

            result = self.landmarker.detect(
                mp_image
            )

            if result.face_landmarks:

                landmarks = (
                    result.face_landmarks[0]
                )

                challenge_result = (
                    self.challenge.process(
                        landmarks
                    )
                )

                with self.lock:

                    self.latest_result = (
                        challenge_result
                    )

            else:

                with self.lock:

                    self.latest_result = {
                        "face_detected": False,

                        "eye_aspect_ratio": None,

                        "face_center": None,

                        "blink_detected": False,

                        "blink_count": (
                            self.challenge.blink_count
                        ),

                        "head_left": (
                            self.challenge.head_left
                        ),

                        "head_right": (
                            self.challenge.head_right
                        ),

                        "challenge_passed": False,
                    }

            # Draw status
            self.draw_status(
                image
            )

            return av.VideoFrame.from_ndarray(
                image,
                format="bgr24"
            )

        except Exception as e:

            print(
                "Frame processing error:",
                e
            )

            return frame

    # ---------------------------------------------------------
    # DRAW STATUS
    # ---------------------------------------------------------

    def draw_status(self, image):

        with self.lock:

            result = dict(
                self.latest_result
            )

        if result["challenge_passed"]:

            text = "LIVENESS PASSED"

            color = (
                0,
                255,
                0
            )

        elif not result["face_detected"]:

            text = "FACE NOT DETECTED"

            color = (
                0,
                0,
                255
            )

        else:

            text = "LIVENESS CHECKING"

            color = (
                0,
                255,
                255
            )

        cv2.rectangle(
            image,
            (10, 10),
            (460, 65),
            (25, 25, 25),
            -1
        )

        cv2.putText(
            image,
            text,
            (25, 48),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )

    # ---------------------------------------------------------
    # GET RESULT
    # ---------------------------------------------------------

    def get_result(self):

        with self.lock:

            return dict(
                self.latest_result
            )


# =============================================================
# STREAMLIT CAMERA
# =============================================================

def render_live_camera():

    if (
        "liveness_processor"
        not in st.session_state
    ):

        st.session_state.liveness_processor = (
            LiveLivenessProcessor()
        )

    processor = (
        st.session_state
        .liveness_processor
    )

    ctx = webrtc_streamer(

        key="interview-live-camera",

        video_frame_callback=(
            processor.process_frame
        ),

        media_stream_constraints={
            "video": True,
            "audio": False,
        },

        async_processing=True,
    )

    return processor, ctx