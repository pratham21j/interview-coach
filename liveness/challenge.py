import os
import cv2
import math
import mediapipe as mp


class LivenessChallenge:
    """
    Liveness challenge using MediaPipe Tasks API.

    Compatible with MediaPipe 1.0.1.
    Does NOT use mp.solutions.
    """

    def __init__(self, model_path=None):

        if model_path is None:
            # Project root:
            # E:\interview-coach\face_landmarker.task
            project_root = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )

            model_path = os.path.join(
                project_root,
                "face_landmarker.task"
            )

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Face landmarker model not found:\n{model_path}\n\n"
                "Put face_landmarker.task in the project root."
            )

        self.model_path = model_path

        # MediaPipe Tasks API
        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        RunningMode = mp.tasks.vision.RunningMode

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=self.model_path
            ),
            running_mode=RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=False,
        )

        self.landmarker = FaceLandmarker.create_from_options(options)

        # Previous face position
        self.previous_center = None

        # Baseline position
        self.baseline_center = None

        # Blink state
        self.was_eye_closed = False

        # Challenge state
        self.blink_count = 0
        self.movement_count = 0

        self.movement_threshold = 0.045

    # ---------------------------------------------------------
    # Calculate Eye Aspect Ratio
    # ---------------------------------------------------------

    def _distance(self, p1, p2):
        return math.sqrt(
            (p1.x - p2.x) ** 2 +
            (p1.y - p2.y) ** 2
        )

    def _eye_aspect_ratio(self, landmarks):

        # MediaPipe eye landmark indexes
        left = [33, 160, 158, 133, 153, 144]
        right = [362, 385, 387, 263, 373, 380]

        try:

            left_ear = (
                self._distance(landmarks[left[1]], landmarks[left[5]])
                +
                self._distance(landmarks[left[2]], landmarks[left[4]])
            ) / (
                2.0 *
                self._distance(landmarks[left[0]], landmarks[left[3]])
            )

            right_ear = (
                self._distance(landmarks[right[1]], landmarks[right[5]])
                +
                self._distance(landmarks[right[2]], landmarks[right[4]])
            ) / (
                2.0 *
                self._distance(landmarks[right[0]], landmarks[right[3]])
            )

            return (left_ear + right_ear) / 2.0

        except Exception:
            return 0.30

    # ---------------------------------------------------------
    # Process frame
    # ---------------------------------------------------------

    def process_frame(self, frame):

        if frame is None:
            return {
                "face_detected": False,
                "eye_aspect_ratio": 0.0,
                "blink_detected": False,
                "movement_detected": False,
                "face_center": None,
                "liveness": False,
            }

        # OpenCV BGR -> RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # MediaPipe image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        result = self.landmarker.detect(mp_image)

        # No face
        if not result.face_landmarks:

            return {
                "face_detected": False,
                "eye_aspect_ratio": 0.0,
                "blink_detected": False,
                "movement_detected": False,
                "face_center": None,
                "liveness": False,
            }

        landmarks = result.face_landmarks[0]

        # -----------------------------------------------------
        # Face center
        # -----------------------------------------------------

        xs = [p.x for p in landmarks]
        ys = [p.y for p in landmarks]

        center_x = sum(xs) / len(xs)
        center_y = sum(ys) / len(ys)

        face_center = (center_x, center_y)

        # -----------------------------------------------------
        # EAR / blink
        # -----------------------------------------------------

        ear = self._eye_aspect_ratio(landmarks)

        blink_detected = False

        # Closed eyes usually EAR < 0.20
        if ear < 0.20:

            if not self.was_eye_closed:
                self.blink_count += 1
                blink_detected = True

            self.was_eye_closed = True

        else:

            self.was_eye_closed = False

        # -----------------------------------------------------
        # Movement
        # -----------------------------------------------------

        movement_detected = False

        if self.previous_center is not None:

            dx = abs(center_x - self.previous_center[0])
            dy = abs(center_y - self.previous_center[1])

            movement = math.sqrt(dx * dx + dy * dy)

            if movement > self.movement_threshold:

                self.movement_count += 1
                movement_detected = True

        self.previous_center = face_center

        # -----------------------------------------------------
        # Baseline movement
        # -----------------------------------------------------

        if self.baseline_center is None:

            self.baseline_center = face_center

        else:

            dx = abs(center_x - self.baseline_center[0])
            dy = abs(center_y - self.baseline_center[1])

            baseline_movement = math.sqrt(
                dx * dx + dy * dy
            )

            if baseline_movement > self.movement_threshold:
                movement_detected = True

        # -----------------------------------------------------
        # Liveness
        # -----------------------------------------------------

        liveness = (
            self.blink_count > 0
            or
            self.movement_count > 0
        )

        return {
            "face_detected": True,
            "eye_aspect_ratio": round(ear, 4),
            "blink_detected": blink_detected,
            "movement_detected": movement_detected,
            "face_center": face_center,
            "liveness": liveness,
        }

    # ---------------------------------------------------------
    # Blink check
    # ---------------------------------------------------------

    def check_blink(self, ear):

        if ear < 0.20:

            if not self.was_eye_closed:

                self.was_eye_closed = True
                self.blink_count += 1

                return True

        else:

            self.was_eye_closed = False

        return False

    # ---------------------------------------------------------
    # Movement check
    # ---------------------------------------------------------

    def check_movement(self, x, y):

        current = (x, y)

        if self.previous_center is None:

            self.previous_center = current
            return False

        dx = abs(x - self.previous_center[0])
        dy = abs(y - self.previous_center[1])

        distance = math.sqrt(dx * dx + dy * dy)

        self.previous_center = current

        if distance > self.movement_threshold:

            self.movement_count += 1
            return True

        return False

    # ---------------------------------------------------------
    # Reset challenge
    # ---------------------------------------------------------

    def reset(self):

        self.previous_center = None
        self.baseline_center = None

        self.was_eye_closed = False

        self.blink_count = 0
        self.movement_count = 0

    # ---------------------------------------------------------
    # Close MediaPipe
    # ---------------------------------------------------------

    def close(self):

        try:
            self.landmarker.close()
        except Exception:
            pass