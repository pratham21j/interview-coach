import json
import math

import streamlit as st
import streamlit.components.v1 as components

from PIL import Image
from google import genai
from google.genai import types

from liveness.inference import (
    load_liveness_model,
    predict_liveness,
)

from liveness.challenge import LivenessChallenge


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Proctored AI Interviewer",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 Proctored AI Mock-Interview Coach")

st.caption(
    "AI-powered interview assessment with webcam liveness, "
    "voice input, spoof detection and tab-switch monitoring."
)


# ============================================================
# TAB SWITCH DETECTION
# ============================================================

tab_detector_js = """
<script>

document.addEventListener("visibilitychange", function() {

    if (document.hidden) {

        alert(
            "WARNING: Tab switch detected! "
            + "Please return to the interview screen."
        );

        window.parent.postMessage(
            {
                type: "tab_switched",
                status: "hidden"
            },
            "*"
        );
    }

});

</script>
"""

components.html(
    tab_detector_js,
    height=0,
)


# ============================================================
# GEMINI CLIENT
# ============================================================

try:

    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )

except Exception as error:

    st.error(
        "Gemini API key not found.\n\n"
        "Create:\n"
        ".streamlit/secrets.toml\n\n"
        "with:\n\n"
        'GEMINI_API_KEY = "YOUR_KEY"'
    )

    st.stop()


# ============================================================
# LIVENESS CNN MODEL
# ============================================================

@st.cache_resource
def get_liveness_model():

    return load_liveness_model()


try:

    liveness_model = get_liveness_model()

except Exception as error:

    st.error(
        f"Unable to load liveness model: {error}"
    )

    st.stop()


# ============================================================
# MEDIAPIPE LIVENESS CHALLENGE
# ============================================================

@st.cache_resource
def get_liveness_challenge():

    return LivenessChallenge()


try:

    challenge_detector = get_liveness_challenge()

except Exception as error:

    st.error(
        f"Unable to initialize MediaPipe liveness detector: {error}"
    )

    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "questions_data" not in st.session_state:
    st.session_state.questions_data = None

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "evaluations" not in st.session_state:
    st.session_state.evaluations = []

if "liveness_results" not in st.session_state:
    st.session_state.liveness_results = {}

if "baseline_data" not in st.session_state:
    st.session_state.baseline_data = {}

if "movement_data" not in st.session_state:
    st.session_state.movement_data = {}

if "blink_data" not in st.session_state:
    st.session_state.blink_data = {}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def process_liveness_image(image):

    """
    Process one webcam image using MediaPipe.

    Returns:

        {
            "face_detected": bool,
            "x": float,
            "y": float,
            "ear": float,
            "movement_detected": bool,
            "blink_detected": bool
        }
    """

    try:

        rgb_image = image.convert("RGB")

        # PIL -> numpy
        import numpy as np
        import cv2

        frame = np.array(rgb_image)

        # RGB -> BGR for existing challenge
        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_RGB2BGR
        )

        result = challenge_detector.process_frame(
            frame
        )

        if not result.get("face_detected", False):

            return {
                "face_detected": False,
                "x": 0.5,
                "y": 0.5,
                "ear": 0.0,
                "movement_detected": False,
                "blink_detected": False,
            }

        x, y = result["face_center"]

        return {
            "face_detected": True,
            "x": float(x),
            "y": float(y),
            "ear": float(
                result["eye_aspect_ratio"]
            ),
            "movement_detected": bool(
                result.get(
                    "movement_detected",
                    False
                )
            ),
            "blink_detected": bool(
                result.get(
                    "blink_detected",
                    False
                )
            ),
        }

    except Exception as error:

        st.error(
            f"Camera/liveness processing error: {error}"
        )

        return {
            "face_detected": False,
            "x": 0.5,
            "y": 0.5,
            "ear": 0.0,
            "movement_detected": False,
            "blink_detected": False,
        }


def calculate_face_movement(first, second):

    dx = second["x"] - first["x"]
    dy = second["y"] - first["y"]

    distance = math.sqrt(
        dx * dx + dy * dy
    )

    return distance


def calculate_blink_change(first, second):

    return abs(
        first["ear"] - second["ear"]
    )


