# 🚀 Quick Start Guide

## AI Live-Proctored Interview Coach

Get up and running in under 10 minutes!

---

## ⚡ 5-Minute Setup

### 1. Install Dependencies (2 minutes)

```bash
cd e:\interview-coach
pip install -r requirements.txt
```

**What it installs:**

- Streamlit (web framework)
- OpenCV (computer vision)
- MediaPipe (face detection)
- Google AI SDK (Gemini API)

---

### 2. Get Gemini API Key (2 minutes)

1. Visit: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Create folder: `.streamlit/` in project root
5. Create file: `.streamlit/secrets.toml`
6. Add this line:

```toml
GEMINI_API_KEY = "paste-your-key-here"
```

**Note:** Never share or commit this file!

---

### 3. Launch Application (1 minute)

```bash
streamlit run app.py
```

App opens at: http://localhost:8501

**Success indicators:**

- ✅ Title: "🎯 AI Live-Proctored Interview Coach"
- ✅ Sidebar: "Interview Setup"
- ✅ No error messages

---

## 🎯 Your First Interview (2-3 minutes)

### Step 1: Configure Session

1. Enter job role:
   - Example: `Backend Engineer with Python expertise`
2. Select questions: Use slider (3-5)
3. Click: `Generate Interview Session`
4. Wait: 5-10 seconds for AI to generate

### Step 2: Answer First Question

1. Read the displayed question
2. Allow camera access when prompted
3. Choose response method:
   - 🎙️ Click microphone to record audio
   - ⌨️ Type your answer in text area
4. Click: `Submit Answer`

### Step 3: Auto-Evaluation

- AI evaluates your response (5-10 seconds)
- Shows: Score, clarity, strengths, gaps
- Loads: Next question automatically

### Step 4: Repeat

- Answer questions 2 and 3
- Same workflow for each
- View final results when done

---

## 📊 What You'll See

### Real-Time Monitoring

```
EAR: 0.25          ← Eye opening ratio
Blinks/Min: 16     ← Blink frequency
Status: ✅ Focused  ← Proctoring status
```

### Evaluation Results

```json
{
  "overall_score": 8,
  "communication_clarity": "Good",
  "strengths": ["Clear explanation", "Good examples"],
  "gaps": ["Missing detail", "Incomplete answer"]
}
```

---

## 🆘 Troubleshooting Quick Fixes

| Issue               | Fix                                       |
| ------------------- | ----------------------------------------- |
| "API key not found" | Restart app after creating secrets.toml   |
| "No camera access"  | Allow browser camera permission           |
| "Face not detected" | Ensure good lighting, face in center      |
| "App won't start"   | Check Python 3.8+, reinstall requirements |
| "Slow performance"  | Close other apps, check internet          |

---

## 📚 Next Steps

### Learn More

- **Setup Details:** See `README.md`
- **Visual Walkthrough:** See `VISUAL_GUIDE.md`
- **All Docs:** See `DOCUMENTATION_SUMMARY.md`

### Explore Features

- Try different job roles
- Experiment with question counts
- Test audio and text responses
- Review evaluation feedback

### Customize

- Modify target role descriptions
- Adjust question counts
- Experiment with different interview types

---

## 🎓 Example Workflow

```
MINUTE 1: Setup
├─ Enter: "Data Engineer - Python & SQL"
├─ Select: 3 questions
└─ Click: Generate

MINUTE 2-3: Interview Question 1
├─ Read: Machine Learning Systems Design
├─ Record: Audio response (1-2 minutes)
└─ Submit

MINUTE 4-5: AI Evaluation + Question 2
├─ View: Score 7/10, Communication Good
├─ Read: Database Optimization
└─ Type: Text response

MINUTE 6-7: AI Evaluation + Question 3
├─ View: Score 8/10, Strengths Listed
├─ Read: API Design Patterns
└─ Record: Audio response

MINUTE 8-9: Final Evaluation
├─ View: Overall Performance
├─ Review: All Feedback
└─ See: Recommendations
```

---

## ✨ Key Features to Explore

1. **Real-Time Proctoring**
   - Watch video feed with face detection
   - See eye tracking in action
   - Monitor for cheating attempts

2. **Dual Response Options**
   - Record audio answers
   - Type written responses
   - Use either or both

3. **AI Feedback**
   - Get scored evaluations
   - See strengths highlighted
   - Identify improvement areas

4. **Session Tracking**
   - All evaluations stored
   - Proctoring flags logged
   - Complete results summary

---

## 🎯 Pro Tips

**Tip 1: Quality Answers**

- Speak clearly for audio
- Type complete thoughts
- Include specific examples
- Show your reasoning

**Tip 2: Proctoring Tips**

- Good lighting is important
- Face camera directly
- Minimize head movement
- Avoid looking away

**Tip 3: Multiple Attempts**

- Try with different roles
- Test various questions
- Compare your scores
- Practice improvement areas

**Tip 4: Before Starting**

- Test camera works
- Verify internet connection
- Have quiet environment
- Prepare notes if needed

---

## 📋 System Requirements

**Minimum:**

- Python 3.8+
- 4GB RAM
- Internet connection
- Webcam or USB camera
- Modern browser (Chrome, Firefox, Safari, Edge)

**Recommended:**

- Python 3.10+
- 8GB RAM
- Good internet speed
- Built-in laptop webcam
- Dedicated GPU (optional, faster processing)

---

## 🔐 Important Notes

⚠️ **Never:**

