"""
TalentSphere Elevate - High School Student Modules
Career Explorer, AI Career Quiz, Interest Assessment, Future Skills Roadmap,
Daily Learning Tasks, Coding Basics, Aptitude Practice, Communication Skills.
"""

import streamlit as st
import random
from datetime import datetime

from database.db import run_query, now, get_profile_extra
from utils.ui import hero, section_title, kpi_card, glass_card_open, glass_card_close, badge
from utils.charts import radar_chart, bar_chart, donut_chart
from utils.ai_engine import generate_quiz, suggest_learning_roadmap, QUIZ_BANK


def _recommend_matching_courses(keywords, category="High School Student", limit=3):
    """Fetch courses whose title/description matches any of the given keywords."""
    courses = run_query("SELECT * FROM courses WHERE category=? OR category='All'", (category,), fetch=True)
    kws = [k.strip().lower() for k in keywords if k and k.strip()]
    matched = [c for c in courses if any(k in f"{c['title']} {c['description']}".lower() for k in kws)]
    return matched[:limit] if matched else courses[:limit]


def _render_course_cards(courses):
    section_title("📚 Recommended Courses Based on Your Result")
    if not courses:
        st.info("No matching courses found yet — check the Learning Dashboard for more options.")
        return
    cols = st.columns(len(courses))
    for col, course in zip(cols, courses):
        with col:
            glass_card_open()
            st.markdown(f"**📘 {course['title']}**")
            st.caption(course["description"])
            st.markdown(badge(course["level"], "info"), unsafe_allow_html=True)
            glass_card_close()


# ================= CAREER EXPLORER =================
def page_career_explorer(user):
    hero("Career Explorer", "Discover exciting career paths and what they involve.", "🧭")
    paths = run_query("SELECT * FROM career_paths ORDER BY title ASC", fetch=True)

    search = st.text_input("🔍 Search careers", placeholder="e.g. Doctor, Engineer, Designer...")
    filtered = [p for p in paths if search.lower() in p["title"].lower()] if search else paths

    for i in range(0, len(filtered), 2):
        cols = st.columns(2)
        for col, p in zip(cols, filtered[i:i + 2]):
            with col:
                glass_card_open()
                st.markdown(f"### 🎓 {p['title']}")
                st.write(p["description"])
                st.markdown(f"**Required Skills:** {p['required_skills']}")
                c1, c2 = st.columns(2)
                c1.markdown(badge(f"💰 {p['avg_salary']}", "success"), unsafe_allow_html=True)
                c2.markdown(badge(f"📈 {p['growth_outlook']} Growth", "info"), unsafe_allow_html=True)
                glass_card_close()


# ================= AI CAREER QUIZ =================
def page_career_quiz(user):
    hero("AI Career Quiz", "Answer a few questions to discover careers that match you.", "🧠")

    if "quiz_qs" not in st.session_state or st.session_state.get("quiz_topic_active") != "Career Interest":
        st.session_state.quiz_qs = generate_quiz("Career Interest", 5)
        st.session_state.quiz_topic_active = "Career Interest"
        st.session_state.quiz_answers = {}

    with st.form("career_quiz_form"):
        for i, q in enumerate(st.session_state.quiz_qs):
            choice = st.radio(f"**{i+1}. {q['q']}**", q["options"], key=f"cq_{i}", index=None)
            st.session_state.quiz_answers[i] = choice
        submitted = st.form_submit_button("🎯 Get My Results", type="primary")

    if submitted:
        if any(v is None for v in st.session_state.quiz_answers.values()):
            st.warning("Please answer all questions.")
        else:
            trait_scores = {"Analytical": 0, "Social": 0, "Creative": 0, "Leadership": 0}
            for i, q in enumerate(st.session_state.quiz_qs):
                answer = st.session_state.quiz_answers[i]
                idx = q["options"].index(answer)
                trait = q["trait"][idx]
                trait_scores[trait] += 1

            top_trait = max(trait_scores, key=trait_scores.get)
            career_map = {
                "Analytical": ["Data Scientist", "Engineer (B.Tech)", "Chartered Accountant"],
                "Social": ["Doctor (MBBS)", "Teacher / Educator", "Psychologist"],
                "Creative": ["UI/UX Designer", "Content Creator / Digital Marketer"],
                "Leadership": ["Entrepreneur", "Product Manager", "Civil Services (UPSC)"],
            }
            st.success(f"Your dominant trait is **{top_trait}**! 🎉")
            st.plotly_chart(radar_chart(list(trait_scores.keys()), [v * 20 for v in trait_scores.values()],
                                         "Your Personality Trait Profile"), use_container_width=True)

            section_title("Careers Matched to You")
            for career in career_map.get(top_trait, []):
                st.markdown(f"- 🎯 **{career}**")

            total_score = max(trait_scores.values()) * 20
            run_query("INSERT INTO quiz_results (user_id, quiz_topic, score, total, details, created_at) VALUES (?,?,?,?,?,?)",
                       (user["id"], "Career Interest Quiz", total_score, 100, top_trait, now()))

            matched_courses = _recommend_matching_courses(career_map.get(top_trait, []) + [top_trait], user["category"])
            _render_course_cards(matched_courses)
            st.balloons()