def run_cnn(image):

    """
    Run the trained CNN.

    IMPORTANT:
    CNN result is advisory.
    Behavioral liveness is used as the primary
    verification signal.
    """

    try:

        result = predict_liveness(
            liveness_model,
            image,
        )

        return result

    except Exception as error:

        return {
            "label": "UNKNOWN",
            "confidence": 0.0,
            "live_probability": 0.0,
            "spoof_probability": 0.0,
            "error": str(error),
        }


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "⚙️ Interview Setup"
)

role_input = st.sidebar.text_area(
    "Target Role / Job Description",
    "Backend Engineer specializing in Python & System Design",
)

num_questions = st.sidebar.slider(
    "Number of Questions",
    3,
    5,
    3,
)


# ============================================================
# GENERATE INTERVIEW
# ============================================================

if st.sidebar.button(
    "🚀 Generate Interview Session"
):

    with st.spinner(
        "Generating targeted interview questions..."
    ):

        prompt = f"""
Generate {num_questions} interview questions
for the following role:

{role_input}

Create a balanced interview containing
technical and behavioral questions.

Questions should test:

1. Core technical knowledge
2. Problem solving
3. System design where appropriate
4. Practical experience
5. Behavioral skills

Return ONLY valid JSON matching this schema:

{{
    "questions": [
        {{
            "id": 1,
            "category": "Technical",
            "question": "Question text here",
            "eval_criteria": "What a strong candidate response should contain"
        }}
    ]
}}
"""

        try:

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )

            data = json.loads(
                response.text
            )

            st.session_state.questions_data = (
                data["questions"]
            )

            st.session_state.current_index = 0

            st.session_state.evaluations = []

            st.session_state.liveness_results = {}

            st.session_state.baseline_data = {}

            st.session_state.movement_data = {}

            st.session_state.blink_data = {}

            st.rerun()

        except Exception as error:

            st.error(
                f"Unable to generate interview: {error}"
            )


# ============================================================
# INTERVIEW
# ============================================================

