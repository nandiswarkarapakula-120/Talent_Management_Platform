# 🌐 TalentSphere Elevate

**AI-Powered Career Guidance Platform** — built with Python, Streamlit, SQLite, Pandas, NumPy, Plotly, Scikit-learn and ReportLab.

TalentSphere Elevate guides **High School Students**, **College Students**, and **Working Professionals** through their entire career journey — from self-discovery and skill-building to resumes, interviews, and certifications — with a dedicated **Admin Portal** to manage the whole platform.

---

## ✨ Highlights

- 🔐 Full authentication: Signup, Login, Forgot Password, Logout — **no email verification required**
- 🎯 Auto-redirect to a category-specific dashboard right after signup
- 🧑‍🎓 **High School Dashboard** — 10 modules, with an extended profile (school, board, study year, favorite subjects, career interest area) that drives personalized course recommendations
- 🎓 **College Dashboard** — 12 modules, with an extended profile (college, branch, specialization, CGPA, GitHub/LinkedIn/portfolio links). Includes resume/GitHub/LinkedIn **PDF upload analysis** and **live navigation** to internship/hackathon platforms
- 💼 **Working Professional Dashboard** — 9 modules, with an extended profile (company, designation, industry, experience, CTC). Includes **Salary Benchmark**, **Networking & Visibility Builder**, AI-predicted certifications, and trending-role navigation to job boards
- 🛡️ **Admin Portal** — Manage Users, Manage Courses, Career Paths, Upload Materials, Create Quizzes, View Analytics, Send Notifications, Generate Reports
- 🤖 AI features run on **smart rule-based / scikit-learn logic out of the box** (no API key needed) and **automatically upgrade** to OpenAI or Gemini the moment you add an API key — zero code changes required
- 📄 Downloadable **PDF certificates & reports** generated with ReportLab, including a comprehensive **Profile Verification Report** (profile snapshot + assessment/quiz/goal history + a unique verification code) for future reference
- 📎 **Resume, GitHub profile, and LinkedIn profile PDF/DOCX upload & analysis** — no manual re-typing needed
- 🔗 **Live navigation buttons** to real platforms (Internshala, LinkedIn Jobs, Naukri, Indeed, Devpost, Unstop, HackerEarth, Glassdoor, etc.) instead of static lists
- 📊 Beautiful **Plotly** dashboards: donut, line, bar, radar & gauge charts
- 🎨 Premium **glassmorphism UI**, smooth animations, gradient hero banners, responsive layout

---

## 🆕 What's new in this update

| Area | Update |
|---|---|
| High School Profile | Added school name, board, study year, city, favorite subjects, career interest area, target exam. Courses in the Learning Dashboard and quiz results are now ranked/matched against these selections. |
| College Profile | Added college name, branch, specialization, CGPA, graduation year, GitHub/LinkedIn/portfolio links, target role. |
| ATS Resume Checker | Now accepts a **file upload** (PDF/DOCX/TXT) instead of pasted text. |
| Internship Recommendations | Each listing now links out to **live searches** on Internshala, LinkedIn, Indeed, and Naukri; plus a free-text search box. |
| Hackathon Updates | Each listing now links out to **live searches** on Devpost, Unstop, HackerEarth, and MLH; plus a free-text search box. |
| GitHub Portfolio Review | Now analyzes an **uploaded PDF export** of your GitHub profile instead of manual checkboxes. |
| LinkedIn Profile Review | Now analyzes an **uploaded PDF export** of your LinkedIn profile, plus recommends 5 personal-branding courses. |
| PDF Reports | Added `generate_verification_report()` — a rich PDF combining your profile snapshot, assessments, quizzes, learning progress, goals, and certificates with a unique verification code, available from **My Profile**. |
| Professional Profile | Added company name, role/designation, industry, years of experience, current CTC, work location, LinkedIn, key skills, career goal. |
| Industry Trend Dashboard | Now lists **trending job roles per industry**, each with buttons linking to live job searches (LinkedIn Jobs, Naukri, Indeed, Glassdoor). |
| Certification Suggestions | Expanded to 7 domains; added an **AI-predicted certifications** feature based on your entered skills, plus matching recommended courses. |
| Resume Update Assistant | Now accepts a **file upload** and a **target role** selection, then highlights which role-specific keywords are present vs. missing. |
| New: Salary Benchmark | Compare your current CTC against market ranges by role and experience band. |
| New: Networking & Visibility Builder | Weekly networking checklist plus links to LinkedIn Events, Meetup, and Eventbrite. |

