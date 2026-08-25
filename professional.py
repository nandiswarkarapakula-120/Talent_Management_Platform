"""
TalentSphere Elevate - Working Professional Modules
Skill Assessment, Industry Trend Dashboard, Certification Suggestions,
Resume Update Assistant, Career Switching Guide, Promotion Readiness Score, AI Career Coach.
"""

import streamlit as st
from datetime import datetime
from urllib.parse import quote_plus

from database.db import run_query, now, get_profile_extra
from utils.ui import hero, section_title, kpi_card, glass_card_open, glass_card_close, badge
from utils.charts import radar_chart, line_chart, bar_chart, gauge_chart, donut_chart
from utils.ai_engine import ats_resume_score, ai_generate, ai_status, ROLE_SKILL_MAP
from utils.file_reader import extract_text_from_upload


# ================= SKILL ASSESSMENT =================
def page_skill_assessment(user):
    hero("Skill Assessment", "Benchmark your current professional skill levels.", "📐")
    skill_areas = ["Technical Expertise", "Communication", "Leadership", "Problem Solving", "Adaptability", "Domain Knowledge"]
    ratings = {}
    with st.form("skill_assess_form"):
        for s in skill_areas:
            ratings[s] = st.slider(s, 0, 100, 60)
        submitted = st.form_submit_button("📊 Assess My Skills", type="primary")

    if submitted:
        st.plotly_chart(radar_chart(list(ratings.keys()), list(ratings.values()), "Your Skill Radar"), use_container_width=True)
        avg = round(sum(ratings.values()) / len(ratings), 1)
        weakest = min(ratings, key=ratings.get)
        st.metric("Overall Skill Score", f"{avg}/100")
        st.info(f"💡 Focus area for growth: **{weakest}**")
        run_query("INSERT INTO assessments (user_id, assessment_type, answers, result, score, created_at) VALUES (?,?,?,?,?,?)",
                   (user["id"], "Skill Assessment", str(ratings), weakest, avg, now()))


# ================= INDUSTRY TREND DASHBOARD =================
INDUSTRY_TRENDS = {
    "Technology": {"growth": [12, 18, 22, 28, 35, 42], "hot_skills": ["AI/ML", "Cloud Computing", "Cybersecurity", "DevOps"],
                   "trending_roles": ["AI/ML Engineer", "Cloud Architect", "DevOps Engineer", "Cybersecurity Analyst", "Full-Stack Developer"]},
    "Finance": {"growth": [8, 10, 13, 15, 18, 21], "hot_skills": ["FinTech", "Risk Analytics", "Blockchain", "Compliance"],
                "trending_roles": ["Financial Analyst", "Risk Manager", "Blockchain Developer", "Compliance Officer", "Investment Analyst"]},
    "Healthcare": {"growth": [10, 14, 17, 20, 24, 29], "hot_skills": ["HealthTech", "Data Privacy", "Telemedicine", "Bioinformatics"],
                   "trending_roles": ["Health Data Analyst", "Telemedicine Coordinator", "Bioinformatics Scientist", "Healthcare IT Consultant"]},
    "Marketing": {"growth": [6, 9, 11, 14, 16, 19], "hot_skills": ["SEO/SEM", "Marketing Analytics", "Content Strategy", "AI Copywriting"],
                  "trending_roles": ["Digital Marketing Manager", "Marketing Analytics Lead", "SEO Specialist", "Content Strategist"]},
}

JOB_PLATFORMS = {
    "LinkedIn Jobs": "https://www.linkedin.com/jobs/search/?keywords={q}",
    "Naukri": "https://www.naukri.com/{q}-jobs",
    "Indeed": "https://www.indeed.com/jobs?q={q}",
    "Glassdoor": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={q}",
}


