# 📸 AI Interview Coach - Visual Guide & Screenshots

## Overview

This document provides visual walkthroughs of the AI Live-Proctored Interview Coach application with annotated screenshots showing key features and user interactions.

---

## 🖥️ Interface Layout

### Main Components

```
┌─────────────────────────────────────────────────────────────────┐
│  STREAMLIT HEADER                                               │
│  [Deploy] [Menu]                                                │
├────────────────────┬─────────────────────────────────────────┤
│                    │                                          │
│   SIDEBAR          │         MAIN CONTENT AREA               │
│   (Left Panel)     │                                          │
│                    │                                          │
│ ┌────────────────┐ │  ┌──────────────────────────────────┐   │
│ │ Interview      │ │  │ Question Display                 │   │
│ │ Setup          │ │  │ + Real-Time Feed (Video)         │   │
│ │                │ │  │ + Response Options               │   │
│ │ • Target Role  │ │  │ + Submit Button                  │   │
│ │ • # Questions  │ │  │                                  │   │
│ │ • Generate Btn │ │  └──────────────────────────────────┘   │
│ └────────────────┘ │                                          │
│                    │                                          │
└────────────────────┴─────────────────────────────────────────┘
```

---

## 📋 Screen 1: Initial Setup

**Purpose:** Configure interview session parameters

**Key Elements:**

```
┌─────────────────────────────────────────┐
│ 🎯 AI Live-Proctored Interview Coach    │  ← Title
└─────────────────────────────────────────┘

SIDEBAR:
┌──────────────────────────────────────────┐
│ Interview Setup                          │
├──────────────────────────────────────────┤
│ Target Role *                            │
│ ┌──────────────────────────────────────┐ │
│ │ Backend Engineer specializing in     │ │
│ │ Python & System Design               │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ Number of Questions                      │
│ [●───────────────────────────────────]   │
│          3              5                 │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ Generate Interview Session           │ │
│ └──────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

**User Actions:**

1. Enter target job role/position
2. Adjust number of questions using slider (3-5)
3. Click "Generate Interview Session" button
4. App calls Gemini API to generate questions
5. Questions appear in main area

**API Flow:**

```
User Input → Streamlit → Gemini API → JSON Response → Display
  (Role)       (Setup)    (Generate)   (Questions)    (UI)
```

---

## 🎤 Screen 2: Interview Session

**Purpose:** Present question and collect candidate response

**Key Sections:**

### Left Column: Real-Time Feed

```
┌─────────────────────────────────────────┐
│ 📹 Real-Time Feed                       │
├─────────────────────────────────────────┤
│                                         │
│  [Video Stream from Webcam]             │
│  - Face Detection Active                │
│  - Eye Landmarks Visible                │
│  - EAR Metrics Displayed                │
│  - Proctoring Status Shown              │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ Pause capturing                  │  │
│  └──────────────────────────────────┘  │
│                                         │
│  Status Bar (Green/Red):                │
│  ✅ Candidate Focused on Screen         │
│  OR                                     │
│  ⚠️ CHEATING WARNING: Eyes Closed       │
│                                         │
└─────────────────────────────────────────┘
```

### Center: Question Display

```
┌──────────────────────────────────────────┐
│ Question 1 of 3                          │
├──────────────────────────────────────────┤
│                                          │
│ Explain how Python's Global Interpreter │
│ Lock (GIL) impacts multithreaded         │
│ CPU-bound versus I/O-bound applications, │
│ and discuss strategies to bypass or      │
│ mitigate its limitations.                │
│                                          │
└──────────────────────────────────────────┘
```

### Right Column: Response Options

```
┌──────────────────────────────────────────┐
│ 🎙️ Response Options                     │
├──────────────────────────────────────────┤
│                                          │
│ Record spoken answer                    │
│ ┌────────────────────────────────────┐  │
│ │ 🎤 Record    | 00:00               │  │
│ └────────────────────────────────────┘  │
│                                          │
│ Or type your answer here:                │
│ ┌────────────────────────────────────┐  │
│ │                                    │  │
│ │ [Text area for written response]  │  │
│ │                                    │  │
│ │                                    │  │
│ └────────────────────────────────────┘  │
│                                          │
│ ┌────────────────────────────────────┐  │
│ │     Submit Answer                  │  │
│ └────────────────────────────────────┘  │
│                                          │
└──────────────────────────────────────────┘
```

---

## 🎯 Feature Highlights: Real-Time Proctoring

### Face Detection System

**Status Indicators:**

```
Status                          Color    Action
─────────────────────────────────────────────────────
✅ Candidate Focused            GREEN    ✓ Pass - Continue
⚠️ No Face Detected             RED      ✗ Fail - Stop Session
⚠️ Multiple Faces Detected      RED      ✗ Fail - Cheating Alert
⚠️ Head Turned Right (>90px)    RED      ✗ Fail - Looking Away
⚠️ Head Turned Left (>90px)     RED      ✗ Fail - Looking Away
⚠️ Eyes Closed (EAR <0.23)      RED      ✗ Fail - Cheating Flag
```

### Metrics Displayed on Video Feed

```
┌───────────────────────────────────┐
│  Video Frame                      │
├───────────────────────────────────┤
│                                   │
│  EAR: 0.28            ← Distance  │
│  Blinks/Min: 16       ← Frequency │
│                                   │
│  [Face with landmarks]            │
│  - 468 facial points detected     │
│  - Eye regions highlighted        │
│  - Head pose estimated            │
│                                   │
│  Status: ✅ Candidate Focused     │
│                                   │
└───────────────────────────────────┘