# ================= INTEREST ASSESSMENT =================
def page_interest_assessment(user):
    hero("Interest Assessment", "Rate your interest across different domains.", "📋")
    domains = ["Science & Technology", "Arts & Design", "Business & Finance", "Healthcare & Medicine",
               "Social Service & Education", "Sports & Fitness"]
    scores = {}
    with st.form("interest_form"):
        for d in domains:
            scores[d] = st.slider(d, 0, 10, 5)
        submitted = st.form_submit_button("📊 Analyze My Interests", type="primary")

    if submitted:
        st.plotly_chart(bar_chart(list(scores.keys()), list(scores.values()),
                                   "Your Interest Levels", horizontal=True), use_container_width=True)
        top_domain = max(scores, key=scores.get)
        st.success(f"Your strongest interest area is **{top_domain}** 🌟")
        run_query("INSERT INTO assessments (user_id, assessment_type, answers, result, score, created_at) VALUES (?,?,?,?,?,?)",
                   (user["id"], "Interest Assessment", str(scores), top_domain, scores[top_domain] * 10, now()))

        matched_courses = _recommend_matching_courses([top_domain], user["category"])
        _render_course_cards(matched_courses)


# ================= FUTURE SKILLS ROADMAP =================
def page_future_skills_roadmap(user):
    hero("Future Skills Roadmap", "Explore the skills of tomorrow and how to build them.", "🗺️")
    goal = st.selectbox("What field interests you most?",
                         ["Software Engineer", "Data Scientist", "UI/UX Designer", "Cybersecurity Analyst", "Cloud Architect"])
    if st.button("🚀 Generate My Roadmap", type="primary"):
        roadmap = suggest_learning_roadmap(goal, "Beginner")
        if isinstance(roadmap, str):
            st.markdown(roadmap)
        else:
            for phase in roadmap:
                glass_card_open()
                st.markdown(f"### {phase['phase']}")
                for topic in phase["topics"]:
                    st.markdown(f"- ✅ {topic}")
                glass_card_close()


# ================= DAILY LEARNING TASKS =================
DAILY_TASKS = [
    "Read one article about a career field you're curious about (15 min)",
    "Practice 5 aptitude questions",
    "Watch a 10-minute video on a new skill",
    "Write 3 things you learned today in a journal",
    "Solve one coding basics problem",
    "Practice public speaking for 5 minutes in front of a mirror",
    "Research one college/course option for your interest area",
]


def page_daily_tasks(user):
    hero("Daily Learning Tasks", "Small daily habits that build a big future.", "📅")
    today = datetime.now().strftime("%Y-%m-%d")
    random.seed(today + str(user["id"]))
    todays_tasks = random.sample(DAILY_TASKS, 4)

    section_title(f"Today's Tasks — {datetime.now().strftime('%d %B %Y')}")
    completed_count = 0
    for i, task in enumerate(todays_tasks):
        key = f"task_{today}_{i}"
        existing = run_query("SELECT * FROM learning_progress WHERE user_id=? AND task=?",
                              (user["id"], task), fetchone=True)
        checked = st.checkbox(task, value=bool(existing and existing["status"] == "Completed"), key=key)
        if checked:
            completed_count += 1
            if not existing:
                run_query("""INSERT INTO learning_progress (user_id, module, task, status, progress_pct, updated_at)
                             VALUES (?,?,?,?,?,?)""",
                          (user["id"], "Daily Tasks", task, "Completed", 100, now()))
            elif existing["status"] != "Completed":
                run_query("UPDATE learning_progress SET status='Completed', progress_pct=100, updated_at=? WHERE id=?",
                           (now(), existing["id"]))

    st.progress(completed_count / len(todays_tasks))
    st.caption(f"{completed_count}/{len(todays_tasks)} tasks completed today")
    if completed_count == len(todays_tasks):
        st.success("🎉 Amazing! You completed all of today's tasks!")


