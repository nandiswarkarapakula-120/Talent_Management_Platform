"""
Talent Management Platform - College Student Modules
Coding Practice, Resume Builder, ATS Resume Checker, Interview Preparation,
Mock Interviews, Skill Gap Analysis, Placement Tracker, Internship Recommendations,
Hackathon Updates, GitHub Portfolio Review, LinkedIn Profile Review, Daily Coding Challenge.
"""

import streamlit as st
import random
import re
from datetime import datetime

from database.db import run_query, now, get_profile_extra
from utils.ui import hero, section_title, kpi_card, glass_card_open, glass_card_close, badge
from utils.charts import donut_chart, bar_chart, gauge_chart, radar_chart
from utils.ai_engine import (ats_resume_score, analyze_skill_gap, ROLE_SKILL_MAP, coding_feedback,
                              INTERVIEW_QUESTIONS, mock_interview_feedback, suggest_projects)
from utils.pdf_generator import generate_report_pdf
from utils.file_reader import extract_text_from_upload
from urllib.parse import quote_plus


CODING_PROBLEMS = [
    {"title": "Two Sum", "desc": "Given an array of integers, return indices of two numbers that add up to a target.", "difficulty": "Easy"},
    {"title": "Reverse a String", "desc": "Write a function to reverse a given string.", "difficulty": "Easy"},
    {"title": "Find the Missing Number", "desc": "Given an array of n distinct numbers from 0 to n, find the missing one.", "difficulty": "Medium"},
    {"title": "Valid Parentheses", "desc": "Check if a string of brackets is validly nested.", "difficulty": "Medium"},
    {"title": "Longest Common Prefix", "desc": "Find the longest common prefix string among an array of strings.", "difficulty": "Medium"},
    {"title": "Merge Two Sorted Lists", "desc": "Merge two sorted linked lists into one sorted list.", "difficulty": "Hard"},
]


# ================= CODING PRACTICE =================
def page_coding_practice(user):
    hero("Coding Practice", "Sharpen your DSA skills with hands-on problems.", "💻")
    problem = st.selectbox("Choose a problem", [p["title"] for p in CODING_PROBLEMS])
    p = next(x for x in CODING_PROBLEMS if x["title"] == problem)
    glass_card_open()
    st.markdown(f"### {p['title']}")
    st.markdown(badge(p["difficulty"], "warning" if p["difficulty"] == "Medium" else ("danger" if p["difficulty"] == "Hard" else "success")), unsafe_allow_html=True)
    st.write(p["desc"])
    glass_card_close()

    language = st.selectbox("Language", ["Python", "Java", "C++", "JavaScript"])
    code = st.text_area("Write your solution here:", height=220, placeholder="def solve():\n    pass")
    if st.button("🔍 Get AI Feedback", type="primary"):
        if not code.strip():
            st.warning("Please write some code first.")
        else:
            fb = coding_feedback(code, language)
            for f in fb:
                st.write(f)
            run_query("""INSERT INTO coding_practice (user_id, problem, language, code, feedback, status, created_at)
                         VALUES (?,?,?,?,?,?,?)""",
                      (user["id"], p["title"], language, code, " | ".join(fb), "Attempted", now()))
            st.success("Solution submitted for review!")

    section_title("Your Recent Submissions")
    subs = run_query("SELECT * FROM coding_practice WHERE user_id=? ORDER BY created_at DESC LIMIT 5", (user["id"],), fetch=True)
    if subs:
        for s in subs:
            st.caption(f"🧩 {s['problem']} ({s['language']}) — {s['created_at'][:16].replace('T',' ')}")
    else:
        st.info("No submissions yet.")


