"""
TalentSphere Elevate - Common Modules
Shared across High School, College, and Working Professional dashboards:
Profile, Notifications, AI Chatbot, Learning Dashboard, Progress Tracking,
Personalized Recommendations, Certificates.
"""

import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

from database.db import run_query, now, get_profile_extra, save_profile_extra
from utils.ui import hero, section_title, kpi_card, glass_card_open, glass_card_close, badge
from utils.charts import donut_chart, line_chart, progress_area_chart, bar_chart
from utils.ai_engine import ai_chat_reply, rule_based_chat_reply, ai_status, recommend_careers, weekly_progress_report
from utils.pdf_generator import generate_certificate, generate_report_pdf, generate_verification_report


# ================= PROFILE =================
def page_profile(user):
    hero("My Profile", f"Manage your personal information, {user['fullname'].split()[0]}!", "🧑‍💼")
    extra = get_profile_extra(user)

    col1, col2 = st.columns([1, 2])
    with col1:
        glass_card_open()
        st.markdown(f"<div style='text-align:center;font-size:4rem'>{user.get('avatar','🧑‍🎓')}</div>", unsafe_allow_html=True)
        avatars = ["🧑‍🎓", "👩‍💻", "🧑‍💻", "👨‍🎓", "🧑‍🔬", "👩‍🔬", "🧑‍💼", "👩‍💼"]
        new_avatar = st.selectbox("Choose Avatar", avatars, index=avatars.index(user.get("avatar", "🧑‍🎓")) if user.get("avatar") in avatars else 0)
        if new_avatar != user.get("avatar"):
            run_query("UPDATE users SET avatar=? WHERE id=?", (new_avatar, user["id"]))
            st.session_state.user["avatar"] = new_avatar
            st.rerun()
        st.markdown(badge(user["category"], "purple"), unsafe_allow_html=True)
        glass_card_close()

    with col2:
        glass_card_open()
        section_title("Account Details")
        with st.form("profile_form"):
            fullname = st.text_input("Full Name", value=user["fullname"])
            mobile = st.text_input("Mobile Number", value=user["mobile"])
            st.text_input("Email (read-only)", value=user["email"], disabled=True)
            st.text_input("Username (read-only)", value=user["username"], disabled=True)
            submitted = st.form_submit_button("💾 Save Changes")
            if submitted:
                run_query("UPDATE users SET fullname=?, mobile=? WHERE id=?", (fullname, mobile, user["id"]))
                st.session_state.user["fullname"] = fullname
                st.session_state.user["mobile"] = mobile
                st.success("Profile updated successfully!")
        glass_card_close()

    # ---------------- Category-specific extended profile ----------------
    section_title(f"{user['category']} Details")
    glass_card_open()

    if user["category"] == "High School Student":
        with st.form("extra_profile_hs"):
            c1, c2 = st.columns(2)
            school_name = c1.text_input("School Name", value=extra.get("school_name", ""))
            board = c2.selectbox("Board", ["CBSE", "ICSE", "State Board", "IB", "IGCSE", "Other"],
                                  index=(["CBSE", "ICSE", "State Board", "IB", "IGCSE", "Other"].index(extra.get("board")) if extra.get("board") in ["CBSE", "ICSE", "State Board", "IB", "IGCSE", "Other"] else 0))
            c3, c4 = st.columns(2)
            study_year = c3.selectbox("Current Study Year", ["Grade 9", "Grade 10", "Grade 11", "Grade 12"],
                                       index=(["Grade 9", "Grade 10", "Grade 11", "Grade 12"].index(extra.get("study_year")) if extra.get("study_year") in ["Grade 9", "Grade 10", "Grade 11", "Grade 12"] else 0))
            city = c4.text_input("City", value=extra.get("city", ""))
            favorite_subjects = st.text_input("Favorite Subjects (comma separated)", value=extra.get("favorite_subjects", ""))
            interest_area = st.selectbox("Career Interest Area", ["Not Sure Yet", "Science & Engineering", "Medicine & Healthcare",
                                          "Commerce & Finance", "Arts & Design", "Humanities & Civil Services", "Sports"],
                                          index=0 if not extra.get("interest_area") else
                                          (["Not Sure Yet", "Science & Engineering", "Medicine & Healthcare", "Commerce & Finance",
                                            "Arts & Design", "Humanities & Civil Services", "Sports"].index(extra.get("interest_area"))
                                           if extra.get("interest_area") in ["Not Sure Yet", "Science & Engineering", "Medicine & Healthcare",
                                          "Commerce & Finance", "Arts & Design", "Humanities & Civil Services", "Sports"] else 0))
            target_exam = st.text_input("Target Exam (optional)", value=extra.get("target_exam", ""), placeholder="e.g. JEE, NEET, Olympiads")
            if st.form_submit_button("💾 Save School Details"):
                save_profile_extra(user["id"], {
                    "school_name": school_name, "board": board, "study_year": study_year, "city": city,
                    "favorite_subjects": favorite_subjects, "interest_area": interest_area, "target_exam": target_exam,
                })
                st.success("School details saved! Your Learning Dashboard will now show more relevant courses.")
                st.rerun()

    elif user["category"] == "College Student":
        with st.form("extra_profile_college"):
            c1, c2 = st.columns(2)
            college_name = c1.text_input("College / University Name", value=extra.get("college_name", ""))
            branch = c2.text_input("Branch / Major", value=extra.get("branch", ""), placeholder="e.g. Computer Science")
            c3, c4 = st.columns(2)
            specialization = c3.text_input("Specialization", value=extra.get("specialization", ""), placeholder="e.g. AI/ML, Cybersecurity")
            year_of_study = c4.selectbox("Year of Study", ["1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year", "Graduated"],
                                          index=(["1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year", "Graduated"].index(extra.get("year_of_study")) if extra.get("year_of_study") in ["1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year", "Graduated"] else 0))
            c5, c6 = st.columns(2)
            cgpa = c5.text_input("CGPA / Percentage", value=extra.get("cgpa", ""))
            grad_year = c6.text_input("Expected Graduation Year", value=extra.get("grad_year", ""))
            github_link = st.text_input("GitHub Profile URL", value=extra.get("github_link", ""), placeholder="https://github.com/username")
            linkedin_link = st.text_input("LinkedIn Profile URL", value=extra.get("linkedin_link", ""), placeholder="https://linkedin.com/in/username")
            portfolio_link = st.text_input("Portfolio Website (optional)", value=extra.get("portfolio_link", ""))
            target_role = st.text_input("Target Job Role", value=extra.get("target_role", ""), placeholder="e.g. Software Engineer, Data Scientist")
            if st.form_submit_button("💾 Save College Details"):
                save_profile_extra(user["id"], {
                    "college_name": college_name, "branch": branch, "specialization": specialization,
                    "year_of_study": year_of_study, "cgpa": cgpa, "grad_year": grad_year,
                    "github_link": github_link, "linkedin_link": linkedin_link,
                    "portfolio_link": portfolio_link, "target_role": target_role,
                })
                st.success("College details saved!")
                st.rerun()

    elif user["category"] == "Working Professional":
        with st.form("extra_profile_prof"):
            c1, c2 = st.columns(2)
            company_name = c1.text_input("Current Company", value=extra.get("company_name", ""))
            designation = c2.text_input("Role / Designation", value=extra.get("designation", ""))
            c3, c4 = st.columns(2)
            industry = c3.text_input("Industry", value=extra.get("industry", ""), placeholder="e.g. Technology, Finance")
            experience_years = c4.number_input("Years of Experience", min_value=0.0, max_value=50.0, step=0.5,
                                                 value=float(extra.get("experience_years", 0) or 0))
            c5, c6 = st.columns(2)
            current_ctc = c5.text_input("Current Salary / CTC (₹ LPA)", value=extra.get("current_ctc", ""))
            work_location = c6.text_input("Work Location", value=extra.get("work_location", ""))
            linkedin_link = st.text_input("LinkedIn Profile URL", value=extra.get("linkedin_link", ""))
            key_skills = st.text_area("Key Skills (comma separated)", value=extra.get("key_skills", ""))
            career_goal = st.text_input("Career Goal", value=extra.get("career_goal", ""), placeholder="e.g. Move into management, switch to Data Science")
            if st.form_submit_button("💾 Save Professional Details"):
                save_profile_extra(user["id"], {
                    "company_name": company_name, "designation": designation, "industry": industry,
                    "experience_years": experience_years, "current_ctc": current_ctc,
                    "work_location": work_location, "linkedin_link": linkedin_link,
                    "key_skills": key_skills, "career_goal": career_goal,
                })
                st.success("Professional details saved!")
                st.rerun()

    glass_card_close()

    section_title("Change Password")
    glass_card_open()
    from auth.auth_utils import verify_password, hash_password
    with st.form("pwd_form"):
        c1, c2 = st.columns(2)
        old_pwd = c1.text_input("Current Password", type="password")
        new_pwd = c2.text_input("New Password", type="password")
        if st.form_submit_button("🔒 Update Password"):
            if not verify_password(old_pwd, user["password"]):
                st.error("Current password is incorrect.")
            elif len(new_pwd) < 6:
                st.error("New password must be at least 6 characters.")
            else:
                run_query("UPDATE users SET password=? WHERE id=?", (hash_password(new_pwd), user["id"]))
                st.success("Password updated successfully!")
    glass_card_close()

    # ---------------- Profile Verification Report ----------------
    section_title("📑 Profile Verification Report")
    st.caption("Generate a comprehensive PDF snapshot of your profile, assessments, and recommendations — useful to verify your progress at a later date (e.g. for mentors, parents, or your own records).")
    if st.button("📄 Generate Verification Report", type="primary"):
        extra = get_profile_extra(user)
        assessments = run_query("SELECT * FROM assessments WHERE user_id=? ORDER BY created_at DESC LIMIT 10", (user["id"],), fetch=True)
        quizzes = run_query("SELECT * FROM quiz_results WHERE user_id=? ORDER BY created_at DESC LIMIT 10", (user["id"],), fetch=True)
        progress_rows = run_query("SELECT * FROM learning_progress WHERE user_id=?", (user["id"],), fetch=True)
        certs = run_query("SELECT * FROM certificates WHERE user_id=?", (user["id"],), fetch=True)
        goals = run_query("SELECT * FROM goals WHERE user_id=?", (user["id"],), fetch=True)

        verification_code = f"TSE-VER-{uuid.uuid4().hex[:8].upper()}"
        sections = {
            "Assessment History": [f"{a['assessment_type']} — Result: {a['result']} (Score: {a['score']}) on {a['created_at'][:10]}" for a in assessments] or ["No assessments completed yet."],
            "Quiz Results": [f"{q['quiz_topic']} — {q['score']}/{q['total']} on {q['created_at'][:10]}" for q in quizzes] or ["No quizzes attempted yet."],
            "Learning Progress": [f"{p['module']} — {p['task']} — {p['status']} ({p['progress_pct']}%)" for p in progress_rows] or ["No learning modules started yet."],
            "Goals": [f"{g['goal_text']} — {g['status']} (Target: {g['target_date'] or 'N/A'})" for g in goals] or ["No goals set yet."],
            "Certificates Earned": [f"{c['title']} — Issued {c['issued_on'][:10]} — Code: {c['cert_code']}" for c in certs] or ["No certificates earned yet."],
        }
        pdf_bytes = generate_verification_report(user, extra, sections, verification_code)
        run_query("INSERT INTO reports (user_id, report_type, content, created_at) VALUES (?,?,?,?)",
                   (user["id"], "Profile Verification", verification_code, now()))
        st.success(f"Report generated! Verification Code: {verification_code}")
        st.download_button("⬇️ Download Verification Report PDF", data=pdf_bytes,
                            file_name=f"profile_verification_{user['username']}.pdf", mime="application/pdf")