EAR (Eye Aspect Ratio):
> 0.23: Eyes Open  ✓
≤ 0.23: Eyes Closed ✗
```

### Detection Algorithm

```
Frame Input
    ↓
[MediaPipe Face Landmarker]
    ↓
Extract 468 Landmarks
    ↓
    ├→ Face Detection (yes/no/multiple)
    ├→ Nose Position (head pose)
    ├→ Eye Landmarks (EAR calculation)
    └→ Blink Detection
    ↓
Generate Status Report
    ↓
Update UI + Log Proctoring Flag
```

---

## 📊 Question Flow & Progression

### Session Progression

```
┌──────────────┐
│  Question 1  │
│  of 3        │
├──────────────┤
│              │
│ Candidate    │
│ Answers      │
│              │
└──────┬───────┘
       │ [Submit]
       ↓
  [Evaluate]
  [Gemini API]
       │
       ↓
┌──────────────┐
│  Question 2  │
│  of 3        │
├──────────────┤
│              │
│ Candidate    │
│ Answers      │
│              │
└──────┬───────┘
       │ [Submit]
       ↓
  [Evaluate]
  [Gemini API]
       │
       ↓
┌──────────────┐
│  Question 3  │
│  of 3        │
├──────────────┤
│              │
│ Candidate    │
│ Answers      │
│              │
└──────┬───────┘
       │ [Submit]
       ↓
  [Evaluate]
  [Gemini API]
       │
       ↓
  [Show Results]
  [Session Complete]
```

---

## 🔍 Proctoring Event Examples

### Normal Session (Pass)

```
Frame 1:  ✅ Face Detected
Frame 2:  ✅ Single Face
Frame 3:  ✅ Head Centered (Nose at 200px)
Frame 4:  ✅ Eyes Open (EAR: 0.27)
Frame 5:  ✅ Candidate Focused

Status: PASS - No flags ✓
```

### Suspected Cheating (Fail)

```
Frame 1:  ✅ Face Detected
Frame 2:  ✅ Single Face
Frame 3:  ⚠️ Head Turned Right (Nose at 350px)
Frame 4:  ⚠️ Eyes Closed (EAR: 0.18)
Frame 5:  ❌ Tab Switch Detected!

Status: FAIL - Multiple Flags 🚨
Logged: "Eyes Closed / Looking Away"
        "Tab Switch Detected"
```

---

## 📈 Evaluation & Results

### Gemini API Evaluation Prompt

```python
eval_prompt = """
Evaluate this response:
Question: Explain how Python's GIL impacts multithreaded...
Written Response: [candidate's text answer]
Proctor Status: ✅ Candidate Focused on Screen

Return JSON with:
- overall_score (1-10)
- communication_clarity (assessment)
- strengths (list)
- gaps_and_misses (list)
"""
```

### Response Evaluation JSON

```json
{
  "overall_score": 7,
  "communication_clarity": "Good",
  "strengths": [
    "Clear explanation of GIL fundamentals",
    "Mentioned multiprocessing as alternative",
    "Understood CPU-bound vs I/O-bound distinction"
  ],
  "gaps_and_misses": [
    "Didn't mention async/await",
    "Limited discussion of C extensions",
    "Missing concrete benchmarks"
  ]
}
```

### Session Results Summary

```
╔═══════════════════════════════════════════════════════╗
║          INTERVIEW SESSION COMPLETE                  ║
╚═══════════════════════════════════════════════════════╝