def page_industry_trends(user):
    hero("Industry Trend Dashboard", "Stay ahead with the latest industry growth trends.", "📈")
    extra = get_profile_extra(user)
    default_industry = extra.get("industry", "") if extra.get("industry", "") in INDUSTRY_TRENDS else "Technology"
    industry = st.selectbox("Select Industry", list(INDUSTRY_TRENDS.keys()),
                             index=list(INDUSTRY_TRENDS.keys()).index(default_industry))
    data = INDUSTRY_TRENDS[industry]
    years = [str(datetime.now().year - 5 + i) for i in range(6)]

    st.plotly_chart(line_chart(years, data["growth"], f"{industry} Industry Growth (%)", "Year", "Growth %"),
                     use_container_width=True)

    section_title("🔥 Hot Skills in Demand")
    cols = st.columns(len(data["hot_skills"]))
    for c, skill in zip(cols, data["hot_skills"]):
        with c:
            glass_card_open()
            st.markdown(f"**{skill}**")
            glass_card_close()

    section_title("🚀 Trending Job Roles — Click to Explore Live Openings")
    for role in data["trending_roles"]:
        glass_card_open()
        st.markdown(f"**💼 {role}**")
        q = quote_plus(role)
        link_cols = st.columns(len(JOB_PLATFORMS))
        for col, (name, url_template) in zip(link_cols, JOB_PLATFORMS.items()):
            url = url_template.format(q=q.replace("+", "-") if name == "Naukri" else q)
            with col:
                st.link_button(f"{name} →", url, use_container_width=True)
        glass_card_close()


# ================= CERTIFICATION SUGGESTIONS =================
CERTIFICATIONS = {
    "Technology": ["AWS Certified Solutions Architect", "Google Professional Data Engineer", "Certified Kubernetes Administrator",
                   "Microsoft Azure Fundamentals", "Google Professional Cloud Architect", "Certified Ethical Hacker (CEH)",
                   "TensorFlow Developer Certificate", "HashiCorp Certified Terraform Associate"],
    "Finance": ["CFA Level 1", "FRM (Financial Risk Manager)", "Certified Blockchain Professional",
                "Chartered Accountant (CA)", "Certified Financial Planner (CFP)", "CPA (Certified Public Accountant)"],
    "Healthcare": ["Certified Health Data Analyst", "HIPAA Compliance Certification", "Certified Clinical Research Associate",
                   "Health Informatics Certificate"],
    "Marketing": ["Google Analytics Certification", "HubSpot Content Marketing", "Meta Blueprint Certification",
                  "Google Ads Certification", "Certified Digital Marketing Professional (CDMP)"],
    "Management": ["PMP (Project Management Professional)", "Certified ScrumMaster (CSM)", "Six Sigma Green Belt",
                   "Prince2 Foundation & Practitioner", "SAFe Agilist Certification"],
    "Data & AI": ["Microsoft Certified: Azure Data Scientist Associate", "IBM Data Science Professional Certificate",
                  "Google Data Analytics Certificate", "Deep Learning Specialization (deeplearning.ai)"],
    "Human Resources": ["SHRM Certified Professional (SHRM-CP)", "HR Analytics Certification", "Certified Compensation Professional"],
}

CERT_ROLE_SKILL_MAP = {
    "AWS Certified Solutions Architect": ["aws", "cloud"], "Google Professional Data Engineer": ["data", "python", "sql"],
    "Certified Kubernetes Administrator": ["kubernetes", "docker", "devops"], "Microsoft Azure Fundamentals": ["azure", "cloud"],
    "TensorFlow Developer Certificate": ["python", "machine learning", "tensorflow"], "Certified Ethical Hacker (CEH)": ["security", "networking"],
    "CFA Level 1": ["finance", "investment"], "FRM (Financial Risk Manager)": ["risk", "finance"],
    "PMP (Project Management Professional)": ["management", "leadership", "project"], "Certified ScrumMaster (CSM)": ["agile", "scrum", "management"],
    "Google Analytics Certification": ["marketing", "analytics", "seo"], "IBM Data Science Professional Certificate": ["python", "data", "machine learning"],
}


def _predict_certifications(skills_text):
    """Suggest certifications whose associated keywords match the user's stated skills."""
    skills_l = [s.strip().lower() for s in skills_text.split(",") if s.strip()]
    if not skills_l:
        return []
    scored = []
    for cert, keywords in CERT_ROLE_SKILL_MAP.items():
        overlap = sum(1 for k in keywords if any(k in s or s in k for s in skills_l))
        if overlap:
            scored.append((cert, overlap))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [c for c, _ in scored[:5]]