# ================= DAILY CODING CHALLENGE =================
def page_daily_challenge(user):
    hero("Daily Coding Challenge", "One problem a day keeps rustiness away!", "🔥")
    today = datetime.now().strftime("%Y-%m-%d")
    random.seed(today)
    challenge = random.choice(CODING_PROBLEMS)

    glass_card_open()
    st.markdown(f"### 🌟 Today's Challenge: {challenge['title']}")
    st.markdown(badge(challenge["difficulty"], "warning"), unsafe_allow_html=True)
    st.write(challenge["desc"])
    glass_card_close()

    code = st.text_area("Submit your solution:", height=200, key="daily_code")
    if st.button("✅ Submit Daily Challenge", type="primary"):
        if code.strip():
            fb = coding_feedback(code, "Python")
            run_query("""INSERT INTO coding_practice (user_id, problem, language, code, feedback, status, created_at)
                         VALUES (?,?,?,?,?,?,?)""",
                      (user["id"], f"[Daily] {challenge['title']}", "Python", code, " | ".join(fb), "Completed", now()))
            st.success("🎉 Daily challenge completed! Streak +1")
            st.balloons()
        else:
            st.warning("Write your solution first.")

    streak_data = run_query("SELECT COUNT(*) as c FROM coding_practice WHERE user_id=? AND problem LIKE '[Daily]%'",
                             (user["id"],), fetchone=True)
    st.metric("🔥 Daily Challenge Streak", f"{streak_data['c']} days")


# ================= RESUME BUILDER =================
def page_resume_builder(user):
    hero("Resume Builder", "Create a professional, ATS-friendly resume.", "📄")
    with st.form("resume_builder_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full Name", value=user["fullname"])
        email = c2.text_input("Email", value=user["email"])
        phone = c1.text_input("Phone", value=user["mobile"])
        linkedin = c2.text_input("LinkedIn URL", placeholder="linkedin.com/in/yourname")
        summary = st.text_area("Professional Summary", placeholder="Motivated computer science student with...")
        education = st.text_area("Education", placeholder="B.Tech in CSE, XYZ University, 2022-2026, CGPA: 8.5")
        skills = st.text_area("Skills (comma separated)", placeholder="Python, SQL, Machine Learning, Git")
        experience = st.text_area("Experience / Internships", placeholder="Software Intern at ABC Corp — built REST APIs...")
        projects = st.text_area("Projects", placeholder="Movie Recommendation System — built using Python & Scikit-learn...")
        certifications = st.text_area("Certifications", placeholder="AWS Cloud Practitioner, Google Data Analytics")
        submitted = st.form_submit_button("📝 Generate Resume", type="primary")

    if submitted:
        resume_text = f"""{name}
{email} | {phone} | {linkedin}

SUMMARY
{summary}

EDUCATION
{education}

SKILLS
{skills}

EXPERIENCE
{experience}

PROJECTS
{projects}

CERTIFICATIONS
{certifications}
"""
        st.session_state.built_resume = resume_text
        run_query("INSERT INTO resume_data (user_id, resume_text, target_role, ats_score, feedback, created_at) VALUES (?,?,?,?,?,?)",
                   (user["id"], resume_text, "", 0, "", now()))
        st.success("Resume generated! Preview and download below.")

    if st.session_state.get("built_resume"):
        section_title("Resume Preview")
        st.text_area("Preview", value=st.session_state.built_resume, height=300, disabled=True)
        sections = {"Resume": st.session_state.built_resume.split("\n")}
        pdf_bytes = generate_report_pdf(f"Resume - {user['fullname']}", user["fullname"], sections)
        st.download_button("⬇️ Download Resume PDF", data=pdf_bytes, file_name=f"resume_{user['username']}.pdf", mime="application/pdf")


