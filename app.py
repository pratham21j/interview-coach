import json
import cv2
import numpy as np
import time
import streamlit as st
import streamlit.components.v1 as components
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from camera_input_live import camera_input_live
from google import genai
from google.genai import types
import os
import urllib.request

MODEL_PATH = 'face_landmarker.task'
MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task'

# Automatically fetch the missing task model if not present locally
if not os.path.exists(MODEL_PATH):
    st.info("Downloading MediaPipe face landmarker model... Please wait a moment.")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    st.rerun()
st.set_page_config(page_title="AI Live Proctored Interviewer", page_icon="🎯", layout="wide")
st.title("🎯 AI Live-Proctored Interview Coach")

# --- 1. TAB-SWITCH DETECTION ---
tab_detector_js = """
<script>
document.addEventListener("visibilitychange", function() {
    if (document.hidden) {
        window.parent.postMessage({type: 'tab_switched', status: 'hidden'}, '*');
        alert("⚠️ WARNING: Tab switch detected!");
    }
});
</script>
"""
components.html(tab_detector_js, height=0)

# --- 2. EAR & EYE TRACKING LOGIC ---
EAR_THRESHOLD = 0.23
closed_frames = 0
blink_timestamps = []

def calculate_ear(eye_landmarks):
    """Calculates the Eye Aspect Ratio (EAR) using 6 landmark points."""
    p1, p2, p3, p4, p5, p6 = eye_landmarks
    v1 = np.linalg.norm(np.array(p2) - np.array(p6))
    v2 = np.linalg.norm(np.array(p3) - np.array(p5))
    h = np.linalg.norm(np.array(p1) - np.array(p4))
    if h == 0:
        return 0.0
    return (v1 + v2) / (2.0 * h)

def process_eye_ear(ear):
    """Tracks blinks and closed-eye duration based on calculated EAR."""
    global closed_frames, blink_timestamps
    eyes_closed = 0
    if ear < EAR_THRESHOLD:
        closed_frames += 1
    else:
        if closed_frames >= 2:
            blink_timestamps.append(time.time())
        closed_frames = 0
    
    eyes_closed = closed_frames / 30.0  # Assumes ~30 FPS
    current_time = time.time()
    blink_timestamps = [t for t in blink_timestamps if current_time - t <= 60]
    blink_rate = len(blink_timestamps)
    return eyes_closed, blink_rate

# --- 3. MEDIAPIPE FACE LANDMARKER SETUP ---
@st.cache_resource
def load_landmarker():
    base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
        num_faces=2
    )
    return vision.FaceLandmarker.create_from_options(options)

try:
    landmarker = load_landmarker()
except Exception as e:
    st.error("Missing 'face_landmarker.task' file. Download it from MediaPipe and place it in the project root directory.")
    st.stop()