def page_certification_suggestions(user):
    hero("Certification Suggestions", "Boost your resume with in-demand certifications.", "🎓")
    extra = get_profile_extra(user)

    section_title("🤖 AI-Predicted Certifications Based on Your Skills")
    default_skills = extra.get("key_skills", "")
    skills_input = st.text_area("Your current skills (comma separated)", value=default_skills,
                                 placeholder="e.g. Python, AWS, Project Management")
    if st.button("🔮 Predict Certifications", type="primary"):
        predicted = _predict_certifications(skills_input)
        if predicted:
            for cert in predicted:
                glass_card_open()
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"**🏅 {cert}**  {badge('Predicted Match', 'success')}", unsafe_allow_html=True)
                if c2.button("Add to Goals", key=f"pred_cert_{cert}"):
                    run_query("INSERT INTO goals (user_id, goal_text, target_date, created_at) VALUES (?,?,?,?)",
                               (user["id"], f"Complete certification: {cert}", "", now()))
                    st.success("Added to your Goal Tracker!")
                glass_card_close()
        else:
            st.info("Add a few recognizable skills (e.g. Python, AWS, Finance) to get AI-predicted matches.")

    st.markdown("---")
    section_title("📚 Browse Certifications by Domain")
    domain = st.selectbox("Your domain", list(CERTIFICATIONS.keys()))
    for cert in CERTIFICATIONS[domain]:
        glass_card_open()
        c1, c2 = st.columns([3, 1])
        c1.markdown(f"**🏅 {cert}**")
        if c2.button("Add to Goals", key=f"cert_{cert}"):
            run_query("INSERT INTO goals (user_id, goal_text, target_date, created_at) VALUES (?,?,?,?)",
                       (user["id"], f"Complete certification: {cert}", "", now()))
            st.success("Added to your Goal Tracker!")
        glass_card_close()

    section_title("🎓 Recommended Learning Courses")
    courses = run_query("SELECT * FROM courses WHERE category='Working Professional' OR category='All'", fetch=True)
    matching = [c for c in courses if domain.lower() in f"{c['title']} {c['description']}".lower()] or courses[:3]
    cols = st.columns(min(3, len(matching)))
    for col, c in zip(cols, matching[:3]):
        with col:
            glass_card_open()
            st.markdown(f"**📘 {c['title']}**")
            st.caption(c["description"])
            glass_card_close()