# ================= NOTIFICATIONS =================
def page_notifications(user):
    hero("Notifications", "Stay updated with your latest alerts and announcements.", "🔔")
    notifs = run_query("SELECT * FROM notifications WHERE user_id IS NULL OR user_id=? ORDER BY created_at DESC",
                        (user["id"],), fetch=True)

    unread = [n for n in notifs if not n["is_read"]]
    if unread:
        if st.button(f"✅ Mark all {len(unread)} as read"):
            run_query("UPDATE notifications SET is_read=1 WHERE user_id=? OR user_id IS NULL", (user["id"],))
            st.rerun()

    if not notifs:
        st.info("No notifications yet. Check back soon!")
    for n in notifs:
        icon = "🔵" if not n["is_read"] else "⚪"
        glass_card_open()
        st.markdown(f"**{icon} {n['title']}**")
        st.caption(n["message"])
        st.caption(f"🕒 {n['created_at'][:16].replace('T', ' ')}")
        glass_card_close()


# ================= AI CHATBOT =================
def page_chatbot(user):
    hero("AI Career Mentor", "Ask me anything about careers, skills, resumes & interviews!", "🤖")
    mode = ai_status()
    st.caption(f"AI Mode: {'🟢 Live API' if mode != 'rule_based' else '🟡 Offline Smart Assistant (add API key for live AI)'}")

    if "chat_log" not in st.session_state:
        history = run_query("SELECT * FROM chat_history WHERE user_id=? ORDER BY id ASC LIMIT 50", (user["id"],), fetch=True)
        st.session_state.chat_log = [(h["role"], h["message"]) for h in history] or [
            ("ai", f"Hi {user['fullname'].split()[0]}! 👋 I'm your AI Career Mentor. Ask me about careers, resumes, interviews or skills!")
        ]

    chat_container = st.container(height=420)
    with chat_container:
        for role, msg in st.session_state.chat_log:
            css_class = "chat-bubble-user" if role == "user" else "chat-bubble-ai"
            align = "right" if role == "user" else "left"
            st.markdown(f'<div style="text-align:{align}"><div class="{css_class}">{msg}</div></div>', unsafe_allow_html=True)

    user_msg = st.chat_input("Type your question here...")
    if user_msg:
        st.session_state.chat_log.append(("user", user_msg))
        run_query("INSERT INTO chat_history (user_id, role, message, created_at) VALUES (?,?,?,?)",
                   (user["id"], "user", user_msg, now()))
        reply = ai_chat_reply(user_msg)
        st.session_state.chat_log.append(("ai", reply))
        run_query("INSERT INTO chat_history (user_id, role, message, created_at) VALUES (?,?,?,?)",
                   (user["id"], "ai", reply, now()))
        st.rerun()

    st.markdown("**💡 Quick prompts:**")
    cols = st.columns(4)
    quick = ["How do I improve my resume?", "Suggest a career for me", "Tips for interviews", "What skills should I learn?"]
    for c, q in zip(cols, quick):
        if c.button(q, use_container_width=True):
            st.session_state.chat_log.append(("user", q))
            reply = ai_chat_reply(q)
            st.session_state.chat_log.append(("ai", reply))
            run_query("INSERT INTO chat_history (user_id, role, message, created_at) VALUES (?,?,?,?)",
                       (user["id"], "user", q, now()))
            run_query("INSERT INTO chat_history (user_id, role, message, created_at) VALUES (?,?,?,?)",
                       (user["id"], "ai", reply, now()))
            st.rerun()