# --- 4. REAL-TIME PROCTORING ENGINE ---
def process_live_proctoring(image_bytes):
    np_img = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    if frame is None:
        return "No Frame Received", None

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = landmarker.detect(mp_image)

    faces = detection_result.face_landmarks
    status = "✅ Candidate Focused on Screen"
    box_color = (0, 255, 0)

    if len(faces) == 0:
        status = "⚠️ CHEATING WARNING: No Face Detected!"
        box_color = (0, 0, 255)
    elif len(faces) > 1:
        status = "⚠️ CHEATING WARNING: Multiple Faces Detected!"
        box_color = (0, 0, 255)
    else:
        landmarks = faces[0]
        h, w, _ = frame.shape
        
        # Exact MediaPipe landmark indices for left and right eyes
        LEFT_EYE_IDX = [362, 385, 387, 263, 373, 380]
        RIGHT_EYE_IDX = [33, 160, 158, 133, 153, 144]

        left_eye_pts = [[landmarks[i].x * w, landmarks[i].y * h] for i in LEFT_EYE_IDX]
        right_eye_pts = [[landmarks[i].x * w, landmarks[i].y * h] for i in RIGHT_EYE_IDX]

        left_ear = calculate_ear(left_eye_pts)
        right_ear = calculate_ear(right_eye_pts)
        avg_ear = (left_ear + right_ear) / 2.0

        eyes_closed, blink_rate = process_eye_ear(avg_ear)

        # Draw Eye Polygons on Feed
        pts_l = np.array(left_eye_pts, dtype=np.int32)
        pts_r = np.array(right_eye_pts, dtype=np.int32)
        cv2.polylines(frame, [pts_l], True, (255, 255, 0), 1)
        cv2.polylines(frame, [pts_r], True, (255, 255, 0), 1)

        # Head Pose Check via Nose Index 1
        nose_x = landmarks[1].x * w
        frame_center_x = w / 2

        if nose_x - frame_center_x > 90:
            status = "⚠️ CHEATING WARNING: Turned Head Right!"
            box_color = (0, 0, 255)
        elif nose_x - frame_center_x < -90:
            status = "⚠️ CHEATING WARNING: Turned Head Left!"
            box_color = (0, 0, 255)
        elif eyes_closed > 2.0:
            status = "⚠️ CHEATING WARNING: Eyes Closed / Looking Away!"
            box_color = (0, 0, 255)

        cv2.putText(frame, f"EAR: {avg_ear:.2f}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Blinks/Min: {blink_rate}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    annotated_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return status, annotated_frame

# --- 5. GEMINI API SETUP ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("Gemini API key not found in .streamlit/secrets.toml")
    st.stop()

if "questions_data" not in st.session_state:
    st.session_state.questions_data = None
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "evaluations" not in st.session_state:
    st.session_state.evaluations = []

# --- 6. SIDEBAR ---
st.sidebar.header("Interview Setup")
role_input = st.sidebar.text_area("Target Role", "Backend Engineer specializing in Python & System Design")
num_questions = st.sidebar.slider("Number of Questions", 3, 5, 3)

if st.sidebar.button("Generate Interview Session"):
    with st.spinner("Generating questions..."):
        prompt = f"""
        Generate {num_questions} technical questions for the role: {role_input}.
        Return ONLY valid JSON:
        {{
          "questions": [
            {{
              "id": 1,
              "category": "Technical",
              "question": "Question text",
              "eval_criteria": "Expected criteria"
            }}
          ]
        }}
        """
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2)
        )
        st.session_state.questions_data = json.loads(response.text)["questions"]
        st.session_state.current_index = 0
        st.session_state.evaluations = []
        st.rerun()

# --- 7. INTERVIEW SESSION ---
if st.session_state.questions_data:
    questions = st.session_state.questions_data
    curr_idx = st.session_state.current_index

    if curr_idx < len(questions):
        q = questions[curr_idx]
        st.subheader(f"Question {curr_idx + 1} of {len(questions)}")
        st.markdown(f"### **{q['question']}**")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("📹 **Real-Time Feed**")
            live_image = camera_input_live()
            proctor_status = "Scanning Camera..."
            if live_image:
                proctor_status, annotated_img = process_live_proctoring(live_image.getvalue())
                if annotated_img is not None:
                    st.image(annotated_img, channels="RGB", use_container_width=True)
                if "✅" in proctor_status:
                    st.success(proctor_status)
                else:
                    st.error(proctor_status)

        with col2:
            st.markdown("🎙️ **Response Options**")
            audio_recording = st.audio_input("Record spoken answer", key=f"audio_{curr_idx}")
            text_answer = st.text_area("Or type your answer here:", height=120, key=f"text_{curr_idx}")

        if st.button("Submit Answer"):
            if not text_answer.strip() and not audio_recording:
                st.warning("Please provide an answer.")
            else:
                with st.spinner("Evaluating..."):
                    eval_prompt = f"""
                    Evaluate this response:
                    Question: {q['question']}
                    Written Response: {text_answer if text_answer else 'Spoken Audio Provided'}
                    Proctor Status: {proctor_status}

                    Return ONLY valid JSON:
                    {{
                      "overall_score": 8,
                      "communication_clarity": "Strong",
                      "strengths": ["Good point"],
                      "gaps_and_misses": ["Missed detail"]
                    }}
                    """
                    eval_res = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=eval_prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2)
                    )
                    st.session_state.evaluations.append({
                        "question": q['question'],
                        "proctor_flag": proctor_status,
                        "eval": json.loads(eval_res.text)
                    })
                    st.session_state.current_index += 1
                    st.rerun()