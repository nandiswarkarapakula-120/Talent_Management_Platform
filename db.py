"""
TalentSphere Elevate - Database Layer
Handles SQLite connection, schema creation and all CRUD helper functions.
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "talentsphere.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            mobile TEXT NOT NULL,
            category TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            avatar TEXT DEFAULT '🧑‍🎓',
            theme TEXT DEFAULT 'light',
            created_at TEXT NOT NULL
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            fullname TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            assessment_type TEXT,
            answers TEXT,
            result TEXT,
            score REAL,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS learning_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            module TEXT,
            task TEXT,
            status TEXT DEFAULT 'Pending',
            progress_pct REAL DEFAULT 0,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            description TEXT,
            level TEXT,
            duration TEXT,
            resource_type TEXT,
            resource_link TEXT,
            created_at TEXT
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS career_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            description TEXT,
            required_skills TEXT,
            avg_salary TEXT,
            growth_outlook TEXT,
            created_at TEXT
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            message TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TEXT
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT,
            issued_on TEXT,
            cert_code TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            report_type TEXT,
            content TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS resume_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resume_text TEXT,
            target_role TEXT,
            ats_score REAL,
            feedback TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_topic TEXT,
            score REAL,
            total INTEGER,
            details TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS mock_interview_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT,
            question TEXT,
            answer TEXT,
            feedback TEXT,
            score REAL,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS coding_practice (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            problem TEXT,
            language TEXT,
            code TEXT,
            feedback TEXT,
            status TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT,
            description TEXT,
            skills TEXT,
            status TEXT DEFAULT 'Suggested',
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT,
            badge TEXT,
            earned_on TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS admin_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_username TEXT,
            action TEXT,
            details TEXT,
            created_at TEXT
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT,
            message TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            goal_text TEXT,
            target_date TEXT,
            status TEXT DEFAULT 'In Progress',
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        _migrate_schema(c)
        _seed_data(c)


def _migrate_schema(c):
    """Adds new columns to existing tables without breaking older databases."""
    c.execute("PRAGMA table_info(users)")
    existing_cols = {row[1] for row in c.fetchall()}
    if "profile_extra" not in existing_cols:
        c.execute("ALTER TABLE users ADD COLUMN profile_extra TEXT DEFAULT '{}'")


def _seed_data(c):
    c.execute("SELECT COUNT(*) FROM admins")
    if c.fetchone()[0] == 0:
        from auth.auth_utils import hash_password
        c.execute(
            "INSERT INTO admins (username, password, fullname, created_at) VALUES (?,?,?,?)",
            ("admin", hash_password("Admin@123"), "System Administrator", datetime.now().isoformat())
        )

    c.execute("SELECT COUNT(*) FROM career_paths")
    if c.fetchone()[0] == 0:
        paths = [
            ("Data Scientist", "College Student", "Analyze data to extract insights using statistics and ML.",
             "Python, Statistics, Machine Learning, SQL", "₹8-25 LPA", "Very High"),
            ("Software Engineer", "College Student", "Design, build and maintain software systems.",
             "DSA, Python/Java, System Design, Git", "₹6-30 LPA", "Very High"),
            ("UI/UX Designer", "College Student", "Design intuitive and beautiful digital experiences.",
             "Figma, Design Thinking, Prototyping", "₹4-15 LPA", "High"),
            ("Cybersecurity Analyst", "Working Professional", "Protect systems and networks from digital attacks.",
             "Networking, Security Tools, Ethical Hacking", "₹6-20 LPA", "Very High"),
            ("Cloud Architect", "Working Professional", "Design scalable cloud infrastructure.",
             "AWS/Azure/GCP, DevOps, Networking", "₹15-40 LPA", "Very High"),
            ("Product Manager", "Working Professional", "Own product vision and roadmap.",
             "Communication, Analytics, Strategy", "₹12-35 LPA", "High"),
            ("Doctor (MBBS)", "High School Student", "Diagnose and treat patients, save lives.",
             "Biology, Chemistry, Empathy, NEET", "₹6-30 LPA", "High"),
            ("Engineer (B.Tech)", "High School Student", "Apply science and math to build solutions.",
             "Physics, Math, Problem Solving, JEE", "₹5-25 LPA", "Very High"),
            ("Chartered Accountant", "High School Student", "Manage finance, audits and taxation.",
             "Accounting, Math, Analytical Thinking", "₹7-25 LPA", "High"),
            ("Content Creator / Digital Marketer", "High School Student", "Build audiences and market brands online.",
             "Creativity, SEO, Communication", "₹3-15 LPA", "High"),
        ]
        for p in paths:
            c.execute("""INSERT INTO career_paths
                (title, category, description, required_skills, avg_salary, growth_outlook, created_at)
                VALUES (?,?,?,?,?,?,?)""", (*p, datetime.now().isoformat()))

    c.execute("SELECT COUNT(*) FROM courses")
    if c.fetchone()[0] == 0:
        courses = [
            ("Python for Beginners", "All", "Learn Python from scratch with hands-on exercises.", "Beginner", "4 weeks", "Video", "#"),
            ("Data Structures & Algorithms", "College Student", "Master DSA for coding interviews.", "Intermediate", "8 weeks", "Course", "#"),
            ("Resume Writing Masterclass", "College Student", "Craft an ATS-friendly resume.", "Beginner", "1 week", "PDF", "#"),
            ("Communication Skills 101", "High School Student", "Build confident public speaking skills.", "Beginner", "2 weeks", "Video", "#"),
            ("Cloud Computing Fundamentals", "Working Professional", "AWS / Azure basics for professionals.", "Intermediate", "6 weeks", "Course", "#"),
            ("Aptitude & Reasoning", "High School Student", "Practice quantitative & logical reasoning.", "Beginner", "3 weeks", "Practice Set", "#"),
            # High School — mapped to interest areas
            ("Intro to Engineering & Robotics", "High School Student", "Explore Science & Engineering fundamentals through fun robotics projects.", "Beginner", "4 weeks", "Video", "#"),
            ("NEET Biology Foundations", "High School Student", "Foundational biology concepts for Medicine & Healthcare aspirants (NEET).", "Intermediate", "6 weeks", "Course", "#"),
            ("JEE Physics Crash Course", "High School Student", "Physics fundamentals for JEE and Science & Engineering track.", "Intermediate", "6 weeks", "Course", "#"),
            ("Commerce & Finance Basics", "High School Student", "Understand accounting, economics and finance basics.", "Beginner", "3 weeks", "Course", "#"),
            ("Design Thinking for Beginners", "High School Student", "Explore Arts & Design careers through creative design projects.", "Beginner", "3 weeks", "Video", "#"),
            ("Civics & Public Administration 101", "High School Student", "Foundations for Humanities & Civil Services aspirants.", "Beginner", "4 weeks", "Course", "#"),
            ("Sports Science Essentials", "High School Student", "Basics of sports science and fitness careers.", "Beginner", "2 weeks", "Video", "#"),
            # College — mapped to branches/roles
            ("Machine Learning A-Z", "College Student", "Complete ML course covering AI/ML specialization and Data Scientist roles.", "Intermediate", "10 weeks", "Course", "#"),
            ("Cybersecurity Fundamentals", "College Student", "Learn networking, ethical hacking basics for Cybersecurity specialization.", "Intermediate", "8 weeks", "Course", "#"),
            ("Full-Stack Web Development", "College Student", "Build complete web apps — great for Computer Science / Software Engineer track.", "Intermediate", "10 weeks", "Course", "#"),
            ("Cloud & DevOps Bootcamp", "College Student", "AWS, Docker and CI/CD for Cloud Architect aspirants.", "Intermediate", "8 weeks", "Course", "#"),
            ("UI/UX Design Specialization", "College Student", "Figma, prototyping and design thinking for UI/UX Designer role.", "Beginner", "6 weeks", "Course", "#"),
            ("Electronics & Mechanical Design", "College Student", "Core concepts for Mechanical/Electronics branch students.", "Intermediate", "8 weeks", "Course", "#"),
            # Working Professional — mapped to industry/skills/goals
            ("Advanced Data Science for Professionals", "Working Professional", "Upskill in Python, ML and analytics for career growth in Technology.", "Advanced", "8 weeks", "Course", "#"),
            ("Leadership & People Management", "Working Professional", "Build leadership and management skills for your career goal of promotion.", "Intermediate", "4 weeks", "Course", "#"),
            ("FinTech & Financial Analytics", "Working Professional", "For professionals in the Finance industry aiming to upskill.", "Intermediate", "6 weeks", "Course", "#"),
            ("Product Management Essentials", "Working Professional", "Learn strategy, roadmapping for a career switch into Product Management.", "Intermediate", "6 weeks", "Course", "#"),
            ("Advanced Cloud Architecture", "Working Professional", "Deepen your Cloud Computing and DevOps skills for senior roles.", "Advanced", "8 weeks", "Course", "#"),
            ("Digital Marketing Mastery", "Working Professional", "SEO, analytics and content strategy for Marketing industry professionals.", "Intermediate", "5 weeks", "Course", "#"),
        ]
        for co in courses:
            c.execute("""INSERT INTO courses
                (title, category, description, level, duration, resource_type, resource_link, created_at)
                VALUES (?,?,?,?,?,?,?,?)""", (*co, datetime.now().isoformat()))


# ---------------- Generic Helpers ----------------

def run_query(query, params=(), fetch=False, fetchone=False):
    with get_conn() as conn:
        cur = conn.execute(query, params)
        if fetchone:
            row = cur.fetchone()
            return dict(row) if row else None
        if fetch:
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        return cur.lastrowid


def now():
    return datetime.now().isoformat(timespec="seconds")


# ---------------- Profile Extra (category-specific fields) Helpers ----------------

def get_profile_extra(user):
    """Parses the JSON blob stored in users.profile_extra into a dict."""
    import json
    raw = user.get("profile_extra") if isinstance(user, dict) else None
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}


def save_profile_extra(user_id, data: dict):
    """Merges `data` into the existing profile_extra JSON blob for a user."""
    import json
    existing = run_query("SELECT profile_extra FROM users WHERE id=?", (user_id,), fetchone=True)
    current = {}
    if existing and existing.get("profile_extra"):
        try:
            current = json.loads(existing["profile_extra"])
        except Exception:
            current = {}
    current.update(data)
    run_query("UPDATE users SET profile_extra=? WHERE id=?", (json.dumps(current), user_id))
    return current