# ================= LEARNING DASHBOARD =================
def page_learning_dashboard(user):
    hero("Learning Dashboard", "Your personalized courses and learning resources.", "📚")
    extra = get_profile_extra(user)
    courses = run_query("SELECT * FROM courses WHERE category=? OR category='All' ORDER BY created_at DESC",
                         (user["category"],), fetch=True)

    # Build a relevance keyword set from the user's own profile selections
    keywords = []
    if user["category"] == "High School Student":
        keywords += [extra.get("interest_area", "")] + extra.get("favorite_subjects", "").split(",") + [extra.get("target_exam", "")]
    elif user["category"] == "College Student":
        keywords += [extra.get("branch", ""), extra.get("specialization", ""), extra.get("target_role", "")]
    elif user["category"] == "Working Professional":
        keywords += extra.get("key_skills", "").split(",") + [extra.get("career_goal", ""), extra.get("industry", "")]
    keywords = [k.strip().lower() for k in keywords if k and k.strip()]

    def is_relevant(course):
        text = f"{course['title']} {course['description']}".lower()
        return any(k in text for k in keywords) if keywords else False

    courses_sorted = sorted(courses, key=lambda c: not is_relevant(c))

    if keywords:
        st.caption(f"✨ Ranked using your profile selections: {', '.join(keywords[:5])}")
    else:
        st.info("💡 Tip: Fill in your profile details to get courses tailored to your interests!")

    section_title(f"Recommended Courses for {user['category']}s")
    if not courses_sorted:
        st.info("No courses available yet.")
    for i in range(0, len(courses_sorted), 3):
        cols = st.columns(3)
        for col, course in zip(cols, courses_sorted[i:i + 3]):
            with col:
                glass_card_open()
                if is_relevant(course):
                    st.markdown(badge("✨ Matched to your profile", "purple"), unsafe_allow_html=True)
                st.markdown(f"**📘 {course['title']}**")
                st.caption(course["description"])
                st.markdown(badge(course["level"], "info") + badge(course["duration"], "purple"), unsafe_allow_html=True)
                if st.button("Start Learning", key=f"course_{course['id']}", use_container_width=True):
                    existing = run_query("SELECT * FROM learning_progress WHERE user_id=? AND module=?",
                                          (user["id"], course["title"]), fetchone=True)
                    if not existing:
                        run_query("""INSERT INTO learning_progress (user_id, module, task, status, progress_pct, updated_at)
                                     VALUES (?,?,?,?,?,?)""",
                                  (user["id"], course["title"], "Course Enrollment", "In Progress", 10, now()))
                        st.success(f"Enrolled in {course['title']}!")
                    else:
                        st.info("You're already enrolled in this course.")
                glass_card_close()