Question 1/3: Python GIL
├─ Score: 7/10
├─ Status: ✅ Candidate Focused
├─ Strengths: [2 identified]
└─ Gaps: [3 identified]

Question 2/3: System Design
├─ Score: 8/10
├─ Status: ✅ Candidate Focused
├─ Strengths: [3 identified]
└─ Gaps: [2 identified]

Question 3/3: API Design Patterns
├─ Score: 6/10
├─ Status: ⚠️ Eyes Closed (2 seconds)
├─ Strengths: [2 identified]
└─ Gaps: [4 identified]

═════════════════════════════════════════════════════════

OVERALL STATISTICS:
├─ Average Score: 7.0/10
├─ Communication: Good
├─ Proctoring Flags: 1 (Eyes Closed)
└─ Duration: 12 minutes

SESSION STATUS: ✅ COMPLETED WITH MINOR FLAG
```

---

## 🖼️ Real Application Screenshots

### Screenshot 1: Initial Setup Screen

**File:** `screenshots/01-setup-screen.png`

Shows:

- Sidebar with Interview Setup
- Target Role input field
- Number of Questions slider (3-5)
- "Generate Interview Session" button
- Clean dark theme UI

---

### Screenshot 2: Interview in Progress

**File:** `screenshots/02-interview-question.png`

Shows:

- Question 1 of 3: Python GIL question
- Real-Time Feed section (left)
  - Video stream placeholder
  - "Pause capturing" button
- Response Options section (right)
  - Audio recording interface
  - Text input area
- Submit Answer button

---

## 🎨 UI Component Details

### Color Scheme

```
Background:      #0E1117 (Dark Gray)
Text Primary:    #E6EAEF (Light Gray)
Text Secondary:  #8B949E (Medium Gray)
Accent Green:    #1A7F37 (Status: OK)
Accent Red:      #DA3633 (Status: Alert)
Accent Blue:     #0969DA (Buttons/Links)
```

### Typography

```
Main Title (H1):     Extra Large, Bold
Section Heading (H2): Large, Bold
Question (H3):       Large, Regular
Labels:              Small, Medium
Status Text:         Small, Bold
```

### Button States

```
NORMAL:        Background: #0969DA, Text: White
HOVER:         Background: #0860CA (Darker)
ACTIVE:        Background: #033D8B (Darkest)
DISABLED:      Background: #6E7681 (Gray)
SUCCESS:       Background: #1A7F37 (Green)
ERROR:         Background: #DA3633 (Red)
```

---

## 🔄 Data Flow Diagram

### Complete Session Flow

```
START
  ↓
[User enters role: "Backend Engineer"]
  ↓
[Slider: 3 questions]
  ↓
[Click: Generate Interview Session]
  ↓
STREAMLIT ─→ GOOGLE GEMINI API
  ├─ Prompt: "Generate 3 technical questions for Backend Engineer"
  ├─ Model: gemini-3.5-flash-lite
  ├─ Response Format: JSON
  └─ Returns: [Question 1, Question 2, Question 3]
  ↓
[Display Question 1]
  ├─ Enable Webcam (browser popup)
  ├─ Show video stream
  ├─ Start face detection (MediaPipe)
  └─ Monitor proctoring
  ↓
[Candidate provides answer]
  ├─ Audio recording OR
  └─ Text input
  ↓
[Click: Submit Answer]
  ↓
STREAMLIT ─→ GOOGLE GEMINI API
  ├─ Prompt: "Evaluate response: [question/answer/proctoring status]"
  ├─ Model: gemini-3.5-flash-lite
  ├─ Response Format: JSON
  └─ Returns: {score, clarity, strengths, gaps}
  ↓
[Store evaluation]
  ↓
[Load Question 2]
  ├─ Repeat proctoring/evaluation
  └─ ...
  ↓
[Load Question 3]
  ├─ Repeat proctoring/evaluation
  └─ ...
  ↓
[Session Complete]
  ↓
[Display Results Summary]
  ├─ Average score
  ├─ All evaluations
  ├─ Proctoring flags
  └─ Recommendations
  ↓