# ================= ATS RESUME CHECKER =================
def page_ats_checker(user):
    hero("ATS Resume Checker", "Upload your resume to check how well it performs against ATS systems.", "🎯")

    uploaded_file = st.file_uploader("📎 Upload your resume (PDF, DOCX or TXT)", type=["pdf", "docx", "txt"])
    jd_text = st.text_area("Paste target Job Description (optional, improves accuracy)", height=120)

    resume_text = ""
    if uploaded_file is not None:
        resume_text, error = extract_text_from_upload(uploaded_file)
        if error:
            st.error(error)
        else:
            st.success(f"✅ Resume '{uploaded_file.name}' read successfully ({len(resume_text.split())} words).")
            with st.expander("👁️ Preview extracted text"):
                st.text_area("Extracted Resume Text", value=resume_text, height=200, disabled=True)
    else:
        st.info("💡 Don't have a file handy? You can also use the text you generated in Resume Builder.")
        if st.session_state.get("built_resume"):
            if st.checkbox("Use my Resume Builder draft instead"):
                resume_text = st.session_state.built_resume

    if st.button("🔍 Analyze Resume", type="primary"):
        if not resume_text.strip():
            st.warning("Please upload a resume file first.")
        else:
            result = ats_resume_score(resume_text, jd_text)
            st.plotly_chart(gauge_chart(result["score"], "ATS Compatibility Score"), use_container_width=True)
            section_title("Feedback")
            for f in result["feedback"]:
                st.write(f)

            existing_resume = run_query("SELECT id FROM resume_data WHERE user_id=?", (user["id"],), fetchone=True)
            if existing_resume:
                run_query("""UPDATE resume_data SET resume_text=?, ats_score=?, feedback=? WHERE id=(
                             SELECT id FROM resume_data WHERE user_id=? ORDER BY created_at DESC LIMIT 1)""",
                          (resume_text, result["score"], " | ".join(result["feedback"]), user["id"]))
            else:
                run_query("INSERT INTO resume_data (user_id, resume_text, target_role, ats_score, feedback, created_at) VALUES (?,?,?,?,?,?)",
                           (user["id"], resume_text, "", result["score"], " | ".join(result["feedback"]), now()))


# ================= INTERVIEW PREPARATION =================
def page_interview_prep(user):
    hero("Interview Preparation", "Curated question banks by role and topic.", "📚")
    role = st.selectbox("Select target role", list(INTERVIEW_QUESTIONS.keys()))
    section_title(f"Common Questions for {role}")
    for i, q in enumerate(INTERVIEW_QUESTIONS[role], 1):
        glass_card_open()
        st.markdown(f"**{i}. {q}**")
        with st.expander("💡 Tips to answer"):
            st.write("Structure your answer using the STAR method: Situation, Task, Action, Result. Be specific and quantify your impact where possible.")
        glass_card_close()


# ================= MOCK INTERVIEWS =================
def page_mock_interviews(user):
    hero("Mock Interviews", "Practice with AI-powered interview simulation.", "🎤")
    role = st.selectbox("Interview for role", list(INTERVIEW_QUESTIONS.keys()), key="mock_role")

    if "mock_q_idx" not in st.session_state or st.session_state.get("mock_role_active") != role:
        st.session_state.mock_q_idx = 0
        st.session_state.mock_role_active = role

    questions = INTERVIEW_QUESTIONS[role]
    idx = st.session_state.mock_q_idx % len(questions)
    question = questions[idx]

    glass_card_open()
    st.markdown(f"### 🎤 Question {idx+1}/{len(questions)}")
    st.markdown(f"**{question}**")
    glass_card_close()

    answer = st.text_area("Your Answer", height=150, key=f"mock_ans_{idx}")
    c1, c2 = st.columns(2)
    if c1.button("✅ Submit Answer", type="primary"):
        if answer.strip():
            result = mock_interview_feedback(question, answer)
            if isinstance(result["feedback"], list):
                for f in result["feedback"]:
                    st.write(f)
            else:
                st.write(result["feedback"])
            if result["score"] is not None:
                st.metric("Score", f"{result['score']}/10")
            run_query("""INSERT INTO mock_interview_results (user_id, role, question, answer, feedback, score, created_at)
                         VALUES (?,?,?,?,?,?,?)""",
                      (user["id"], role, question, answer, str(result["feedback"]), result["score"] or 0, now()))
        else:
            st.warning("Please write an answer first.")
    if c2.button("⏭️ Next Question"):
        st.session_state.mock_q_idx += 1
        st.rerun()

    section_title("Your Interview History")
    history = run_query("SELECT * FROM mock_interview_results WHERE user_id=? ORDER BY created_at DESC LIMIT 5", (user["id"],), fetch=True)
    if history:
        avg_score = sum(h["score"] for h in history) / len(history)
        st.metric("Average Score", f"{round(avg_score,1)}/10")
    else:
        st.info("No interview history yet.")


