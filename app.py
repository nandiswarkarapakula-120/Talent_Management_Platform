"""
Talent Management Platform for Employee Performance and Career Growth
Main Application Entry Point
Run with: streamlit run app.py
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db, run_query
from auth.auth_utils import signup_user, login_user, login_admin, reset_password
from utils.ui import load_css, hero, section_title, glass_card_open, glass_card_close, render_module_grid, badge
from utils.ai_engine import ai_status

from modules import common, high_school, college, professional, admin as admin_module

# ----------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------
st.set_page_config(
    page_title="Talent Management Platform | Employee Performance & Career Growth",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
load_css()

# ----------------------------------------------------------------
# SESSION STATE DEFAULTS
# ----------------------------------------------------------------
defaults = {
    "logged_in": False, "user": None, "is_admin": False, "admin": None,
    "auth_page": "login", "active_module": "home",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def go_to(page):
    st.session_state.auth_page = page
    st.rerun()


def logout():
    for k in ["logged_in", "user", "is_admin", "admin", "active_module", "chat_log",
              "quiz_qs", "apt_quiz", "cb_quiz", "built_resume", "mock_q_idx"]:
        st.session_state.pop(k, None)
    st.session_state.logged_in = False
    st.session_state.is_admin = False
    st.session_state.active_module = "home"
    st.session_state.auth_page = "login"
    st.rerun()


# ==================================================================
# AUTH PAGES
# ==================================================================

def render_auth_header(logo, title, subtitle):
    st.markdown(f"""
    <div class="auth-logo">{logo}</div>
    <div class="auth-title">{title}</div>
    <div class="auth-subtitle">{subtitle}</div>
    """, unsafe_allow_html=True)


def page_login():
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)
        render_auth_header("🌐", "Talent Management Platform", "for Employee Performance and Career Growth")
        st.markdown("#### Welcome Back 👋")
        with st.form("login_form"):
            identifier = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("🔓 Login", use_container_width=True)
        if submitted:
            ok, msg, user = login_user(identifier, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.session_state.active_module = "home"
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

        c1, c2 = st.columns(2)
        if c1.button("Create an Account", use_container_width=True):
            go_to("signup")
        if c2.button("Forgot Password?", use_container_width=True):
            go_to("forgot")
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("🛡️ Admin Login", use_container_width=True):
            go_to("admin_login")
        st.markdown('</div>', unsafe_allow_html=True)


def page_signup():
    _, mid, _ = st.columns([1, 1.3, 1])
    with mid:
        st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)
        render_auth_header("🌐", "Join Talent Management Platform", "Start your personalized career journey today")
        with st.form("signup_form"):
            fullname = st.text_input("Full Name")
            email = st.text_input("Email")
            username = st.text_input("Username")
            c1, c2 = st.columns(2)
            password = c1.text_input("Password", type="password")
            confirm_password = c2.text_input("Confirm Password", type="password")
            mobile = st.text_input("Mobile Number", max_chars=10)
            category = st.selectbox("I am a...", ["High School Student", "College Student", "Working Professional"])
            submitted = st.form_submit_button("🚀 Create My Account", use_container_width=True)

        if submitted:
            ok, errors, user_id = signup_user(fullname, email, username, password, confirm_password, mobile, category)
            if ok:
                user = run_query("SELECT * FROM users WHERE id=?", (user_id,), fetchone=True)
                st.session_state.logged_in = True
                st.session_state.user = user
                st.session_state.active_module = "home"
                st.success("🎉 Account created successfully! Redirecting to your dashboard...")
                st.balloons()
                st.rerun()
            else:
                for e in errors:
                    st.error(e)

        if st.button("← Back to Login", use_container_width=True):
            go_to("login")
        st.markdown('</div>', unsafe_allow_html=True)


def page_forgot_password():
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)
        render_auth_header("🔑", "Reset Password", "Verify your identity using your registered mobile number")
        with st.form("forgot_form"):
            username = st.text_input("Username")
            mobile = st.text_input("Registered Mobile Number", max_chars=10)
            c1, c2 = st.columns(2)
            new_password = c1.text_input("New Password", type="password")
            confirm_password = c2.text_input("Confirm New Password", type="password")
            submitted = st.form_submit_button("🔄 Reset Password", use_container_width=True)
        if submitted:
            ok, msg = reset_password(username, mobile, new_password, confirm_password)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
        if st.button("← Back to Login", use_container_width=True):
            go_to("login")
        st.markdown('</div>', unsafe_allow_html=True)


def page_admin_login():
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)
        render_auth_header("🛡️", "Admin Portal", "Restricted access — Authorized personnel only")
        with st.form("admin_login_form"):
            username = st.text_input("Admin Username", value="")
            password = st.text_input("Admin Password", type="password")
            submitted = st.form_submit_button("🔓 Admin Login", use_container_width=True)
        if submitted:
            ok, msg, admin = login_admin(username, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.is_admin = True
                st.session_state.admin = admin
                st.session_state.active_module = "admin_home"
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
        st.caption("Default demo credentials — username: `admin`  password: `Admin@123`")
        if st.button("← Back to User Login", use_container_width=True):
            go_to("login")
        st.markdown('</div>', unsafe_allow_html=True)


# ==================================================================
# DASHBOARD HOME (Module Grid) PER CATEGORY
# ==================================================================

MODULE_DEFS = {
    "High School Student": [
        {"icon": "🧭", "title": "Career Explorer", "desc": "Discover exciting career paths", "key": "career_explorer"},
        {"icon": "🧠", "title": "AI Career Quiz", "desc": "Find careers that match you", "key": "career_quiz"},
        {"icon": "📋", "title": "Interest Assessment", "desc": "Rate your domain interests", "key": "interest_assessment"},
        {"icon": "🗺️", "title": "Future Skills Roadmap", "desc": "Skills of tomorrow", "key": "future_skills_roadmap"},
        {"icon": "📅", "title": "Daily Learning Tasks", "desc": "Small daily habits, big results", "key": "daily_tasks"},
        {"icon": "💻", "title": "Coding Basics", "desc": "Learn to code, fun & easy", "key": "coding_basics"},
        {"icon": "🔢", "title": "Aptitude Practice", "desc": "Sharpen reasoning skills", "key": "aptitude_practice"},
        {"icon": "🗣️", "title": "Communication Skills", "desc": "Speak & write with confidence", "key": "communication_skills"},
        {"icon": "🎯", "title": "Goal Tracker", "desc": "Track your personal goals", "key": "goal_tracker"},
        {"icon": "🤖", "title": "AI Mentor Chatbot", "desc": "Your 24/7 career mentor", "key": "chatbot"},
    ],
    "College Student": [
        {"icon": "💻", "title": "Coding Practice", "desc": "Sharpen your DSA skills", "key": "coding_practice"},
        {"icon": "🔥", "title": "Daily Coding Challenge", "desc": "One problem a day", "key": "daily_challenge"},
        {"icon": "📄", "title": "Resume Builder", "desc": "Create a professional resume", "key": "resume_builder"},
        {"icon": "🎯", "title": "ATS Resume Checker", "desc": "Beat the applicant tracking systems", "key": "ats_checker"},
        {"icon": "📚", "title": "Interview Preparation", "desc": "Curated Q&A banks", "key": "interview_prep"},
        {"icon": "🎤", "title": "Mock Interviews", "desc": "Practice with AI feedback", "key": "mock_interviews"},
        {"icon": "🧩", "title": "Skill Gap Analysis", "desc": "Know what to learn next", "key": "skill_gap"},
        {"icon": "📊", "title": "Placement Tracker", "desc": "Track your applications", "key": "placement_tracker"},
        {"icon": "💼", "title": "Internship Recommendations", "desc": "Curated internships for you", "key": "internships"},
        {"icon": "🏆", "title": "Hackathon Updates", "desc": "Upcoming hackathons", "key": "hackathons"},
        {"icon": "🐙", "title": "GitHub Portfolio Review", "desc": "Strengthen your GitHub", "key": "github_review"},
        {"icon": "🔗", "title": "LinkedIn Profile Review", "desc": "Optimize for recruiters", "key": "linkedin_review"},
        {"icon": "🎯", "title": "Goal Tracker", "desc": "Track your personal goals", "key": "goal_tracker"},
        {"icon": "🤖", "title": "AI Mentor Chatbot", "desc": "Your 24/7 career mentor", "key": "chatbot"},
    ],
    "Working Professional": [
        {"icon": "📐", "title": "Skill Assessment", "desc": "Benchmark your skills", "key": "skill_assessment"},
        {"icon": "📈", "title": "Industry Trend Dashboard", "desc": "Stay ahead of the curve", "key": "industry_trends"},
        {"icon": "🎓", "title": "Certification Suggestions", "desc": "Boost your credentials", "key": "certification_suggestions"},
        {"icon": "📝", "title": "Resume Update Assistant", "desc": "Refresh for your next move", "key": "resume_update"},
        {"icon": "🔄", "title": "Career Switching Guide", "desc": "Plan a confident transition", "key": "career_switching"},
        {"icon": "🚀", "title": "Promotion Readiness Score", "desc": "Are you ready for the next step?", "key": "promotion_readiness"},
        {"icon": "💰", "title": "Salary Benchmark", "desc": "Compare your CTC to the market", "key": "salary_benchmark"},
        {"icon": "🤝", "title": "Networking & Visibility Builder", "desc": "Grow your professional network", "key": "networking_builder"},
        {"icon": "🧭", "title": "AI Career Coach", "desc": "Long-term strategy advice", "key": "ai_career_coach"},
        {"icon": "🎯", "title": "Goal Tracker", "desc": "Track your personal goals", "key": "goal_tracker"},
        {"icon": "🤖", "title": "AI Mentor Chatbot", "desc": "Your 24/7 career mentor", "key": "chatbot"},
    ],
}

COMMON_SIDEBAR_ITEMS = [
    ("home", "🏠 Dashboard Home"),
    ("profile", "🧑‍💼 My Profile"),
    ("notifications", "🔔 Notifications"),
    ("learning_dashboard", "📚 Learning Dashboard"),
    ("progress_tracking", "📈 Progress Tracking"),
    ("recommendations", "✨ Recommendations"),
    ("certificates", "🏆 Certificates"),
]

ADMIN_SIDEBAR_ITEMS = [
    ("admin_home", "🏠 Overview"),
    ("manage_users", "👥 Manage Users"),
    ("manage_courses", "📚 Manage Courses"),
    ("manage_career_paths", "🧭 Career Paths"),
    ("upload_materials", "📤 Upload Materials"),
    ("create_quizzes", "📝 Create Quizzes"),
    ("view_analytics", "📊 View Analytics"),
    ("send_notifications", "📢 Send Notifications"),
    ("generate_reports", "📑 Generate Reports"),
]


def page_dashboard_home(user):
    hero(f"Welcome, {user['fullname'].split()[0]}! 👋",
         f"{user['category']} Dashboard — Your personalized career journey starts here.", "🌐")

    unread = run_query("SELECT COUNT(*) c FROM notifications WHERE (user_id=? OR user_id IS NULL) AND is_read=0",
                        (user["id"],), fetchone=True)["c"]
    progress_rows = run_query("SELECT * FROM learning_progress WHERE user_id=?", (user["id"],), fetch=True)
    certs = run_query("SELECT COUNT(*) c FROM certificates WHERE user_id=?", (user["id"],), fetchone=True)["c"]

    from utils.ui import kpi_card
    c1, c2, c3, c4 = st.columns(4)
    kpi_card("📘", len(progress_rows), "Active Modules", c1)
    kpi_card("🔔", unread, "Unread Alerts", c2)
    kpi_card("🏆", certs, "Certificates", c3)
    kpi_card("🎯", user["category"], "Your Track", c4)

    section_title("Explore Your Modules")
    render_module_grid(MODULE_DEFS[user["category"]], cols=4, key_prefix="usermod")


def page_admin_home_grid(admin):
    section_title("Quick Admin Actions")
    admin_modules = [
        {"icon": "👥", "title": "Manage Users", "desc": "Add/edit/deactivate users", "key": "manage_users"},
        {"icon": "📚", "title": "Manage Courses", "desc": "Add learning content", "key": "manage_courses"},
        {"icon": "🧭", "title": "Career Paths", "desc": "Curate career info", "key": "manage_career_paths"},
        {"icon": "📤", "title": "Upload Materials", "desc": "PDFs, videos, resources", "key": "upload_materials"},
        {"icon": "📝", "title": "Create Quizzes", "desc": "Build quiz questions", "key": "create_quizzes"},
        {"icon": "📊", "title": "View Analytics", "desc": "Platform insights", "key": "view_analytics"},
        {"icon": "📢", "title": "Send Notifications", "desc": "Broadcast announcements", "key": "send_notifications"},
        {"icon": "📑", "title": "Generate Reports", "desc": "Export platform reports", "key": "generate_reports"},
    ]
    render_module_grid(admin_modules, cols=4, key_prefix="adminmod")


# ==================================================================
# ROUTING TABLES
# ==================================================================

USER_MODULE_ROUTES = {
    "profile": common.page_profile,
    "notifications": common.page_notifications,
    "learning_dashboard": common.page_learning_dashboard,
    "progress_tracking": common.page_progress_tracking,
    "recommendations": common.page_recommendations,
    "certificates": common.page_certificates,
    "goal_tracker": common.page_goal_tracker,
    "chatbot": common.page_chatbot,
    # High School
    "career_explorer": high_school.page_career_explorer,
    "career_quiz": high_school.page_career_quiz,
    "interest_assessment": high_school.page_interest_assessment,
    "future_skills_roadmap": high_school.page_future_skills_roadmap,
    "daily_tasks": high_school.page_daily_tasks,
    "coding_basics": high_school.page_coding_basics,
    "aptitude_practice": high_school.page_aptitude_practice,
    "communication_skills": high_school.page_communication_skills,
    # College
    "coding_practice": college.page_coding_practice,
    "daily_challenge": college.page_daily_challenge,
    "resume_builder": college.page_resume_builder,
    "ats_checker": college.page_ats_checker,
    "interview_prep": college.page_interview_prep,
    "mock_interviews": college.page_mock_interviews,
    "skill_gap": college.page_skill_gap,
    "placement_tracker": college.page_placement_tracker,
    "internships": college.page_internship_recommendations,
    "hackathons": college.page_hackathon_updates,
    "github_review": college.page_github_review,
    "linkedin_review": college.page_linkedin_review,
    # Working Professional
    "skill_assessment": professional.page_skill_assessment,
    "industry_trends": professional.page_industry_trends,
    "certification_suggestions": professional.page_certification_suggestions,
    "resume_update": professional.page_resume_update_assistant,
    "career_switching": professional.page_career_switching_guide,
    "promotion_readiness": professional.page_promotion_readiness,
    "salary_benchmark": professional.page_salary_benchmark,
    "networking_builder": professional.page_networking_builder,
    "ai_career_coach": professional.page_ai_career_coach,
}

ADMIN_MODULE_ROUTES = {
    "manage_users": admin_module.page_manage_users,
    "manage_courses": admin_module.page_manage_courses,
    "manage_career_paths": admin_module.page_manage_career_paths,
    "upload_materials": admin_module.page_upload_materials,
    "create_quizzes": admin_module.page_create_quizzes,
    "view_analytics": admin_module.page_view_analytics,
    "send_notifications": admin_module.page_send_notifications,
    "generate_reports": admin_module.page_generate_reports,
}


# ==================================================================
# SIDEBAR + APP SHELL
# ==================================================================

def render_user_sidebar(user):
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">🌐 Talent Management Platform</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sidebar-user">
            <div style="font-size:2.2rem">{user.get('avatar','🧑‍🎓')}</div>
            <strong>{user['fullname']}</strong><br>
            <span style="font-size:0.8rem;color:#636E72">{user['category']}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**MAIN**")
        for key, label in COMMON_SIDEBAR_ITEMS:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.active_module = key
                st.rerun()

        st.markdown("---")
        st.markdown(f"**{user['category'].upper()} MODULES**")
        for m in MODULE_DEFS[user["category"]]:
            if m["key"] in ("goal_tracker", "chatbot"):
                continue
            if st.button(f"{m['icon']} {m['title']}", key=f"nav_{m['key']}", use_container_width=True):
                st.session_state.active_module = m["key"]
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()


def render_admin_sidebar(admin):
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">🛡️ Admin Portal</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sidebar-user">
            <div style="font-size:2.2rem">🛡️</div>
            <strong>{admin['fullname']}</strong><br>
            <span style="font-size:0.8rem;color:#636E72">Administrator</span>
        </div>
        """, unsafe_allow_html=True)

        for key, label in ADMIN_SIDEBAR_ITEMS:
            if st.button(label, key=f"anav_{key}", use_container_width=True):
                st.session_state.active_module = key
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()