if st.session_state.questions_data:

    questions = (
        st.session_state.questions_data
    )

    curr_idx = (
        st.session_state.current_index
    )


    # ========================================================
    # CURRENT QUESTION
    # ========================================================

    if curr_idx < len(questions):

        q = questions[curr_idx]


        # ====================================================
        # PROGRESS
        # ====================================================

        progress = (
            curr_idx / len(questions)
        )

        st.progress(progress)

        st.subheader(
            f"Question {curr_idx + 1} "
            f"of {len(questions)} "
            f"[{q['category']}]"
        )

        st.markdown(
            f"### {q['question']}"
        )

        st.divider()


        # ====================================================
        # LIVENESS SECTION
        # ====================================================

        st.subheader(
            "🛡️ Live Person Verification"
        )

        st.info(
            "Complete the three webcam checks below. "
            "This is more reliable than judging liveness "
            "from a single photograph."
        )


        # ====================================================
        # STEP 1 - BASELINE
        # ====================================================

        st.markdown(
            "#### Step 1 — Look straight at the camera"
        )

        baseline_image = st.camera_input(
            "Take baseline photo",
            key=f"baseline_{curr_idx}",
        )

        baseline_result = None

        if baseline_image:

            baseline_pil = Image.open(
                baseline_image
            ).convert("RGB")

            baseline_result = process_liveness_image(
                baseline_pil
            )

            if baseline_result["face_detected"]:

                st.success(
                    "🟢 Face detected"
                )

                st.write(
                    f"Eye openness (EAR): "
                    f"{baseline_result['ear']:.3f}"
                )

                st.session_state.baseline_data[
                    curr_idx
                ] = baseline_result

            else:

                st.error(
                    "🔴 No face detected. "
                    "Please take another photo."
                )


        # ====================================================
        # STEP 2 - HEAD MOVEMENT
        # ====================================================

        st.markdown(
            "#### Step 2 — Move your head slightly LEFT or RIGHT"
        )

        movement_image = st.camera_input(
            "Take movement verification photo",
            key=f"movement_{curr_idx}",
        )

        movement_result = None

        if movement_image:

            movement_pil = Image.open(
                movement_image
            ).convert("RGB")

            movement_result = process_liveness_image(
                movement_pil
            )

            baseline = (
                st.session_state.baseline_data.get(
                    curr_idx
                )
            )

            if movement_result["face_detected"]:

                if baseline:

                    movement_distance = (
                        calculate_face_movement(
                            baseline,
                            movement_result
                        )
                    )

                    st.write(
                        f"Detected face movement: "
                        f"{movement_distance:.4f}"
                    )

                    # Threshold
                    if movement_distance > 0.015:

                        st.success(
                            "🟢 HEAD MOVEMENT DETECTED"
                        )

                        st.session_state.movement_data[
                            curr_idx
                        ] = {
                            "detected": True,
                            "distance": movement_distance,
                        }

                    else:

                        st.warning(
                            "🟡 Very little movement detected. "
                            "Move your head a little more."
                        )

                else:

                    st.warning(
                        "Please complete Step 1 first."
                    )

            else:

                st.error(
                    "🔴 No face detected."
                )


        # ====================================================
        # STEP 3 - BLINK
        # ====================================================

        st.markdown(
            "#### Step 3 — Blink once"
        )

        blink_image = st.camera_input(
            "Take blink verification photo",
            key=f"blink_{curr_idx}",
        )

        blink_result = None

        if blink_image:

            blink_pil = Image.open(
                blink_image
            ).convert("RGB")

            blink_result = process_liveness_image(
                blink_pil
            )

            baseline = (
                st.session_state.baseline_data.get(
                    curr_idx
                )
            )

            if blink_result["face_detected"]:

                if baseline:

                    ear_change = (
                        calculate_blink_change(
                            baseline,
                            blink_result
                        )
                    )

                    st.write(
                        f"Eye change: "
                        f"{ear_change:.3f}"
                    )

                    # Blink threshold
                    if (
                        blink_result["blink_detected"]
                        or ear_change > 0.06
                    ):

                        st.success(
                            "🟢 BLINK DETECTED"
                        )

                        st.session_state.blink_data[
                            curr_idx
                        ] = {
                            "detected": True,
                            "ear_change": ear_change,
                        }

                    else:

                        st.warning(
                            "🟡 Blink not detected. "
                            "Close your eyes and capture again."
                        )

                else:

                    st.warning(
                        "Please complete Step 1 first."
                    )

            else:

                st.error(
                    "🔴 No face detected."
                )


        # ====================================================
        # CNN ANALYSIS
        # ====================================================

        cnn_result = None

        if baseline_image:

            cnn_result = run_cnn(
                baseline_pil
            )

            st.markdown(
                "#### 🤖 AI Presentation-Attack Model"
            )

            if "error" not in cnn_result:

                cnn_label = cnn_result.get(
                    "label",
                    "UNKNOWN"
                )

                cnn_confidence = (
                    cnn_result.get(
                        "confidence",
                        0.0
                    )
                    * 100
                )

                live_probability = (
                    cnn_result.get(
                        "live_probability",
                        0.0
                    )
                    * 100
                )

                spoof_probability = (
                    cnn_result.get(
                        "spoof_probability",
                        0.0
                    )
                    * 100
                )


                # ------------------------------------------------
                # IMPORTANT
                # ------------------------------------------------

                if cnn_label == "LIVE":

                    st.success(
                        f"🟢 CNN: LIVE "
                        f"({cnn_confidence:.1f}%)"
                    )

                elif cnn_label == "SPOOF":

                    st.warning(
                        f"🟡 CNN: SPOOF "
                        f"({cnn_confidence:.1f}%)"
                    )

                    st.caption(
                        "CNN result is advisory because "
                        "single-image liveness can produce "
                        "false positives. Behavioral checks "
                        "below are used for final verification."
                    )

                else:

                    st.warning(
                        "🟡 CNN result unavailable."
                    )


                with st.expander(
                    "🔍 CNN Liveness Details"
                ):

                    st.write(
                        f"Live probability: "
                        f"{live_probability:.2f}%"
                    )

                    st.write(
                        f"Spoof probability: "
                        f"{spoof_probability:.2f}%"
                    )


        # ====================================================
        # FINAL BEHAVIORAL LIVENESS DECISION
        # ====================================================

        movement_passed = (
            curr_idx in st.session_state.movement_data
            and
            st.session_state.movement_data[
                curr_idx
            ]["detected"]
        )

        blink_passed = (
            curr_idx in st.session_state.blink_data
            and
            st.session_state.blink_data[
                curr_idx
            ]["detected"]
        )

        baseline_passed = (
            curr_idx in st.session_state.baseline_data
            and
            st.session_state.baseline_data[
                curr_idx
            ]["face_detected"]
        )


        behavioral_live = (
            baseline_passed
            and
            (
                movement_passed
                or blink_passed
            )
        )


        st.divider()

        st.markdown(
            "### 🛡️ Liveness Status"
        )


        if behavioral_live:

            st.success(
                "🟢 LIVE PERSON VERIFIED"
            )

            st.write(
                "The candidate's face was detected "
                "and a real-time behavioral change "
                "was observed."
            )

        elif baseline_passed:

            st.warning(
                "🟡 LIVENESS NOT VERIFIED YET"
            )

            st.write(
                "Complete at least one behavioral "
                "challenge: head movement or blink."
            )

        else:

            st.error(
                "🔴 FACE NOT VERIFIED"
            )


        # ====================================================
        # ANSWER SECTION
        # ====================================================

        st.divider()

        col1, col2 = st.columns(2)


        # ====================================================
        # VOICE
        # ====================================================

        with col1:

            st.markdown(
                "### 🎙️ Your Answer"
            )

            audio_recording = st.audio_input(
                "Record your answer",
                key=f"audio_{curr_idx}",
            )


        # ====================================================
        # TEXT
        # ====================================================

        with col2:

            st.markdown(
                "### 📝 Text Answer"
            )

            text_answer = st.text_area(
                "Or type your response:",
                height=150,
                key=f"text_{curr_idx}",
            )


        # ====================================================
        # SUBMIT
        # ====================================================

        st.divider()

        if st.button(
            "✅ Submit Answer & Evaluate",
            key=f"submit_{curr_idx}",
            type="primary",
        ):


            # =================================================
            # ANSWER VALIDATION
            # =================================================

            if (
                not text_answer.strip()
                and not audio_recording
            ):

                st.warning(
                    "Please provide either a "
                    "voice recording or typed answer."
                )

                st.stop()


            # =================================================
            # LIVENESS VALIDATION
            # =================================================

            if not behavioral_live:

                st.error(
                    "🔴 Liveness verification failed."
                )

                st.warning(
                    "Please complete the webcam checks. "
                    "You must show a face and perform "
                    "either a head movement or blink."
                )

                st.stop()


            # =================================================
            # GEMINI EVALUATION
            # =================================================

            with st.spinner(
                "🤖 AI is evaluating your answer..."
            ):

                contents_payload = []


                eval_prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer strictly against