# ================= CODING BASICS =================
def page_coding_basics(user):
    hero("Coding Basics", "Learn to code with fun, bite-sized lessons and quizzes.", "💻")
    tab1, tab2 = st.tabs(["📖 Learn", "📝 Quiz"])

    with tab1:
        topic = st.selectbox("Choose a topic", ["Variables & Data Types", "Loops", "Conditionals", "Functions", "Lists"])
        lessons = {
            "Variables & Data Types": "Variables store data. In Python: `name = 'Alex'` creates a string variable. Numbers, text, and True/False are common data types.",
            "Loops": "Loops repeat actions. `for i in range(5): print(i)` prints numbers 0 to 4.",
            "Conditionals": "if/else lets code make decisions. `if age >= 18: print('Adult')` else: `print('Minor')`",
            "Functions": "Functions are reusable blocks. `def greet(name): return f'Hello {name}'`",
            "Lists": "Lists store multiple items. `fruits = ['apple','banana']` — access with `fruits[0]`.",
        }
        glass_card_open()
        st.markdown(f"### {topic}")
        st.code(lessons[topic], language="python")
        glass_card_close()

    with tab2:
        if "cb_quiz" not in st.session_state:
            st.session_state.cb_quiz = generate_quiz("Coding Basics", 5)
        with st.form("coding_quiz"):
            answers = {}
            for i, q in enumerate(st.session_state.cb_quiz):
                answers[i] = st.radio(f"{i+1}. {q['q']}", q["options"], key=f"cbq_{i}", index=None)
            if st.form_submit_button("Submit Quiz", type="primary"):
                score = sum(1 for i, q in enumerate(st.session_state.cb_quiz) if answers[i] == q["answer"])
                st.success(f"You scored {score}/{len(st.session_state.cb_quiz)}!")
                run_query("INSERT INTO quiz_results (user_id, quiz_topic, score, total, details, created_at) VALUES (?,?,?,?,?,?)",
                           (user["id"], "Coding Basics", score, len(st.session_state.cb_quiz), "", now()))
                if score == len(st.session_state.cb_quiz):
                    st.balloons()


# ================= APTITUDE PRACTICE =================
def page_aptitude_practice(user):
    hero("Aptitude Practice", "Sharpen your logical & quantitative reasoning.", "🔢")
    if "apt_quiz" not in st.session_state:
        st.session_state.apt_quiz = generate_quiz("Aptitude", 5)
    with st.form("aptitude_quiz"):
        answers = {}
        for i, q in enumerate(st.session_state.apt_quiz):
            answers[i] = st.radio(f"{i+1}. {q['q']}", q["options"], key=f"aq_{i}", index=None)
        if st.form_submit_button("Submit", type="primary"):
            score = sum(1 for i, q in enumerate(st.session_state.apt_quiz) if answers[i] == q["answer"])
            st.success(f"Score: {score}/{len(st.session_state.apt_quiz)}")
            st.plotly_chart(donut_chart(["Correct", "Incorrect"],
                                         [score, len(st.session_state.apt_quiz) - score], "Result"),
                             use_container_width=True)
            run_query("INSERT INTO quiz_results (user_id, quiz_topic, score, total, details, created_at) VALUES (?,?,?,?,?,?)",
                       (user["id"], "Aptitude", score, len(st.session_state.apt_quiz), "", now()))
    if st.button("🔄 New Set of Questions"):
        st.session_state.apt_quiz = generate_quiz("Aptitude", 5)
        st.rerun()


# ================= COMMUNICATION SKILLS =================
def page_communication_skills(user):
    hero("Communication Skills", "Build confidence in speaking, writing and listening.", "🗣️")
    tab1, tab2 = st.tabs(["🎤 Speaking Practice", "✍️ Writing Practice"])

    with tab1:
        prompts = ["Introduce yourself in 30 seconds.", "Describe your favorite hobby.",
                   "Talk about a book/movie that inspired you.", "Explain why teamwork matters."]
        prompt = st.selectbox("Choose a speaking prompt", prompts)
        st.info(f"🎯 Prompt: {prompt}")
        response = st.text_area("Type what you would say (practice structuring your thoughts):", height=120)
        if st.button("Get Feedback", key="speak_fb"):
            if response.strip():
                word_count = len(response.split())
                fb = []
                if word_count < 20:
                    fb.append("💡 Try to elaborate a bit more with examples.")
                else:
                    fb.append("✅ Good length and detail!")
                if response.strip().endswith((".", "!")):
                    fb.append("✅ Clear sentence structure.")
                for f in fb:
                    st.write(f)
            else:
                st.warning("Please write a response first.")

    with tab2:
        topic = st.text_input("Writing topic", value="Why is continuous learning important?")
        essay = st.text_area("Write a short paragraph:", height=150)
        if st.button("Analyze Writing", key="write_fb"):
            if essay.strip():
                words = len(essay.split())
                sentences = essay.count(".") + essay.count("!") + essay.count("?")
                st.markdown(f"**Word count:** {words}  |  **Sentences:** {max(sentences,1)}")
                if words < 50:
                    st.warning("Try writing a bit more to fully develop your idea.")
                else:
                    st.success("Good effort! Clear structure helps readability.")
            else:
                st.warning("Please write something first.")