# ================= SKILL GAP ANALYSIS =================
def page_skill_gap(user):
    hero("Skill Gap Analysis", "Find out exactly what to learn to reach your goal role.", "🧩")
    target_role = st.selectbox("Target Role", list(ROLE_SKILL_MAP.keys()))
    current_skills = st.text_area("Your current skills (comma separated)", placeholder="Python, SQL, Git")

    if st.button("🔍 Analyze Gap", type="primary"):
        result = analyze_skill_gap(current_skills, target_role)
        if "ai_text" in result:
            st.markdown(result["ai_text"])
        else:
            st.plotly_chart(gauge_chart(result["readiness_pct"], "Readiness Score"), use_container_width=True)
            c1, c2 = st.columns(2)
            with c1:
                section_title("✅ Skills You Have")
                for s in result["have"]:
                    st.markdown(f"- {s}")
                if not result["have"]:
                    st.caption("None yet — let's build them!")
            with c2:
                section_title("📚 Skills to Learn")
                for s in result["missing"]:
                    st.markdown(f"- {s}")
                if not result["missing"]:
                    st.success("You're fully equipped for this role!")


# ================= PLACEMENT TRACKER =================
def page_placement_tracker(user):
    hero("Placement Tracker", "Track your job applications and placement journey.", "📊")
    with st.form("placement_form"):
        c1, c2, c3 = st.columns(3)
        company = c1.text_input("Company")
        role = c2.text_input("Role")
        status = c3.selectbox("Status", ["Applied", "OA Cleared", "Interview Scheduled", "Offer Received", "Rejected"])
        if st.form_submit_button("➕ Add Application") and company.strip():
            run_query("INSERT INTO projects (user_id, title, description, skills, status, created_at) VALUES (?,?,?,?,?,?)",
                       (user["id"], f"[Placement] {company}", role, "", status, now()))
            st.success("Application tracked!")
            st.rerun()

    applications = run_query("SELECT * FROM projects WHERE user_id=? AND title LIKE '[Placement]%' ORDER BY created_at DESC",
                              (user["id"],), fetch=True)
    if applications:
        statuses = [a["status"] for a in applications]
        counts = {s: statuses.count(s) for s in set(statuses)}
        st.plotly_chart(donut_chart(list(counts.keys()), list(counts.values()), "Application Status"), use_container_width=True)
        for a in applications:
            glass_card_open()
            st.markdown(f"**🏢 {a['title'].replace('[Placement] ','')}** — {a['description']}")
            st.markdown(badge(a["status"], "info"), unsafe_allow_html=True)
            glass_card_close()
    else:
        st.info("No applications tracked yet. Add one above!")


# ================= INTERNSHIP RECOMMENDATIONS =================
INTERNSHIPS = [
    {"title": "Software Engineering Intern", "company": "TechNova Solutions", "skills": "Python, Git, APIs", "stipend": "₹15,000/mo"},
    {"title": "Data Analyst Intern", "company": "InsightWorks", "skills": "Excel, SQL, Python", "stipend": "₹12,000/mo"},
    {"title": "UI/UX Design Intern", "company": "PixelCraft Studio", "skills": "Figma, Prototyping", "stipend": "₹10,000/mo"},
    {"title": "Cloud Intern", "company": "CloudSphere Inc.", "skills": "AWS, Linux, Networking", "stipend": "₹18,000/mo"},
    {"title": "Marketing Intern", "company": "BrandBoost", "skills": "SEO, Content Writing", "stipend": "₹8,000/mo"},
]