- Share your API key
- Commit `.streamlit/secrets.toml` to git
- Leave the app running unattended with API key visible

✅ **Always:**

- Keep API key confidential
- Use `.gitignore` to exclude secrets
- Review privacy policies
- Test with sample data first

---

## 🎨 Interface Overview

### Sidebar (Left)

- Job role input
- Question count slider
- Generate button
- Remains visible during interview

### Main Area (Center/Right)

- Question display
- Real-time video feed
- Response input options
- Submit button
- Results display

### Top Bar

- App title and logo
- Deploy button
- Menu options
- Stop/Run controls

---

## 📊 Understanding Your Results

### Score Breakdown

- **9-10:** Excellent answer
- **7-8:** Good answer
- **5-6:** Average answer
- **3-4:** Below average
- **1-2:** Poor answer

### Clarity Assessment

- **Excellent:** Clear, well-structured
- **Good:** Mostly clear, good flow
- **Fair:** Some confusion, incomplete
- **Poor:** Unclear, hard to follow

### Strengths

- Positive aspects you demonstrated
- Areas you did well
- Good practices shown

### Gaps

- Missing information
- Incomplete explanations
- Areas for improvement
- Follow-up topics to study

---

## 🔄 Workflow Summary

```
1. LAUNCH
   ↓
2. CONFIGURE
   ├─ Role
   ├─ Questions
   └─ Generate
   ↓
3. INTERVIEW
   ├─ Question 1 → Answer → Submit
   ├─ Question 2 → Answer → Submit
   └─ Question 3 → Answer → Submit
   ↓
4. RESULTS
   ├─ Scores
   ├─ Feedback
   └─ Recommendations
   ↓
5. REVIEW & IMPROVE
```

---

## 💡 Common Questions

**Q: Can I skip a question?**  
A: No, you must answer each question before moving to next.

**Q: Can I use external resources?**  
A: The proctoring system monitors for cheating. Keep camera focused on you.

**Q: How long does it take?**  
A: Typically 8-15 minutes total depending on answer length and question complexity.

**Q: Can I save my results?**  
A: Results are stored in session memory. Take screenshots to save permanently.

**Q: Can I retry?**  
A: Yes! Generate a new session with same or different role to retry.

**Q: What if I make a mistake?**  
A: You can't undo submitted answers, but you can generate new sessions to retake.

---

## 🚀 Advanced Usage

### Different Interview Scenarios

```
Senior Engineer:
- Role: "Senior Backend Engineer"
- Questions: 5
- Difficulty: Technical depth expected

Intern Interview:
- Role: "Junior Developer - Python"
- Questions: 3
- Difficulty: Fundamental concepts

Specific Focus:
- Role: "DevOps Engineer - Kubernetes"
- Questions: 4
- Difficulty: Specialized knowledge
```

### Custom Role Examples

- `Full-Stack Engineer with React and Node.js`
- `Data Scientist specializing in ML Ops`
- `DevOps Engineer with AWS and Docker experience`
- `Mobile Developer - iOS Swift Development`
- `QA Automation Engineer - Selenium and Python`

---

## 📞 Getting Help

### Documentation

1. **Quick answers:** This file
2. **Setup help:** `README.md`
3. **Visual guide:** `VISUAL_GUIDE.md`
4. **Full reference:** `DOCUMENTATION_SUMMARY.md`

### Common Issues

1. Check `README.md` → "Troubleshooting" section
2. Review error message carefully
3. Verify all setup steps completed
4. Test with different browser if needed

### Still Stuck?

1. Read the detailed README
2. Check browser console for errors
3. Verify API key works
4. Test camera separately
5. Try fresh browser tab

---

## ✅ Pre-Flight Checklist

Before starting your interview:

- ⬜ Python installed (3.8+)
- ⬜ Dependencies installed (`pip install -r requirements.txt`)
- ⬜ API key configured (`.streamlit/secrets.toml`)
- ⬜ App running (`streamlit run app.py`)
- ⬜ Browser open (`http://localhost:8501`)
- ⬜ Camera working and accessible
- ⬜ Microphone working (for audio responses)
- ⬜ Good lighting and camera position
- ⬜ Quiet environment
- ⬜ Internet connection stable

---

## 🎯 You're Ready!

Once your checklist is complete:

1. Open `http://localhost:8501`
2. Enter a job role
3. Click "Generate Interview Session"
4. Start answering questions
5. Get AI feedback
6. Practice and improve!

---

## 📚 Resource Links

- **Streamlit Docs:** https://docs.streamlit.io
- **Google Gemini API:** https://ai.google.dev
- **MediaPipe:** https://mediapipe.dev
- **OpenCV:** https://docs.opencv.org
- **Python Docs:** https://docs.python.org

---

## 🎉 Good Luck!

You're all set to start practicing technical interviews with AI coaching!

**Tips for success:**

- Practice multiple times with different roles
- Read feedback carefully and improve
- Record audio to practice speaking clarity
- Type responses to practice written communication
- Review gaps and study those topics
- Come back and retry after studying

**Remember:** The more you practice, the better your interview performance will be! 🚀

---

**Need more details?** Check out the full documentation:

- 📖 `README.md` - Comprehensive guide
- 🎨 `VISUAL_GUIDE.md` - UI walkthrough
- 📋 `DOCUMENTATION_SUMMARY.md` - All resources

**Last Updated:** August 20, 2026  
**Version:** 1.0  
**Status:** Ready to use ✅