# ================= RESUME UPDATE ASSISTANT =================
def page_resume_update_assistant(user):
    hero("Resume Update Assistant", "Upload your resume and pick a target role for tailored update suggestions.", "📝")

    uploaded_file = st.file_uploader("📎 Upload your current resume (PDF, DOCX or TXT)", type=["pdf", "docx", "txt"])
    target_role = st.selectbox("Target Role / Job Title", list(ROLE_SKILL_MAP.keys()) + ["Other (type below)"])
    custom_role = ""
    if target_role == "Other (type below)":
        custom_role = st.text_input("Enter your target role", placeholder="e.g. Senior Software Engineer")
    final_role = custom_role.strip() if target_role == "Other (type below)" else target_role

    resume_text = ""
    if uploaded_file is not None:
        resume_text, error = extract_text_from_upload(uploaded_file)
        if error:
            st.error(error)
        else:
            st.success(f"✅ '{uploaded_file.name}' read successfully ({len(resume_text.split())} words).")

    if st.button("🔍 Analyze & Suggest Updates", type="primary"):
        if not resume_text.strip():
            st.warning("Please upload your resume file first.")
        else:
            result = ats_resume_score(resume_text, final_role)
            st.plotly_chart(gauge_chart(result["score"], "Resume Strength Score"), use_container_width=True)
            section_title("General Feedback")
            for f in result["feedback"]:
                st.write(f)

            required_skills = ROLE_SKILL_MAP.get(final_role, [])
            if required_skills:
                text_l = resume_text.lower()
                missing_keywords = [s for s in required_skills if s.split("/")[0].lower() not in text_l]
                present_keywords = [s for s in required_skills if s not in missing_keywords]

                section_title(f"🎯 Role-Specific Suggestions for {final_role}")
                if present_keywords:
                    st.write(f"✅ Your resume already reflects: {', '.join(present_keywords)}")
                if missing_keywords:
                    st.write(f"⚠️ Consider adding these keywords/skills relevant to {final_role}: **{', '.join(missing_keywords)}**")
                else:
                    st.success("Great! Your resume covers all the key skills for this role.")

            st.markdown("---")
            st.markdown("**💡 Additional tips for professionals:**")
            st.write("- Lead with recent, most relevant experience (reverse chronological order).")
            st.write("- Quantify leadership impact: team size managed, budget owned, % improvements.")
            st.write(f"- Tailor keywords to match the {final_role} job description exactly.")

            run_query("INSERT INTO resume_data (user_id, resume_text, target_role, ats_score, feedback, created_at) VALUES (?,?,?,?,?,?)",
                       (user["id"], resume_text, final_role, result["score"], " | ".join(result["feedback"]), now()))

            section_title("🎓 Recommended Courses to Close the Gaps")
            courses = run_query("SELECT * FROM courses WHERE category='Working Professional' OR category='All'", fetch=True)
            matching = [c for c in courses if final_role.lower() in f"{c['title']} {c['description']}".lower()] or courses[:3]
            cols = st.columns(min(3, len(matching)))
            for col, c in zip(cols, matching[:3]):
                with col:
                    glass_card_open()
                    st.markdown(f"**📘 {c['title']}**")
                    st.caption(c["description"])
                    glass_card_close()


# ================= CAREER SWITCHING GUIDE =================
def page_career_switching_guide(user):
    hero("Career Switching Guide", "Plan a confident transition into a new field.", "🔄")
    current_role = st.text_input("Current Role", placeholder="e.g. Marketing Executive")
    target_role = st.selectbox("Target Role", list(ROLE_SKILL_MAP.keys()))

    if st.button("🗺️ Generate Switching Plan", type="primary"):
        required = ROLE_SKILL_MAP.get(target_role, [])
        st.plotly_chart(bar_chart(required, [70] * len(required), f"Key Skills for {target_role}", horizontal=True),
                         use_container_width=True)
        section_title("📋 Transition Roadmap")
        steps = [
            f"**Step 1 — Assess:** Compare your experience as a {current_role or 'professional'} against {target_role} requirements.",
            f"**Step 2 — Upskill:** Focus on: {', '.join(required[:3])}.",
            "**Step 3 — Build Proof:** Create 1-2 portfolio projects or take on cross-functional projects at your current job.",
            f"**Step 4 — Network:** Connect with {target_role}s on LinkedIn, join communities, attend meetups.",
            "**Step 5 — Apply Strategically:** Target companies open to career switchers; highlight transferable skills in your resume.",
        ]
        for s in steps:
            glass_card_open()
            st.markdown(s)
            glass_card_close()


# ================= PROMOTION READINESS SCORE =================
def page_promotion_readiness(user):
    hero("Promotion Readiness Score", "Find out how ready you are for your next promotion.", "🚀")
    with st.form("promo_form"):
        years_exp = st.slider("Years in current role", 0, 15, 2)
        performance = st.select_slider("Recent performance rating", ["Below Expectations", "Meets Expectations", "Exceeds Expectations", "Outstanding"])
        leadership = st.checkbox("I have led a project or mentored teammates")
        cert = st.checkbox("I've completed relevant certifications recently")
        visibility = st.slider("Visibility with leadership (1-10)", 1, 10, 5)
        submitted = st.form_submit_button("🎯 Calculate Readiness", type="primary")

    if submitted:
        score = 0
        score += min(25, years_exp * 5)
        perf_map = {"Below Expectations": 0, "Meets Expectations": 15, "Exceeds Expectations": 25, "Outstanding": 30}
        score += perf_map[performance]
        score += 15 if leadership else 0
        score += 10 if cert else 0
        score += visibility * 2

        score = min(100, score)
        st.plotly_chart(gauge_chart(score, "Promotion Readiness"), use_container_width=True)

        if score >= 75:
            st.success("🌟 You're highly ready! Consider scheduling a conversation with your manager about promotion.")
        elif score >= 50:
            st.warning("👍 You're on the right track. Focus on leadership visibility and certifications.")
        else:
            st.info("💡 Build more experience, take initiative on projects, and seek feedback regularly.")

        run_query("INSERT INTO assessments (user_id, assessment_type, answers, result, score, created_at) VALUES (?,?,?,?,?,?)",
                   (user["id"], "Promotion Readiness", performance, "", score, now()))