def page_internship_recommendations(user):
    hero("Internship Recommendations", "Curated internship roles — click through to real internship platforms.", "💼")
    st.caption("These are sample role suggestions. Click a platform button to search live listings for that role.")

    platforms = {
        "Internshala": "https://internshala.com/internships/keywords-{q}",
        "LinkedIn": "https://www.linkedin.com/jobs/search/?keywords={q}&f_JT=I",
        "Indeed": "https://www.indeed.com/jobs?q={q}+intern",
        "Naukri": "https://www.naukri.com/{q}-internship-jobs",
    }

    for i in INTERNSHIPS:
        glass_card_open()
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**💼 {i['title']}** — {i['company']}")
            st.caption(f"Skills: {i['skills']}")
        with c2:
            st.markdown(badge(i["stipend"], "success"), unsafe_allow_html=True)
            if st.button("💾 Save to Tracker", key=f"intern_{i['title']}"):
                run_query("INSERT INTO projects (user_id, title, description, skills, status, created_at) VALUES (?,?,?,?,?,?)",
                           (user["id"], f"[Internship] {i['title']}", i["company"], i["skills"], "Saved", now()))
                st.success("Saved to your tracker!")

        st.markdown("**🔗 Find live openings for this role:**")
        link_cols = st.columns(len(platforms))
        query = quote_plus(i["title"])
        for col, (name, url_template) in zip(link_cols, platforms.items()):
            url = url_template.format(q=query.replace("+", "-") if name in ("Internshala", "Naukri") else query)
            with col:
                st.link_button(f"{name} →", url, use_container_width=True)
        glass_card_close()

    st.markdown("---")
    section_title("🔍 Search Internships Yourself")
    custom_query = st.text_input("Enter a role, skill, or company", placeholder="e.g. Python Developer, Marketing")
    if custom_query.strip():
        q = quote_plus(custom_query.strip())
        link_cols = st.columns(len(platforms))
        for col, (name, url_template) in zip(link_cols, platforms.items()):
            url = url_template.format(q=q.replace("+", "-") if name in ("Internshala", "Naukri") else q)
            with col:
                st.link_button(f"Search on {name}", url, use_container_width=True)


# ================= HACKATHON UPDATES =================
HACKATHONS = [
    {"name": "Smart India Hackathon", "date": "Aug 2026", "mode": "Offline", "theme": "GovTech & Public Welfare"},
    {"name": "HackTheNorth", "date": "Sept 2026", "mode": "Hybrid", "theme": "Open Innovation"},
    {"name": "CodeStorm AI Challenge", "date": "Oct 2026", "mode": "Online", "theme": "AI & Machine Learning"},
    {"name": "DevSprint 48hr", "date": "Nov 2026", "mode": "Online", "theme": "Web3 & FinTech"},
]


