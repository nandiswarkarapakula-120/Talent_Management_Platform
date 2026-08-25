"""
TalentSphere Elevate - Admin Portal
Manage Users, Manage Courses, Add Career Paths, Upload Learning Materials,
Create Quizzes, View Analytics, Send Notifications, Generate Reports.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from database.db import run_query, now
from utils.ui import hero, section_title, kpi_card, glass_card_open, glass_card_close, badge
from utils.charts import donut_chart, bar_chart, line_chart
from utils.pdf_generator import generate_report_pdf


def log_admin_action(admin_username, action, details=""):
    run_query("INSERT INTO admin_actions (admin_username, action, details, created_at) VALUES (?,?,?,?)",
               (admin_username, action, details, now()))


# ================= ADMIN OVERVIEW =================
def page_admin_overview(admin):
    hero("Admin Dashboard", f"Welcome back, {admin['fullname']}! Here's your platform overview.", "🛡️")

    total_users = run_query("SELECT COUNT(*) c FROM users", fetchone=True)["c"]
    active_users = run_query("SELECT COUNT(*) c FROM users WHERE is_active=1", fetchone=True)["c"]
    total_courses = run_query("SELECT COUNT(*) c FROM courses", fetchone=True)["c"]
    total_certs = run_query("SELECT COUNT(*) c FROM certificates", fetchone=True)["c"]

    c1, c2, c3, c4 = st.columns(4)
    kpi_card("👥", total_users, "Total Users", c1)
    kpi_card("✅", active_users, "Active Users", c2)
    kpi_card("📚", total_courses, "Courses", c3)
    kpi_card("🏆", total_certs, "Certificates Issued", c4)

    col1, col2 = st.columns(2)
    with col1:
        section_title("Users by Category")
        rows = run_query("SELECT category, COUNT(*) c FROM users GROUP BY category", fetch=True)
        if rows:
            st.plotly_chart(donut_chart([r["category"] for r in rows], [r["c"] for r in rows], "User Distribution"),
                             use_container_width=True)
        else:
            st.info("No users yet.")
    with col2:
        section_title("Signups Over Time")
        rows = run_query("SELECT substr(created_at,1,10) d, COUNT(*) c FROM users GROUP BY d ORDER BY d", fetch=True)
        if rows:
            st.plotly_chart(line_chart([r["d"] for r in rows], [r["c"] for r in rows], "Daily Signups", "Date", "Users"),
                             use_container_width=True)
        else:
            st.info("No signup data yet.")

    section_title("Recent Admin Actions")
    actions = run_query("SELECT * FROM admin_actions ORDER BY created_at DESC LIMIT 8", fetch=True)
    if actions:
        st.dataframe(pd.DataFrame(actions)[["admin_username", "action", "details", "created_at"]],
                     use_container_width=True, hide_index=True)
    else:
        st.info("No admin actions logged yet.")


# ================= MANAGE USERS =================
def page_manage_users(admin):
    hero("Manage Users", "Add, edit, activate or deactivate user accounts.", "👥")

    users = run_query("SELECT * FROM users ORDER BY created_at DESC", fetch=True)
    search = st.text_input("🔍 Search by name, email or username")
    filtered = users
    if search:
        s = search.lower()
        filtered = [u for u in users if s in u["fullname"].lower() or s in u["email"].lower() or s in u["username"].lower()]

    category_filter = st.multiselect("Filter by category", ["High School Student", "College Student", "Working Professional"])
    if category_filter:
        filtered = [u for u in filtered if u["category"] in category_filter]

    section_title(f"All Users ({len(filtered)})")
    for u in filtered:
        glass_card_open()
        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
        with c1:
            st.markdown(f"**{u.get('avatar','🧑')} {u['fullname']}**")
            st.caption(f"{u['email']} | @{u['username']}")
        with c2:
            st.markdown(badge(u["category"], "purple"), unsafe_allow_html=True)
            st.caption(f"📱 {u['mobile']}")
        with c3:
            status_badge = badge("Active", "success") if u["is_active"] else badge("Inactive", "danger")
            st.markdown(status_badge, unsafe_allow_html=True)
            st.caption(f"Joined: {u['created_at'][:10]}")
        with c4:
            toggle_label = "🚫 Deactivate" if u["is_active"] else "✅ Activate"
            if st.button(toggle_label, key=f"toggle_{u['id']}"):
                run_query("UPDATE users SET is_active=? WHERE id=?", (0 if u["is_active"] else 1, u["id"]))
                log_admin_action(admin["username"], toggle_label, f"User: {u['username']}")
                st.rerun()
            if st.button("🗑️ Delete", key=f"del_{u['id']}"):
                run_query("DELETE FROM users WHERE id=?", (u["id"],))
                log_admin_action(admin["username"], "Deleted User", f"User: {u['username']}")
                st.rerun()
        glass_card_close()

    if not filtered:
        st.info("No users match your filters.")


# ================= MANAGE COURSES =================
def page_manage_courses(admin):
    hero("Manage Courses", "Add, edit and organize learning courses.", "📚")

    with st.expander("➕ Add New Course"):
        with st.form("add_course_form"):
            c1, c2 = st.columns(2)
            title = c1.text_input("Course Title")
            category = c2.selectbox("Category", ["All", "High School Student", "College Student", "Working Professional"])
            description = st.text_area("Description")
            c3, c4, c5 = st.columns(3)
            level = c3.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])
            duration = c4.text_input("Duration", value="4 weeks")
            resource_type = c5.selectbox("Resource Type", ["Video", "Course", "PDF", "Practice Set", "Article"])
            resource_link = st.text_input("Resource Link (URL)", value="#")
            if st.form_submit_button("💾 Add Course") and title.strip():
                run_query("""INSERT INTO courses (title, category, description, level, duration, resource_type, resource_link, created_at)
                             VALUES (?,?,?,?,?,?,?,?)""",
                          (title, category, description, level, duration, resource_type, resource_link, now()))
                log_admin_action(admin["username"], "Added Course", title)
                st.success("Course added!")
                st.rerun()

    section_title("All Courses")
    courses = run_query("SELECT * FROM courses ORDER BY created_at DESC", fetch=True)
    for c in courses:
        glass_card_open()
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**📘 {c['title']}**  {badge(c['category'],'purple')}", unsafe_allow_html=True)
            st.caption(c["description"])
            st.markdown(badge(c["level"], "info") + badge(c["duration"], "warning") + badge(c["resource_type"], "success"), unsafe_allow_html=True)
        with col2:
            if st.button("🗑️ Delete", key=f"delcourse_{c['id']}"):
                run_query("DELETE FROM courses WHERE id=?", (c["id"],))
                log_admin_action(admin["username"], "Deleted Course", c["title"])
                st.rerun()
        glass_card_close()


# ================= ADD CAREER PATHS =================
def page_manage_career_paths(admin):
    hero("Manage Career Paths", "Add and curate career path information.", "🧭")

    with st.expander("➕ Add New Career Path"):
        with st.form("add_career_form"):
            c1, c2 = st.columns(2)
            title = c1.text_input("Career Title")
            category = c2.selectbox("Relevant For", ["High School Student", "College Student", "Working Professional"])
            description = st.text_area("Description")
            skills = st.text_input("Required Skills (comma separated)")
            c3, c4 = st.columns(2)
            salary = c3.text_input("Average Salary", value="₹5-15 LPA")
            growth = c4.selectbox("Growth Outlook", ["Low", "Moderate", "High", "Very High"])
            if st.form_submit_button("💾 Add Career Path") and title.strip():
                run_query("""INSERT INTO career_paths (title, category, description, required_skills, avg_salary, growth_outlook, created_at)
                             VALUES (?,?,?,?,?,?,?)""",
                          (title, category, description, skills, salary, growth, now()))
                log_admin_action(admin["username"], "Added Career Path", title)
                st.success("Career path added!")
                st.rerun()

    section_title("All Career Paths")
    paths = run_query("SELECT * FROM career_paths ORDER BY created_at DESC", fetch=True)
    for p in paths:
        glass_card_open()
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**🎓 {p['title']}** {badge(p['category'],'purple')}", unsafe_allow_html=True)
            st.caption(p["description"])
            st.markdown(badge(p["avg_salary"], "success") + badge(p["growth_outlook"], "info"), unsafe_allow_html=True)
        with col2:
            if st.button("🗑️ Delete", key=f"delpath_{p['id']}"):
                run_query("DELETE FROM career_paths WHERE id=?", (p["id"],))
                log_admin_action(admin["username"], "Deleted Career Path", p["title"])
                st.rerun()
        glass_card_close()


# ================= UPLOAD LEARNING MATERIALS =================
def page_upload_materials(admin):
    hero("Upload Learning Materials", "Add PDFs, videos or resource links for learners.", "📤")
    with st.form("upload_form"):
        title = st.text_input("Material Title")
        category = st.selectbox("Target Category", ["All", "High School Student", "College Student", "Working Professional"])
        material_type = st.selectbox("Type", ["PDF", "Video", "Link", "Document"])
        uploaded_file = st.file_uploader("Upload File (optional)", type=["pdf", "mp4", "docx", "pptx"])
        link = st.text_input("Or paste a resource link")
        description = st.text_area("Description")
        if st.form_submit_button("📤 Upload Material") and title.strip():
            resource_link = link if link else (uploaded_file.name if uploaded_file else "#")
            run_query("""INSERT INTO courses (title, category, description, level, duration, resource_type, resource_link, created_at)
                         VALUES (?,?,?,?,?,?,?,?)""",
                      (title, category, description, "Resource", "-", material_type, resource_link, now()))
            log_admin_action(admin["username"], "Uploaded Material", title)
            st.success(f"'{title}' uploaded successfully!")
            st.rerun()

    section_title("Recently Uploaded Materials")
    materials = run_query("SELECT * FROM courses WHERE resource_type IN ('PDF','Video','Link','Document') ORDER BY created_at DESC LIMIT 10", fetch=True)
    for m in materials:
        glass_card_open()
        st.markdown(f"**📎 {m['title']}** {badge(m['resource_type'],'info')} {badge(m['category'],'purple')}", unsafe_allow_html=True)
        st.caption(m["description"])
        glass_card_close()


# ================= CREATE QUIZZES =================
def page_create_quizzes(admin):
    hero("Create Quizzes", "Build custom quiz questions for learners.", "📝")
    st.info("💡 Quizzes created here appear in the platform's dynamic quiz bank alongside built-in questions.")

    with st.form("quiz_create_form"):
        topic = st.text_input("Quiz Topic", placeholder="e.g. Python Basics")
        question = st.text_input("Question")
        c1, c2 = st.columns(2)
        opt1 = c1.text_input("Option A")
        opt2 = c2.text_input("Option B")
        opt3 = c1.text_input("Option C")
        opt4 = c2.text_input("Option D")
        correct = st.selectbox("Correct Answer", [opt1, opt2, opt3, opt4]) if all([opt1, opt2, opt3, opt4]) else None
        if st.form_submit_button("💾 Save Question") and topic.strip() and question.strip():
            run_query("""INSERT INTO assessments (user_id, assessment_type, answers, result, score, created_at)
                         VALUES (?,?,?,?,?,?)""",
                      (0, f"AdminQuiz::{topic}", f"{question} | {opt1}|{opt2}|{opt3}|{opt4}", correct or "", 0, now()))
            log_admin_action(admin["username"], "Created Quiz Question", f"{topic}: {question}")
            st.success("Question saved to quiz bank!")

    section_title("Admin-Created Questions")
    qs = run_query("SELECT * FROM assessments WHERE assessment_type LIKE 'AdminQuiz::%' ORDER BY created_at DESC LIMIT 10", fetch=True)
    for q in qs:
        glass_card_open()
        topic_name = q["assessment_type"].replace("AdminQuiz::", "")
        st.markdown(f"**[{topic_name}]** {q['answers'].split('|')[0]}")
        st.caption(f"Correct: {q['result']}")
        glass_card_close()


# ================= VIEW ANALYTICS =================
def page_view_analytics(admin):
    hero("Platform Analytics", "Deep insights into user engagement and performance.", "📊")

    quiz_count = run_query("SELECT COUNT(*) c FROM quiz_results", fetchone=True)["c"]
    coding_count = run_query("SELECT COUNT(*) c FROM coding_practice", fetchone=True)["c"]
    interview_count = run_query("SELECT COUNT(*) c FROM mock_interview_results", fetchone=True)["c"]
    resume_count = run_query("SELECT COUNT(*) c FROM resume_data", fetchone=True)["c"]

    c1, c2, c3, c4 = st.columns(4)
    kpi_card("🧠", quiz_count, "Quizzes Taken", c1)
    kpi_card("💻", coding_count, "Coding Submissions", c2)
    kpi_card("🎤", interview_count, "Mock Interviews", c3)
    kpi_card("📄", resume_count, "Resumes Analyzed", c4)

    col1, col2 = st.columns(2)
    with col1:
        section_title("Module Engagement")
        engagement = {
            "Quizzes": quiz_count, "Coding": coding_count,
            "Interviews": interview_count, "Resumes": resume_count,
        }
        st.plotly_chart(bar_chart(list(engagement.keys()), list(engagement.values()), "Feature Usage"), use_container_width=True)
    with col2:
        section_title("Average ATS Scores")
        rows = run_query("SELECT ats_score FROM resume_data WHERE ats_score > 0", fetch=True)
        if rows:
            avg_score = round(sum(r["ats_score"] for r in rows) / len(rows), 1)
            st.metric("Average ATS Score across platform", f"{avg_score}/100")
        else:
            st.info("No resume analysis data yet.")

    section_title("Top Learning Progress")
    progress = run_query("""SELECT u.fullname, COUNT(lp.id) tasks, AVG(lp.progress_pct) avg_pct
                             FROM users u LEFT JOIN learning_progress lp ON u.id = lp.user_id
                             GROUP BY u.id ORDER BY tasks DESC LIMIT 10""", fetch=True)
    if progress:
        df = pd.DataFrame(progress)
        df["avg_pct"] = df["avg_pct"].fillna(0).round(1)
        st.dataframe(df, use_container_width=True, hide_index=True)


# ================= SEND NOTIFICATIONS =================
def page_send_notifications(admin):
    hero("Send Notifications", "Broadcast announcements to all users or specific groups.", "📢")

    with st.form("notif_form"):
        title = st.text_input("Notification Title")
        message = st.text_area("Message")
        target = st.selectbox("Send To", ["All Users", "High School Student", "College Student", "Working Professional"])
        if st.form_submit_button("📢 Send Notification") and title.strip():
            if target == "All Users":
                run_query("INSERT INTO notifications (user_id, title, message, created_at) VALUES (?,?,?,?)",
                           (None, title, message, now()))
                log_admin_action(admin["username"], "Broadcast Notification", title)
                st.success("Notification sent to all users!")
            else:
                users = run_query("SELECT id FROM users WHERE category=?", (target,), fetch=True)
                for u in users:
                    run_query("INSERT INTO notifications (user_id, title, message, created_at) VALUES (?,?,?,?)",
                               (u["id"], title, message, now()))
                log_admin_action(admin["username"], "Targeted Notification", f"{title} -> {target}")
                st.success(f"Notification sent to {len(users)} {target}s!")

    section_title("Recent Notifications Sent")
    notifs = run_query("SELECT * FROM notifications ORDER BY created_at DESC LIMIT 10", fetch=True)
    for n in notifs:
        glass_card_open()
        st.markdown(f"**{n['title']}**")
        st.caption(n["message"])
        st.caption(f"🕒 {n['created_at'][:16].replace('T',' ')}")
        glass_card_close()


# ================= GENERATE REPORTS =================
def page_generate_reports(admin):
    hero("Generate Reports", "Export platform-wide performance reports as PDF.", "📑")

    total_users = run_query("SELECT COUNT(*) c FROM users", fetchone=True)["c"]
    active_users = run_query("SELECT COUNT(*) c FROM users WHERE is_active=1", fetchone=True)["c"]
    total_courses = run_query("SELECT COUNT(*) c FROM courses", fetchone=True)["c"]
    total_certs = run_query("SELECT COUNT(*) c FROM certificates", fetchone=True)["c"]
    quiz_count = run_query("SELECT COUNT(*) c FROM quiz_results", fetchone=True)["c"]
    by_category = run_query("SELECT category, COUNT(*) c FROM users GROUP BY category", fetch=True)

    section_title("Report Preview")
    glass_card_open()
    st.write(f"**Total Users:** {total_users}")
    st.write(f"**Active Users:** {active_users}")
    st.write(f"**Total Courses:** {total_courses}")
    st.write(f"**Certificates Issued:** {total_certs}")
    st.write(f"**Quizzes Completed:** {quiz_count}")
    glass_card_close()

    if st.button("📄 Generate Full Platform Report PDF", type="primary"):
        sections = {
            "Platform Summary": [
                f"Total Users: {total_users}", f"Active Users: {active_users}",
                f"Total Courses: {total_courses}", f"Certificates Issued: {total_certs}",
                f"Quizzes Completed: {quiz_count}",
            ],
            "Users by Category": [f"{r['category']}: {r['c']}" for r in by_category],
        }
        pdf_bytes = generate_report_pdf("TalentSphere Elevate — Platform Report", admin["fullname"], sections)
        run_query("INSERT INTO reports (user_id, report_type, content, created_at) VALUES (?,?,?,?)",
                   (0, "Admin Platform Report", str(sections), now()))
        log_admin_action(admin["username"], "Generated Platform Report", "")
        st.download_button("⬇️ Download Report PDF", data=pdf_bytes, file_name="platform_report.pdf", mime="application/pdf")