# ================= SALARY BENCHMARK =================
SALARY_BENCHMARKS = {
    # role: {experience_band: (min_lpa, max_lpa)}
    "Software Engineer": {"0-2 yrs": (6, 12), "3-5 yrs": (12, 22), "6-10 yrs": (22, 40), "10+ yrs": (35, 65)},
    "Data Scientist": {"0-2 yrs": (8, 15), "3-5 yrs": (15, 28), "6-10 yrs": (28, 45), "10+ yrs": (40, 70)},
    "Cloud Architect": {"0-2 yrs": (10, 18), "3-5 yrs": (18, 30), "6-10 yrs": (30, 50), "10+ yrs": (45, 75)},
    "Product Manager": {"0-2 yrs": (10, 16), "3-5 yrs": (16, 28), "6-10 yrs": (28, 45), "10+ yrs": (40, 70)},
    "Cybersecurity Analyst": {"0-2 yrs": (7, 13), "3-5 yrs": (13, 22), "6-10 yrs": (22, 38), "10+ yrs": (35, 55)},
    "Marketing Manager": {"0-2 yrs": (5, 9), "3-5 yrs": (9, 16), "6-10 yrs": (16, 28), "10+ yrs": (25, 45)},
    "Financial Analyst": {"0-2 yrs": (5, 9), "3-5 yrs": (9, 16), "6-10 yrs": (16, 28), "10+ yrs": (25, 45)},
    "HR Manager": {"0-2 yrs": (5, 8), "3-5 yrs": (8, 14), "6-10 yrs": (14, 24), "10+ yrs": (22, 38)},
}


def _experience_band(years):
    if years <= 2:
        return "0-2 yrs"
    elif years <= 5:
        return "3-5 yrs"
    elif years <= 10:
        return "6-10 yrs"
    return "10+ yrs"


def page_salary_benchmark(user):
    hero("Salary Benchmark", "See how your compensation compares to the market.", "💰")
    extra = get_profile_extra(user)

    c1, c2 = st.columns(2)
    role = c1.selectbox("Your Role", list(SALARY_BENCHMARKS.keys()),
                         index=list(SALARY_BENCHMARKS.keys()).index(extra.get("designation")) if extra.get("designation") in SALARY_BENCHMARKS else 0)
    experience = c2.number_input("Years of Experience", min_value=0.0, max_value=40.0, step=0.5,
                                  value=float(extra.get("experience_years", 2) or 2))

    current_ctc_default = 0.0
    try:
        current_ctc_default = float(str(extra.get("current_ctc", "0")).replace("₹", "").replace("LPA", "").strip() or 0)
    except ValueError:
        current_ctc_default = 0.0
    current_ctc = st.number_input("Your Current CTC (₹ LPA)", min_value=0.0, step=0.5, value=current_ctc_default)

    if st.button("📊 Compare to Market", type="primary"):
        band = _experience_band(experience)
        low, high = SALARY_BENCHMARKS[role][band]
        mid = round((low + high) / 2, 1)

        st.plotly_chart(bar_chart(["Market Low", "Your CTC", "Market Midpoint", "Market High"],
                                   [low, current_ctc, mid, high], f"{role} — {band} Salary Benchmark (₹ LPA)"),
                         use_container_width=True)

        if current_ctc < low:
            st.warning(f"💡 Your CTC (₹{current_ctc} LPA) is below the typical market range (₹{low}-{high} LPA) for a {role} with {band} experience. Consider negotiating your next offer or exploring a role change.")
        elif current_ctc > high:
            st.success(f"🌟 You're being compensated above the typical market range (₹{low}-{high} LPA) — great position!")
        else:
            st.info(f"👍 Your CTC (₹{current_ctc} LPA) falls within the typical market range (₹{low}-{high} LPA) for a {role} with {band} experience.")

        run_query("INSERT INTO assessments (user_id, assessment_type, answers, result, score, created_at) VALUES (?,?,?,?,?,?)",
                   (user["id"], "Salary Benchmark", f"{role}, {band}, current: {current_ctc}", f"Market: {low}-{high} LPA", mid, now()))