---

## 🗂️ Project Structure

```
TalentSphere_Elevate/
├── app.py                     # Main entry point & router (run this file)
├── requirements.txt
├── .streamlit/
│   └── config.toml            # Theme configuration
├── assets/
│   └── style.css              # Glassmorphism UI, animations, theming
├── database/
│   ├── db.py                  # SQLite schema, CRUD helpers, seed data
│   └── talentsphere.db        # Auto-created on first run
├── auth/
│   └── auth_utils.py          # Signup / Login / Forgot Password logic
├── utils/
│   ├── ai_engine.py           # AI features (rule-based + pluggable OpenAI/Gemini)
│   ├── pdf_generator.py       # ReportLab certificates & reports
│   ├── charts.py              # Reusable Plotly chart components
│   └── ui.py                  # Reusable UI components (hero, cards, KPIs)
└── modules/
    ├── common.py               # Profile, Notifications, Chatbot, Progress, Certificates
    ├── high_school.py          # High School Student modules
    ├── college.py               # College Student modules
    ├── professional.py          # Working Professional modules
    └── admin.py                 # Admin Portal modules
```

---

## 🚀 Getting Started (VS Code)

### 1. Open the project
Open the `TalentSphere_Elevate` folder in VS Code.

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**

### 5. Default Admin Login
```
Username: admin
Password: Admin@123
```
The database (`database/talentsphere.db`) and this default admin account are created automatically the first time you run the app.

---

## 🤖 Enabling Live AI (Optional)

By default, all AI features (career recommendations, resume/ATS scoring, mock interview feedback, chatbot, etc.) run on an **intelligent offline engine** built with TF-IDF, cosine similarity, and rule-based logic from scikit-learn — so the app is 100% functional with zero setup.

To switch to a live LLM (OpenAI or Gemini), simply set an environment variable **before** launching the app — no code changes needed:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."          # macOS/Linux
set OPENAI_API_KEY=sk-...               # Windows (cmd)

# OR Gemini
export GEMINI_API_KEY="..."
```
```bash
streamlit run app.py
```
The `utils/ai_engine.py` module automatically detects the key and routes all AI calls through the live API using the Strategy Pattern — the rest of the app is unaffected.

---

## 🗄️ Database Schema (SQLite)

`users` (includes a `profile_extra` JSON column storing category-specific fields like school/college/company details), `admins`, `assessments`, `learning_progress`, `courses`, `career_paths`, `notifications`,
`certificates`, `reports`, `resume_data`, `quiz_results`, `mock_interview_results`, `coding_practice`,
`projects`, `achievements`, `goals`, `chat_history`, `admin_actions`

All tables are created automatically with `init_db()` on first launch, along with seed data for career paths and courses. Schema migrations (like the `profile_extra` column) are applied automatically and safely on every startup, so existing databases upgrade without data loss.

---

## 🧭 User Journey

1. User signs up (no email verification) → redirected instantly to their category dashboard
2. User explores modules relevant to their stage: assessments, quizzes, skill tools
3. AI analyzes results → strengths/weaknesses identified → personalized recommendations generated
4. User completes learning tasks → progress tracked continuously with visual dashboards
5. Certificates & reports generated and downloadable as PDF at any time
6. Admin manages the entire platform via a completely separate, secure Admin Portal

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI Framework | Streamlit |
| Database | SQLite |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly, Matplotlib |
| AI / ML | Scikit-learn (TF-IDF, Cosine Similarity), optional OpenAI/Gemini |
| PDF Generation | ReportLab |
| Styling | Custom CSS (Glassmorphism, animations) |

---

## 📌 Notes

- This project uses **local password hashing (HMAC-SHA256)** — for production deployment, pair with HTTPS and consider a managed auth provider.
- The SQLite database file is created locally; delete `database/talentsphere.db` to reset all data back to the seeded defaults.
- All chart colors and the UI theme can be customized in `assets/style.css` and `utils/charts.py`.

---

Built with ❤️ for learners and professionals everywhere — **TalentSphere Elevate**.