END
```

---

## 🚨 Proctoring System Visualization

### Face Detection Zones

```
┌───────────────────────────────────────────┐
│ Camera View (640 x 480)                   │
├───────────────────────────────────────────┤
│                                           │
│              Head Pose Check              │
│        ↑ Center Frame ↑                   │
│        |               |                   │
│   Left │               │ Right             │
│   Limit           Limit                    │
│  (-90px) ────── (0px) ────── (+90px)       │
│        |               |                   │
│        └─ Nose ────────┘ Nose Tracked     │
│                                           │
│                                           │
│        ┌─────────────────┐                │
│        │ Face Detected   │                │
│        │ [468 Points]    │                │
│        │                 │                │
│        │  ●●● ←Eye●●●   │                │
│        │ ●     ●     ●   │                │
│        │ ●   ●  ●  ●    │  Left Eye Set  │
│        │ ●     ●     ●   │  Right Eye Set │
│        │  ●●●  ↓ ●●●    │                │
│        │       Nose      │                │
│        └─────────────────┘                │
│                                           │
│  Status: ✅ Single Face Detected          │
│  Position: ✅ Head Centered               │
│  Eyes: ✅ Open (EAR: 0.27)                │
│  Blinks: ✅ Normal (16/min)               │
│                                           │
└───────────────────────────────────────────┘
```

### EAR Calculation Visualization

```
Eye Aspect Ratio Formula:
──────────────────────

           p2  p3
            \  /
        p1   \/   p4
            /\
           /  \
          p6  p5

EAR = (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)


Visual Representation:
─────────────────────

EYES OPEN (EAR ≈ 0.28):     EYES CLOSED (EAR ≈ 0.10):
┌─────────────┐             ┌──────────┐
│ ○ ○ ○ ○ ○ ○ │ Big ratio   │ ─ ─ ─ ─ │ Small ratio
└─────────────┘             └──────────┘

Threshold = 0.23

EAR > 0.23  ✓ Eyes Open
EAR ≤ 0.23  ✗ Eyes Closed (Flag)
```

---

## 📊 Technical Metrics Display

### Real-Time Monitoring Output

```
┌────────────────────────────────────────┐
│ Video Frame with Metrics               │
├────────────────────────────────────────┤
│                                        │
│  EAR: 0.25  ← Updated every frame     │
│  Blinks/Min: 15  ← Calculated/60s     │
│                                        │
│  [Video showing face with landmarks]   │
│  - Eye regions outlined in yellow      │
│  - Face bounding box                   │
│  - Landmarks visible                   │
│                                        │
│  ✅ Candidate Focused on Screen        │
│                                        │
└────────────────────────────────────────┘

Typical Values:
- EAR (Eyes Open): 0.25-0.35
- EAR (Eyes Closed): 0.10-0.15
- Blink Rate: 15-20 per minute
- Frame Rate: 30+ FPS
```

---

## 🎬 Session Workflow Sequence

```
Step 1: SETUP
┌─────────────────────────────────┐
│ • Enter role                    │
│ • Select question count         │
│ • Click "Generate"              │
└──────────────┬──────────────────┘
               ↓
Step 2: GENERATION
┌─────────────────────────────────┐
│ • Gemini API processes request  │
│ • Generates Q1, Q2, Q3          │
│ • Returns JSON                  │
└──────────────┬──────────────────┘
               ↓
Step 3: INTERVIEW SESSION
┌─────────────────────────────────┐
│ For each question (1-3):        │
│  • Display question             │
│  • Enable proctoring            │
│  • Candidate records/types       │
│  • Click submit                 │
└──────────────┬──────────────────┘
               ↓
Step 4: EVALUATION
┌─────────────────────────────────┐
│ • Gemini API evaluates response │
│ • Returns score + feedback      │
│ • Stores in session state       │
└──────────────┬──────────────────┘
               ↓
Step 5: COMPLETION
┌─────────────────────────────────┐
│ • Display results summary       │
│ • Show all evaluations          │
│ • Display proctoring flags      │
│ • Option to review/export       │
└─────────────────────────────────┘
```

---

## 💡 Key Interaction Points

### Interactive Elements

| Element           | Function           | Interaction                 |
| ----------------- | ------------------ | --------------------------- |
| Target Role Input | Define job role    | Type/paste role description |
| Questions Slider  | Choose # questions | Drag to 3-5 range           |
| Generate Button   | Initiate session   | Click to call API           |
| Pause/Resume      | Control camera     | Click to pause video        |
| Record Button     | Audio response     | Click to record             |
| Text Area         | Written response   | Type answer here            |
| Submit Button     | Submit response    | Click to evaluate           |

---

## 📚 Additional Resources

- **Screenshots Location:** `/screenshots/` folder
- **Main README:** See `README.md` for setup and configuration
- **API Documentation:** Google Gemini API docs
- **MediaPipe:** Facial Landmark Detection documentation

---

**Last Updated:** August 2026  
**Version:** 1.0