# ================= NETWORKING & VISIBILITY BUILDER =================
NETWORKING_PLATFORMS = {
    "LinkedIn Events": "https://www.linkedin.com/events/",
    "Meetup": "https://www.meetup.com/find/?keywords={q}",
    "Eventbrite": "https://www.eventbrite.com/d/online/{q}/",
}


def page_networking_builder(user):
    hero("Networking & Visibility Builder", "Grow your professional network strategically.", "🤝")
    extra = get_profile_extra(user)
    industry = extra.get("industry", "Technology") or "Technology"

    section_title("💡 Weekly Networking Checklist")
    checklist = [
        "Comment thoughtfully on 3 posts from people in your target role/industry",
        "Send 2 personalized connection requests with a short note",
        "Share one piece of content (article, insight, or project update)",
        "Reach out to 1 former colleague or classmate to reconnect",
        "Attend or watch one industry webinar/event",
    ]
    completed = 0
    for i, item in enumerate(checklist):
        if st.checkbox(item, key=f"network_{i}"):
            completed += 1
    st.progress(completed / len(checklist))
    st.caption(f"{completed}/{len(checklist)} networking actions completed this week")

    section_title(f"🔗 Find Events & Communities in {industry}")
    q = quote_plus(industry)
    cols = st.columns(len(NETWORKING_PLATFORMS))
    for col, (name, url_template) in zip(cols, NETWORKING_PLATFORMS.items()):
        with col:
            st.link_button(f"{name} →", url_template.format(q=q), use_container_width=True)


# ================= AI CAREER COACH =================
def page_ai_career_coach(user):
    hero("AI Career Coach", "Get personalized long-term career strategy advice.", "🧭")
    st.caption(f"AI Mode: {'🟢 Live API' if ai_status() != 'rule_based' else '🟡 Offline Smart Assistant'}")

    goal = st.text_area("Describe your career goal or challenge",
                         placeholder="e.g. I want to move from an individual contributor role to a management position within 2 years...")
    if st.button("🧭 Get Coaching Advice", type="primary"):
        if not goal.strip():
            st.warning("Please describe your goal first.")
        else:
            with st.spinner("Your AI coach is thinking..."):
                if ai_status() != "rule_based":
                    advice = ai_generate(f"As a career coach, give actionable advice for this goal: {goal}")
                    st.markdown(advice)
                else:
                    st.markdown(f"""
**🎯 Coaching Insights for your goal:**

*"{goal}"*

1. **Clarify the destination** — Write down the exact title/role and the 3 measurable outcomes that define success.
2. **Audit the gap** — Use the Skill Gap Analysis and Skill Assessment modules to quantify what's missing.
3. **Create visibility** — Volunteer for cross-functional projects that showcase the capabilities your goal requires.
4. **Find a mentor/sponsor** — Someone already in that role can fast-track your learning curve.
5. **Review quarterly** — Revisit this goal every 3 months and adjust your roadmap based on progress.

💡 *Tip: Small, consistent actions compound — track them in your Goal Tracker!*
                    """)
            run_query("INSERT INTO chat_history (user_id, role, message, created_at) VALUES (?,?,?,?)",
                       (user["id"], "user", f"[Career Coach] {goal}", now()))