def run_user_app():
    user = run_query("SELECT * FROM users WHERE id=?", (st.session_state.user["id"],), fetchone=True)
    if not user:
        logout()
        return
    st.session_state.user = user
    render_user_sidebar(user)

    active = st.session_state.active_module
    if active == "home":
        page_dashboard_home(user)
    elif active in USER_MODULE_ROUTES:
        if st.button("← Back to Dashboard"):
            st.session_state.active_module = "home"
            st.rerun()
        USER_MODULE_ROUTES[active](user)
    else:
        page_dashboard_home(user)


def run_admin_app():
    admin = st.session_state.admin
    render_admin_sidebar(admin)

    active = st.session_state.active_module
    if active == "admin_home":
        admin_module.page_admin_overview(admin)
        page_admin_home_grid(admin)
    elif active in ADMIN_MODULE_ROUTES:
        if st.button("← Back to Overview"):
            st.session_state.active_module = "admin_home"
            st.rerun()
        ADMIN_MODULE_ROUTES[active](admin)
    else:
        admin_module.page_admin_overview(admin)
        page_admin_home_grid(admin)


# ==================================================================
# MAIN ROUTER
# ==================================================================

def main():
    if not st.session_state.logged_in:
        page = st.session_state.auth_page
        if page == "signup":
            page_signup()
        elif page == "forgot":
            page_forgot_password()
        elif page == "admin_login":
            page_admin_login()
        else:
            page_login()
        return

    if st.session_state.is_admin:
        run_admin_app()
    else:
        run_user_app()


if __name__ == "__main__":
    main()