the question and evaluation criteria.

Question:
{q['question']}

Expected Criteria:
{q['eval_criteria']}

Written Response:
{
    text_answer
    if text_answer.strip()
    else
    "Candidate responded using audio."
}

The candidate has passed behavioral liveness
verification.

Evaluate:

1. Technical correctness
2. Depth of understanding
3. Problem solving
4. Communication clarity
5. Relevance
6. Missing concepts

Return ONLY valid JSON:

{{
    "overall_score": 8,
    "communication_clarity": "Strong",
    "technical_depth": "Strong",
    "strengths": [
        "Strength 1",
        "Strength 2"
    ],
    "gaps_and_misses": [
        "Gap 1"
    ],
    "ideal_response_highlights":
        "Summary of what an excellent answer should contain"
}}

overall_score must be an integer from 0 to 10.
"""

                contents_payload.append(
                    eval_prompt
                )


                # =============================================
                # AUDIO
                # =============================================

                if audio_recording:

                    audio_bytes = (
                        audio_recording.getvalue()
                    )

                    contents_payload.append(
                        types.Part.from_bytes(
                            data=audio_bytes,
                            mime_type="audio/wav",
                        )
                    )


                # =============================================
                # CAMERA IMAGE
                # =============================================

                if baseline_image:

                    image_bytes = (
                        baseline_image.getvalue()
                    )

                    contents_payload.append(
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type="image/jpeg",
                        )
                    )


                # =============================================
                # GEMINI
                # =============================================

                try:

                    eval_res = (
                        client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=contents_payload,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                temperature=0.2,
                            ),
                        )
                    )


                    evaluation = json.loads(
                        eval_res.text
                    )


                    # =========================================
                    # STORE RESULT
                    # =========================================

                    liveness_record = {

                        "label": "LIVE",

                        "confidence": 1.0,

                        "behavioral_verification": True,

                        "movement_detected":
                            movement_passed,

                        "blink_detected":
                            blink_passed,

                    }


                    if cnn_result:

                        liveness_record[
                            "cnn_label"
                        ] = cnn_result.get(
                            "label",
                            "UNKNOWN"
                        )

                        liveness_record[
                            "cnn_confidence"
                        ] = cnn_result.get(
                            "confidence",
                            0.0
                        )


                    st.session_state.evaluations.append(
                        {
                            "question":
                                q["question"],

                            "eval":
                                evaluation,

                            "liveness":
                                liveness_record,
                        }
                    )


                    st.session_state.current_index += 1

                    st.rerun()


                except Exception as error:

                    st.error(
                        f"AI evaluation failed: {error}"
                    )


    # ========================================================
    # INTERVIEW COMPLETE
    # ========================================================

    else:

        st.success(
            "🎉 Interview Complete!"
        )


        evaluations = (
            st.session_state.evaluations
        )


        if evaluations:

            # =================================================
            # SCORE
            # =================================================

            total_score = sum(
                item["eval"]["overall_score"]
                for item in evaluations
            )

            average_score = (
                total_score
                / len(evaluations)
            )


            # =================================================
            # METRICS
            # =================================================

            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "🏆 Overall Score",
                    f"{average_score:.1f} / 10",
                )


            with col2:

                st.metric(
                    "📋 Questions",
                    len(evaluations),
                )


            with col3:

                live_count = sum(
                    1
                    for item in evaluations
                    if item["liveness"][
                        "behavioral_verification"
                    ]
                )

                st.metric(
                    "🛡️ Liveness Checks",
                    f"{live_count}/{len(evaluations)}",
                )


            st.divider()


            # =================================================
            # RESULTS
            # =================================================

            st.subheader(
                "📊 Question-by-Question Results"
            )


            for idx, item in enumerate(
                evaluations
            ):

                ev = item["eval"]

                liveness = item[
                    "liveness"
                ]


                with st.expander(
                    f"Question {idx + 1}: "
                    f"{item['question']}"
                ):

                    st.write(
                        f"**Score:** "
                        f"{ev['overall_score']}/10"
                    )

                    st.write(
                        f"**Communication:** "
                        f"{ev['communication_clarity']}"
                    )

                    st.write(
                        f"**Technical Depth:** "
                        f"{ev.get('technical_depth', 'N/A')}"
                    )


                    st.write(
                        "**Liveness:** 🟢 LIVE"
                    )


                    if liveness.get(
                        "movement_detected"
                    ):

                        st.write(
                            "✓ Head movement detected"
                        )


                    if liveness.get(
                        "blink_detected"
                    ):

                        st.write(
                            "✓ Blink detected"
                        )


                    if "cnn_label" in liveness:

                        st.write(
                            f"**CNN result:** "
                            f"{liveness['cnn_label']} "
                            f"({liveness['cnn_confidence'] * 100:.1f}%)"
                        )


                    st.markdown(
                        "### 💪 Strengths"
                    )

                    for strength in ev[
                        "strengths"
                    ]:

                        st.write(
                            f"• {strength}"
                        )


                    st.markdown(
                        "### ⚠️ Gaps / Misses"
                    )

                    for gap in ev[
                        "gaps_and_misses"
                    ]:

                        st.write(
                            f"• {gap}"
                        )


                    st.markdown(
                        "### 💡 Ideal Response"
                    )

                    st.write(
                        ev[
                            "ideal_response_highlights"
                        ]
                    )


            st.divider()


            # =================================================
            # NEW INTERVIEW
            # =================================================

            if st.button(
                "🔄 Start New Interview"
            ):

                st.session_state.questions_data = None

                st.session_state.current_index = 0

                st.session_state.evaluations = []

                st.session_state.liveness_results = {}

                st.session_state.baseline_data = {}

                st.session_state.movement_data = {}

                st.session_state.blink_data = {}

                st.rerun()


# ============================================================
# INITIAL SCREEN
# ============================================================

else:

    st.info(
        "👈 Configure the target role and click "
        "**Generate Interview Session** to begin."
    )


    st.markdown(
        """
### 🛡️ Proctoring Features

- 📷 Webcam verification
- 👤 Face detection
- ↔️ Head movement challenge
- 👁️ Blink challenge
- 🤖 CNN presentation-attack analysis
- 🎙️ Voice answers
- 📝 Text answers
- 👁️ Browser tab-switch warning
- 📊 AI interview scoring
- 💡 Personalized feedback
"""
    )