def page_hackathon_updates(user):
    hero("Hackathon Updates", "Discover upcoming hackathons — navigate straight to registration platforms.", "🏆")

    hackathon_platforms = {
        "Devpost": "https://devpost.com/hackathons?search={q}",
        "Unstop": "https://unstop.com/hackathons?searchTerm={q}",
        "HackerEarth": "https://www.hackerearth.com/challenges/hackathon/?search={q}",
        "MLH": "https://mlh.io/seasons/2026/events",
    }

    for h in HACKATHONS:
        glass_card_open()
        st.markdown(f"### 🏆 {h['name']}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(badge(h["date"], "purple"), unsafe_allow_html=True)
        c2.markdown(badge(h["mode"], "info"), unsafe_allow_html=True)
        c3.markdown(badge(h["theme"], "warning"), unsafe_allow_html=True)

        st.markdown("**🔗 Explore & Register:**")
        link_cols = st.columns(len(hackathon_platforms))
        q = quote_plus(h["theme"].split("&")[0].strip())
        for col, (name, url_template) in zip(link_cols, hackathon_platforms.items()):
            url = url_template.format(q=q)
            with col:
                st.link_button(f"{name} →", url, use_container_width=True)
        glass_card_close()

    st.markdown("---")
    section_title("🔍 Search Hackathons Yourself")
    custom_theme = st.text_input("Enter a theme or technology", placeholder="e.g. AI, Web3, FinTech")
    if custom_theme.strip():
        q = quote_plus(custom_theme.strip())
        link_cols = st.columns(len(hackathon_platforms))
        for col, (name, url_template) in zip(link_cols, hackathon_platforms.items()):
            with col:
                st.link_button(f"Search on {name}", url_template.format(q=q), use_container_width=True)


# ================= GITHUB PORTFOLIO REVIEW =================
def page_github_review(user):
    hero("GitHub Portfolio Review", "Upload a PDF export of your GitHub profile for instant AI feedback.", "🐙")
    st.caption("💡 Tip: Open your GitHub profile page and use your browser's 'Print → Save as PDF' option, then upload it below.")

    profile_url = st.text_input("GitHub Profile URL (optional, for reference)", placeholder="https://github.com/yourusername")
    uploaded_file = st.file_uploader("📎 Upload GitHub Profile PDF", type=["pdf", "txt"])

    manual_mode = st.checkbox("I don't have a PDF — let me answer a few quick questions instead")

    extracted_text = ""
    if uploaded_file is not None:
        extracted_text, error = extract_text_from_upload(uploaded_file)
        if error:
            st.error(error)
        else:
            st.success(f"✅ '{uploaded_file.name}' analyzed ({len(extracted_text.split())} words extracted).")

    if st.button("🔍 Review My Profile", type="primary"):
        if not extracted_text.strip() and not manual_mode:
            st.warning("Please upload a PDF export of your GitHub profile, or check the manual option above.")
            return

        score = 0
        tips = []

        if extracted_text.strip():
            text_l = extracted_text.lower()
            repo_matches = re.findall(r"repositor(?:y|ies)", text_l)
            pin_hits = "pinned" in text_l
            readme_hits = "readme" in text_l
            contrib_hits = bool(re.search(r"contribution|commits? in the last year|activity", text_l))
            followers_match = re.search(r"(\d+)\s*followers?", text_l)
            lang_hits = sum(1 for lang in ["python", "javascript", "java", "c++", "typescript", "html", "css", "go", "rust"] if lang in text_l)

            score += min(30, 10 + lang_hits * 4)
            tips.append(f"✅ Detected {lang_hits} programming languages mentioned on your profile." if lang_hits else "⚠️ Add more diverse language-based repositories to show range.")

            if pin_hits:
                score += 20
                tips.append("✅ Pinned repositories detected — great for first impressions.")
            else:
                tips.append("⚠️ Pin your 4-6 strongest projects so recruiters see them first.")

            if readme_hits:
                score += 20
                tips.append("✅ README content detected in your profile export.")
            else:
                tips.append("⚠️ Add clear README.md files with setup instructions & screenshots to your repos.")

            if contrib_hits:
                score += 20
                tips.append("✅ Contribution activity detected — consistency shows dedication.")
            else:
                tips.append("💡 Try to commit regularly; an active contribution graph builds credibility.")

            if followers_match:
                score += 10
                tips.append(f"✅ You have visibility with {followers_match.group(1)} followers.")
            else:
                tips.append("💡 Grow your network by following and engaging with other developers.")
        else:
            # Manual quick-question fallback
            repo_count = st.session_state.get("gh_repo_count", 5)
            score += 40
            tips.append("💡 For a more precise review, upload a PDF export of your GitHub profile next time.")

        st.plotly_chart(gauge_chart(min(100, score), "GitHub Profile Strength"), use_container_width=True)
        section_title("Feedback")
        for t in tips:
            st.write(t)

        run_query("INSERT INTO assessments (user_id, assessment_type, answers, result, score, created_at) VALUES (?,?,?,?,?,?)",
                   (user["id"], "GitHub Portfolio Review", profile_url, " | ".join(tips), min(100, score), now()))


# ================= LINKEDIN PROFILE REVIEW =================
LINKEDIN_BRANDING_COURSES = [
    "Optimize Your LinkedIn Profile — LinkedIn Learning",
    "Personal Branding on LinkedIn — Coursera",
    "LinkedIn Networking Mastery — Udemy",
    "Write a Standout LinkedIn About Section — HubSpot Academy",
    "Building Your Professional Brand — LinkedIn Learning",
]


def page_linkedin_review(user):
    hero("LinkedIn Profile Review", "Upload a PDF export of your LinkedIn profile for AI feedback.", "🔗")
    st.caption("💡 Tip: On your LinkedIn profile, click 'More' → 'Save to PDF' to export, then upload it below.")

    uploaded_file = st.file_uploader("📎 Upload LinkedIn Profile PDF", type=["pdf", "txt"])

    extracted_text = ""
    if uploaded_file is not None:
        extracted_text, error = extract_text_from_upload(uploaded_file)
        if error:
            st.error(error)
        else:
            st.success(f"✅ '{uploaded_file.name}' analyzed ({len(extracted_text.split())} words extracted).")
            with st.expander("👁️ Preview extracted text"):
                st.text_area("Extracted Text", value=extracted_text, height=200, disabled=True)

    if st.button("🔍 Review Profile", type="primary"):
        if not extracted_text.strip():
            st.warning("Please upload a PDF export of your LinkedIn profile first.")
            return

        text_l = extracted_text.lower()
        score = 0
        tips = []

        connections_match = re.search(r"(\d+[\+,]?\d*)\s*(connections|followers)", text_l)
        has_about = "about" in text_l
        has_experience = "experience" in text_l
        has_education = "education" in text_l
        has_skills = "skills" in text_l
        has_certs = "licenses & certifications" in text_l or "certification" in text_l
        has_featured = "featured" in text_l

        word_count = len(extracted_text.split())
        if word_count > 150:
            score += 15
            tips.append("✅ Good amount of profile content detected.")
        else:
            tips.append("⚠️ Your exported profile seems sparse — flesh out more sections on LinkedIn.")

        if has_about:
            score += 20
            tips.append("✅ 'About' section detected — great for storytelling.")
        else:
            tips.append("⚠️ Add a compelling 'About' section (3-5 sentences on goals & skills).")

        if has_experience:
            score += 15
            tips.append("✅ Experience section detected.")
        else:
            tips.append("⚠️ Add internships/part-time roles/projects under Experience.")

        if has_education:
            score += 10
            tips.append("✅ Education section detected.")

        if has_skills:
            score += 15
            tips.append("✅ Skills section detected — helps you show up in recruiter searches.")
        else:
            tips.append("⚠️ Add relevant skills — LinkedIn allows recruiters to filter candidates by skill.")

        if has_certs:
            score += 10
            tips.append("✅ Certifications detected — builds credibility.")
        else:
            tips.append("⚠️ Add certifications under 'Licenses & Certifications'.")

        if has_featured:
            score += 10
            tips.append("✅ Featured section detected — great for showcasing projects.")
        else:
            tips.append("⚠️ Use the 'Featured' section to pin your best projects/posts.")

        if connections_match:
            score += 5
            tips.append(f"✅ Network size detected: {connections_match.group(1)} {connections_match.group(2)}.")
        else:
            tips.append("💡 Grow your network — connect with alumni, recruiters, and industry peers.")

        st.plotly_chart(gauge_chart(min(100, score), "LinkedIn Profile Strength"), use_container_width=True)
        section_title("Feedback")
        for t in tips:
            st.write(t)

        run_query("INSERT INTO assessments (user_id, assessment_type, answers, result, score, created_at) VALUES (?,?,?,?,?,?)",
                   (user["id"], "LinkedIn Profile Review", "", " | ".join(tips), min(100, score), now()))

        section_title("🎓 Recommended Courses to Strengthen Your Personal Brand")
        for c in LINKEDIN_BRANDING_COURSES:
            glass_card_open()
            st.markdown(f"📘 {c}")
            glass_card_close()