# ================= PROGRESS TRACKING =================
def page_progress_tracking(user):
    hero("Progress Tracker", "Visualize your learning journey and achievements.", "📈")
    progress_rows = run_query("SELECT * FROM learning_progress WHERE user_id=?", (user["id"],), fetch=True)
    quiz_rows = run_query("SELECT * FROM quiz_results WHERE user_id=?", (user["id"],), fetch=True)
    coding_rows = run_query("SELECT * FROM coding_practice WHERE user_id=?", (user["id"],), fetch=True)

    total_tasks = len(progress_rows)
    done_tasks = len([p for p in progress_rows if p["status"] == "Completed"])
    avg_progress = round(sum(p["progress_pct"] for p in progress_rows) / total_tasks, 1) if total_tasks else 0

    c1, c2, c3, c4 = st.columns(4)
    kpi_card("📘", total_tasks, "Modules Started", c1)
    kpi_card("✅", done_tasks, "Completed", c2)
    kpi_card("🧠", len(quiz_rows), "Quizzes Taken", c3)
    kpi_card("💻", len(coding_rows), "Coding Problems", c4)

    col1, col2 = st.columns(2)
    with col1:
        section_title("Overall Progress")
        st.plotly_chart(donut_chart(["Completed", "In Progress", "Pending"],
                                     [done_tasks, total_tasks - done_tasks, max(0, 5 - total_tasks)],
                                     "Task Status"), use_container_width=True)
    with col2:
        section_title("Progress Trend")
        if progress_rows:
            df = pd.DataFrame(progress_rows)
            df["updated_at"] = pd.to_datetime(df["updated_at"])
            df = df.sort_values("updated_at")
            st.plotly_chart(progress_area_chart(list(range(1, len(df) + 1)), df["progress_pct"].tolist(),
                                                  "Progress Over Activities"), use_container_width=True)
        else:
            st.info("Start learning modules to see your progress trend!")

    section_title("Detailed Progress Log")
    if progress_rows:
        df = pd.DataFrame(progress_rows)[["module", "task", "status", "progress_pct", "updated_at"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No progress recorded yet. Explore the Learning Dashboard to get started!")

    st.markdown("---")
    if st.button("📄 Generate Weekly Progress Report (PDF)"):
        stats = {"tasks_done": done_tasks, "tasks_total": max(total_tasks, 1),
                 "quizzes": len(quiz_rows), "coding_solved": len(coding_rows), "progress_pct": avg_progress}
        report_text = weekly_progress_report(user["fullname"], stats)
        sections = {"Summary": report_text.split("\n")}
        pdf_bytes = generate_report_pdf("Weekly Progress Report", user["fullname"], sections)
        run_query("INSERT INTO reports (user_id, report_type, content, created_at) VALUES (?,?,?,?)",
                   (user["id"], "Weekly Progress", report_text, now()))
        st.download_button("⬇️ Download Report PDF", data=pdf_bytes,
                            file_name=f"progress_report_{user['username']}.pdf", mime="application/pdf")


# ================= PERSONALIZED RECOMMENDATIONS =================
def page_recommendations(user):
    hero("Personalized Recommendations", "AI-curated suggestions based on your profile & activity.", "✨")
    section_title("Tell us what interests you")
    interest_text = st.text_area("Describe your interests, hobbies, or subjects you enjoy",
                                  placeholder="e.g. I enjoy solving math problems, building things, and working with computers...")
    if st.button("🔮 Get AI Recommendations", type="primary"):
        if not interest_text.strip():
            st.warning("Please describe your interests first.")
        else:
            with st.spinner("Analyzing your interests..."):
                results = recommend_careers(interest_text, user["category"])
            if isinstance(results, str):
                st.markdown(results)
            else:
                for r in results:
                    glass_card_open()
                    st.markdown(f"**🎯 {r['career']}**")
                    st.progress(r["match"] / 100)
                    st.caption(f"Match Score: {r['match']}%")
                    glass_card_close()
                run_query("INSERT INTO assessments (user_id, assessment_type, answers, result, score, created_at) VALUES (?,?,?,?,?,?)",
                           (user["id"], "Recommendation", interest_text, str(results), 0, now()))


# ================= CERTIFICATES =================
def page_certificates(user):
    hero("My Certificates", "Download your earned certificates as PDF.", "🏆")

    completed = run_query("SELECT * FROM learning_progress WHERE user_id=? AND status='Completed'", (user["id"],), fetch=True)
    existing_certs = run_query("SELECT * FROM certificates WHERE user_id=?", (user["id"],), fetch=True)
    existing_titles = {c["title"] for c in existing_certs}

    section_title("Available to Claim")
    claimable = [c for c in completed if c["module"] not in existing_titles]
    if not claimable:
        st.info("Complete learning modules to unlock certificates!")
    for c in claimable:
        glass_card_open()
        st.markdown(f"**🎓 {c['module']}**")
        if st.button(f"Claim Certificate", key=f"claim_{c['id']}"):
            cert_code = f"TSE-{uuid.uuid4().hex[:8].upper()}"
            run_query("INSERT INTO certificates (user_id, title, issued_on, cert_code) VALUES (?,?,?,?)",
                       (user["id"], c["module"], now(), cert_code))
            st.success("Certificate claimed! Scroll down to download.")
            st.rerun()
        glass_card_close()

    section_title("My Certificates")
    certs = run_query("SELECT * FROM certificates WHERE user_id=? ORDER BY issued_on DESC", (user["id"],), fetch=True)
    if not certs:
        st.info("No certificates earned yet.")
    for c in certs:
        col1, col2 = st.columns([3, 1])
        with col1:
            glass_card_open()
            st.markdown(f"**🏅 {c['title']}**")
            st.caption(f"Issued: {c['issued_on'][:10]}  |  Code: {c['cert_code']}")
            glass_card_close()
        with col2:
            pdf_bytes = generate_certificate(user["fullname"], c["title"], c["cert_code"], c["issued_on"][:10])
            st.download_button("⬇️ PDF", data=pdf_bytes, file_name=f"certificate_{c['cert_code']}.pdf",
                                mime="application/pdf", key=f"dl_{c['id']}", use_container_width=True)


# ================= GOAL TRACKER (used by High School but generic) =================
def page_goal_tracker(user):
    hero("Goal Tracker", "Set goals and track your journey to achieving them.", "🎯")
    with st.form("goal_form"):
        c1, c2 = st.columns([3, 1])
        goal_text = c1.text_input("New Goal", placeholder="e.g. Complete Python basics course")
        target_date = c2.date_input("Target Date")
        if st.form_submit_button("➕ Add Goal") and goal_text.strip():
            run_query("INSERT INTO goals (user_id, goal_text, target_date, created_at) VALUES (?,?,?,?)",
                       (user["id"], goal_text, str(target_date), now()))
            st.success("Goal added!")
            st.rerun()

    goals = run_query("SELECT * FROM goals WHERE user_id=? ORDER BY created_at DESC", (user["id"],), fetch=True)
    section_title("Your Goals")
    if not goals:
        st.info("No goals set yet. Add one above!")
    for g in goals:
        glass_card_open()
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.markdown(f"**{g['goal_text']}**")
        c1.caption(f"Target: {g['target_date']}")
        status_color = "success" if g["status"] == "Completed" else "warning"
        c2.markdown(badge(g["status"], status_color), unsafe_allow_html=True)
        if g["status"] != "Completed":
            if c3.button("Mark Done", key=f"goal_{g['id']}"):
                run_query("UPDATE goals SET status='Completed' WHERE id=?", (g["id"],))
                st.rerun()
        glass_card_close()
