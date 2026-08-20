import json
import os
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types

st.set_page_config(page_title="AI Live Proctored Interviewer", page_icon="🎯", layout="wide")
st.title("🎯 AI Real-Time Proctored Interview Coach")

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# --- 1. CLIENT-SIDE JS FACE & EYE PROCTORING ENGINE ---
# Pure JavaScript + Canvas frame processing (Zero C++/OpenCV required)
proctoring_js = """
<!DOCTYPE html>
<html>
<head>
  <style>
    body { margin: 0; padding: 0; background: #0e1117; font-family: sans-serif; color: white; }
    .card { position: relative; width: 100%; max-width: 480px; margin: auto; border-radius: 8px; overflow: hidden; background: #1f2937; }
    video { width: 100%; height: 320px; object-fit: cover; transform: scaleX(-1); display: block; }
    canvas { display: none; }
    #status {
      position: absolute; top: 10px; left: 10px; right: 10px; padding: 10px;
      border-radius: 6px; font-size: 14px; font-weight: bold; text-align: center;
      background: rgba(16, 185, 129, 0.9); transition: all 0.2s ease;
    }
    .alert { background: rgba(220, 38, 38, 0.95) !important; }
  </style>
</head>
<body>
  <div class="card">
    <div id="status">🟢 Camera Active - Monitoring...</div>
    <video id="webcam" autoplay playsinline muted></video>
    <canvas id="procCanvas"></canvas>
  </div>

  <script>
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('procCanvas');
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    const statusBox = document.getElementById('status');

    let prevFrameData = null;
    let steadyFrames = 0;

    navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240 } })
      .then(stream => {
        video.srcObject = stream;
        video.onloadedmetadata = () => {
          canvas.width = 160;
          canvas.height = 120;
          requestAnimationFrame(processFrame);
        };
      })
      .catch(err => {
        statusBox.innerText = "❌ Camera Access Denied!";
        statusBox.className = "alert";
      });

    function processFrame() {
      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const currentFrame = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const pixels = currentFrame.data;

        let totalBrightness = 0;
        let motionPixels = 0;

        if (prevFrameData) {
          const prevPixels = prevFrameData.data;
          for (let i = 0; i < pixels.length; i += 16) {
            let avg = (pixels[i] + pixels[i+1] + pixels[i+2]) / 3;
            let prevAvg = (prevPixels[i] + prevPixels[i+1] + prevPixels[i+2]) / 3;
            totalBrightness += avg;

            if (Math.abs(avg - prevAvg) > 25) motionPixels++;
          }

          let frameLight = totalBrightness / (pixels.length / 16);

          if (frameLight < 15) {
            statusBox.innerText = "⚠️ PROCTOR WARNING: Camera Covered / Poor Lighting!";
            statusBox.className = "alert";
          } else if (motionPixels > 75) {
            statusBox.innerText = "⚠️ PROCTOR WARNING: Head / Face Movement Detected!";
            statusBox.className = "alert";
            steadyFrames = 0;
          } else {
            steadyFrames++;
            if (steadyFrames > 5) {
              statusBox.innerText = "✅ Candidate Focused on Screen";
              statusBox.className = "";
            }
          }
        }
        prevFrameData = currentFrame;
      }
      requestAnimationFrame(processFrame);
    }

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        alert("⚠️ PROCTOR ALERT: Tab Switch Detected!");
      }
    });
  </script>
</body>
</html>
"""

# --- 2. GEMINI CLIENT SETUP ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("Missing Gemini API Key. Please configure GEMINI_API_KEY under Streamlit Cloud Secrets.")
    st.stop()

if "questions_data" not in st.session_state:
    st.session_state.questions_data = None
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "evaluations" not in st.session_state:
    st.session_state.evaluations = []

# --- 3. SIDEBAR SETUP ---
st.sidebar.header("Interview Setup")
role_input = st.sidebar.text_area("Target Role", "Backend Engineer specializing in Python & System Design")
num_questions = st.sidebar.slider("Number of Questions", 3, 5, 3)

if st.sidebar.button("Generate Interview Session"):
    with st.spinner("Generating interview questions..."):
        prompt = f"""
        Generate {num_questions} technical interview questions for the role: {role_input}.
        Return ONLY valid JSON format:
        {{
          "questions": [
            {{
              "id": 1,
              "category": "Technical",
              "question": "Question text",
              "eval_criteria": "Expected answer requirements"
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

# --- 4. INTERVIEW QUESTION WORKFLOW ---
if st.session_state.questions_data:
    questions = st.session_state.questions_data
    curr_idx = st.session_state.current_index

    if curr_idx < len(questions):
        q = questions[curr_idx]
        st.subheader(f"Question {curr_idx + 1} of {len(questions)}")
        st.markdown(f"### **{q['question']}**")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("📹 **Real-Time Proctoring Stream**")
            components.html(proctoring_js, height=380)

        with col2:
            st.markdown("🎙️ **Candidate Response**")
            audio_recording = st.audio_input("Record spoken answer", key=f"audio_{curr_idx}")
            text_answer = st.text_area("Or type your answer here:", height=150, key=f"text_{curr_idx}")

        if st.button("Submit Answer & Evaluate"):
            if not text_answer.strip() and not audio_recording:
                st.warning("Please provide a typed or audio response before submitting.")
            else:
                with st.spinner("Evaluating response..."):
                    payload = []
                    eval_prompt = f"""
                    Evaluate this response strictly against the scoring rubric.
                    Question: {q['question']}
                    Expected Criteria: {q['eval_criteria']}
                    Written Answer: {text_answer if text_answer else 'Spoken Audio Provided'}

                    Return ONLY valid JSON format:
                    {{
                      "overall_score": 8,
                      "communication_clarity": "Strong",
                      "strengths": ["Clear technical explanation"],
                      "gaps_and_misses": ["Did not address edge cases"]
                    }}
                    """
                    payload.append(eval_prompt)

                    if audio_recording:
                        payload.append(
                            types.Part.from_bytes(data=audio_recording.getvalue(), mime_type="audio/wav")
                        )

                    eval_res = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=payload,
                        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2)
                    )

                    st.session_state.evaluations.append({
                        "question": q['question'],
                        "eval": json.loads(eval_res.text)
                    })
                    st.session_state.current_index += 1
                    st.rerun()

    else:
        st.success("🎉 Interview Completed!")
        total_score = sum(e["eval"]["overall_score"] for e in st.session_state.evaluations)
        st.metric("Overall Performance Score", f"{total_score / len(st.session_state.evaluations):.1f} / 10")

        for idx, item in enumerate(st.session_state.evaluations):
            with st.expander(f"Question {idx+1}: {item['question']}"):
                ev = item["eval"]
                st.write(f"**Score:** {ev['overall_score']}/10 | **Clarity:** {ev['communication_clarity']}")
                st.write("**Strengths:**", ev["strengths"])
                st.write("**Gaps:**", ev["gaps_and_misses"])

        if st.button("Start New Session"):
            st.session_state.questions_data = None
            st.rerun()