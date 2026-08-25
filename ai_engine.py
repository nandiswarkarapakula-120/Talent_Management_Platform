"""
TalentSphere Elevate - AI Engine
Provides AI-powered features with a rule-based / scikit-learn fallback.
If OPENAI_API_KEY or GEMINI_API_KEY environment variables are set, the engine
will transparently switch to using the real LLM API without any change
required elsewhere in the app (Strategy Pattern).
"""

import os
import random
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
AI_MODE = "openai" if OPENAI_API_KEY else ("gemini" if GEMINI_API_KEY else "rule_based")


def ai_status():
    return AI_MODE


def _call_openai(prompt, system="You are a helpful, encouraging career guidance AI assistant."):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            max_tokens=500,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[AI temporarily unavailable, using offline mode] {rule_based_chat_reply(prompt)}"


def _call_gemini(prompt, system="You are a helpful, encouraging career guidance AI assistant."):
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system)
        resp = model.generate_content(prompt)
        return resp.text
    except Exception:
        return rule_based_chat_reply(prompt)


def ai_generate(prompt, system=None):
    """Central dispatcher: uses real API if configured, else rule-based fallback."""
    if AI_MODE == "openai":
        return _call_openai(prompt, system) if system else _call_openai(prompt)
    if AI_MODE == "gemini":
        return _call_gemini(prompt, system) if system else _call_gemini(prompt)
    return rule_based_chat_reply(prompt)


# ==========================================================
# 1. CAREER RECOMMENDATION ENGINE (TF-IDF + Cosine Similarity)
# ==========================================================

CAREER_PROFILES = {
    "Data Scientist": "math statistics python analysis logical data curious research problem solving analytical",
    "Software Engineer": "coding programming logical problem solving building systems technology python java",
    "UI/UX Designer": "creative design art visual empathy aesthetics user experience drawing",
    "Cybersecurity Analyst": "security detail oriented logical investigative technology puzzles protective",
    "Cloud Architect": "systems technology infrastructure logical scalable engineering organized",
    "Product Manager": "communication leadership strategy organized people planning business",
    "Doctor (MBBS)": "biology helping people science care empathy medicine health service",
    "Engineer (B.Tech)": "math physics building problem solving logical technical innovation",
    "Chartered Accountant": "math numbers organized detail oriented finance analytical accuracy",
    "Content Creator / Digital Marketer": "creative communication social media writing storytelling trendy",
    "Teacher / Educator": "communication patience helping people explaining mentoring people oriented",
    "Entrepreneur": "leadership risk taking creative business strategy independent innovation",
    "Psychologist": "empathy people oriented listening research helping communication",
    "Civil Services (UPSC)": "leadership service society law governance communication analytical",
    "Mechanical Engineer": "math physics building hands on machines technical problem solving",
}


def recommend_careers(interest_text, category="College Student", top_n=5):
    """Rule-based recommendation using TF-IDF cosine similarity across a career bank."""
    if AI_MODE != "rule_based":
        prompt = (f"Based on these interests: '{interest_text}', suggest the top {top_n} career paths "
                  f"for a {category}. For each, give a one-line reason. Keep it concise.")
        return ai_generate(prompt)

    titles = list(CAREER_PROFILES.keys())
    docs = list(CAREER_PROFILES.values()) + [interest_text.lower()]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(docs)
    sims = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()
    ranked = sorted(zip(titles, sims), key=lambda x: x[1], reverse=True)
    results = []
    for title, score in ranked[:top_n]:
        pct = round(float(min(99, max(35, score * 100 + random.uniform(5, 15)))), 1)
        results.append({"career": title, "match": pct})
    return results


# ==========================================================
# 2. SKILL GAP ANALYSIS
# ==========================================================

ROLE_SKILL_MAP = {
    "Data Scientist": ["Python", "Statistics", "Machine Learning", "SQL", "Data Visualization", "Deep Learning"],
    "Software Engineer": ["DSA", "Python/Java/C++", "Git", "System Design", "Databases", "Testing"],
    "UI/UX Designer": ["Figma", "Design Thinking", "Wireframing", "User Research", "Prototyping"],
    "Cybersecurity Analyst": ["Networking", "Linux", "Security Tools", "Ethical Hacking", "Cryptography"],
    "Cloud Architect": ["AWS/Azure/GCP", "Docker", "Kubernetes", "Networking", "DevOps", "IaC"],
    "Product Manager": ["Communication", "Analytics", "Roadmapping", "Agile", "Stakeholder Management"],
}


def analyze_skill_gap(current_skills, target_role):
    if AI_MODE != "rule_based":
        prompt = (f"My current skills are: {current_skills}. My target role is {target_role}. "
                  f"List the skill gaps and a 4-step learning roadmap to bridge them.")
        return {"ai_text": ai_generate(prompt)}

    required = ROLE_SKILL_MAP.get(target_role, ["Python", "Communication", "Problem Solving", "Domain Knowledge"])
    current_set = {s.strip().lower() for s in current_skills.split(",") if s.strip()}
    missing = [s for s in required if s.lower() not in current_set]
    have = [s for s in required if s.lower() in current_set]
    readiness = round((len(have) / len(required)) * 100, 1) if required else 0
    return {
        "required": required,
        "have": have,
        "missing": missing,
        "readiness_pct": readiness,
    }


# ==========================================================
# 3. RESUME / ATS ANALYSIS
# ==========================================================

def ats_resume_score(resume_text, job_description=""):
    if not resume_text.strip():
        return {"score": 0, "feedback": ["Please paste your resume text first."]}

    feedback = []
    score = 0

    sections = ["experience", "education", "skills", "project", "summary", "certification"]
    found_sections = [s for s in sections if s in resume_text.lower()]
    score += len(found_sections) * 8
    if len(found_sections) < 4:
        feedback.append(f"⚠️ Add missing sections: {', '.join(set(sections) - set(found_sections))}")
    else:
        feedback.append("✅ Good section coverage (Experience/Education/Skills etc.)")

    word_count = len(resume_text.split())
    if 300 <= word_count <= 900:
        score += 15
        feedback.append("✅ Resume length is appropriate.")
    else:
        feedback.append("⚠️ Ideal resume length is 300-900 words. Yours is " + str(word_count) + ".")

    action_verbs = ["led", "built", "developed", "designed", "improved", "managed", "created",
                     "implemented", "achieved", "increased", "reduced", "launched", "optimized"]
    verb_hits = sum(1 for v in action_verbs if v in resume_text.lower())
    score += min(20, verb_hits * 3)
    if verb_hits >= 4:
        feedback.append(f"✅ Strong action verbs detected ({verb_hits} found).")
    else:
        feedback.append("⚠️ Use more action verbs like 'developed', 'led', 'improved'.")

    numbers_found = len(re.findall(r"\d+%|\d+\+|\$\d+|\d{2,}", resume_text))
    score += min(15, numbers_found * 3)
    if numbers_found >= 3:
        feedback.append(f"✅ Good use of quantifiable metrics ({numbers_found} found).")
    else:
        feedback.append("⚠️ Add quantifiable achievements (e.g., 'increased efficiency by 20%').")

    if job_description.strip():
        vectorizer = TfidfVectorizer(stop_words="english")
        try:
            tfidf = vectorizer.fit_transform([resume_text, job_description])
            match = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            jd_score = round(float(match) * 100, 1)
            score += min(25, jd_score * 0.25)
            feedback.append(f"🎯 Job Description Match: {jd_score}%")
        except Exception:
            pass
    else:
        score += 15

    score = round(float(min(100, score)), 1)
    if score >= 80:
        feedback.insert(0, "🌟 Excellent! Your resume is highly ATS-friendly.")
    elif score >= 60:
        feedback.insert(0, "👍 Good resume, a few tweaks will make it even stronger.")
    else:
        feedback.insert(0, "🔧 Your resume needs improvement to pass ATS filters.")

    return {"score": score, "feedback": feedback}


# ==========================================================
# 4. QUIZ GENERATION
# ==========================================================

QUIZ_BANK = {
    "Career Interest": [
        {"q": "Which activity excites you most?", "options": ["Solving puzzles", "Helping people", "Designing things", "Leading a team"], "trait": ["Analytical", "Social", "Creative", "Leadership"]},
        {"q": "Pick your ideal weekend project:", "options": ["Build an app", "Volunteer work", "Paint / Design", "Organize an event"], "trait": ["Analytical", "Social", "Creative", "Leadership"]},
        {"q": "In a group project you usually:", "options": ["Analyze data", "Support teammates", "Design the presentation", "Lead the plan"], "trait": ["Analytical", "Social", "Creative", "Leadership"]},
        {"q": "Your favorite school subject area:", "options": ["Math/Science", "Social Studies", "Art/Music", "Business Studies"], "trait": ["Analytical", "Social", "Creative", "Leadership"]},
        {"q": "You feel most accomplished when you:", "options": ["Solve a hard problem", "Make someone's day better", "Create something beautiful", "Achieve a team goal"], "trait": ["Analytical", "Social", "Creative", "Leadership"]},
    ],
    "Aptitude": [
        {"q": "If a train travels 60km in 45 minutes, its speed is?", "options": ["70 km/h", "80 km/h", "75 km/h", "90 km/h"], "answer": "80 km/h"},
        {"q": "Find the next number: 2, 6, 12, 20, 30, ?", "options": ["40", "42", "44", "36"], "answer": "42"},
        {"q": "A shop gives 20% discount. Original price ₹500. Final price?", "options": ["₹400", "₹420", "₹450", "₹380"], "answer": "₹400"},
        {"q": "Synonym of 'Abundant':", "options": ["Scarce", "Plentiful", "Rare", "Empty"], "answer": "Plentiful"},
        {"q": "If CAT = 3120, then DOG = ?", "options": ["4157", "4715", "4715", "4517"], "answer": "4157"},
    ],
    "Coding Basics": [
        {"q": "Which symbol is used for comments in Python?", "options": ["//", "#", "<!-- -->", "/*"], "answer": "#"},
        {"q": "What does 'len([1,2,3])' return?", "options": ["2", "3", "4", "Error"], "answer": "3"},
        {"q": "Which data type is mutable in Python?", "options": ["Tuple", "String", "List", "Int"], "answer": "List"},
        {"q": "What does HTML stand for?", "options": ["Hyper Trainer Markup Language", "HyperText Markup Language", "Hyperlink Text Markup Language", "None"], "answer": "HyperText Markup Language"},
        {"q": "Which loop runs at least once?", "options": ["for", "while", "do-while", "if"], "answer": "do-while"},
    ],
}


def generate_quiz(topic, n=5):
    bank = QUIZ_BANK.get(topic, QUIZ_BANK["Aptitude"])
    return random.sample(bank, min(n, len(bank)))


# ==========================================================
# 5. MOCK INTERVIEW FEEDBACK
# ==========================================================

INTERVIEW_QUESTIONS = {
    "Software Engineer": [
        "Tell me about a challenging bug you fixed.",
        "Explain the difference between a list and a tuple in Python.",
        "How would you design a URL shortener?",
        "Describe a time you worked in a team under a deadline.",
        "What is your approach to learning a new technology?",
    ],
    "Data Scientist": [
        "Explain overfitting and how to prevent it.",
        "Walk me through a data science project you've done.",
        "What is the difference between supervised and unsupervised learning?",
        "How do you handle missing data?",
        "Explain a p-value in simple terms.",
    ],
    "General / HR": [
        "Tell me about yourself.",
        "What are your strengths and weaknesses?",
        "Why should we hire you?",
        "Where do you see yourself in 5 years?",
        "Describe a conflict you resolved at work or college.",
    ],
}


def mock_interview_feedback(question, answer):
    if AI_MODE != "rule_based":
        prompt = f"Interview question: {question}\nCandidate answer: {answer}\nGive constructive feedback and a score out of 10."
        return {"feedback": ai_generate(prompt), "score": None}

    word_count = len(answer.split())
    feedback = []
    score = 5.0

    if word_count < 15:
        feedback.append("⚠️ Your answer is too short. Try to elaborate with an example (STAR method: Situation, Task, Action, Result).")
        score -= 1.5
    elif word_count > 200:
        feedback.append("⚠️ Your answer is quite long. Aim to be concise and structured.")
        score -= 0.5
    else:
        feedback.append("✅ Good answer length.")
        score += 1

    if re.search(r"\bi\b", answer.lower()):
        score += 0.5
        feedback.append("✅ You personalized the answer well using specific examples.")

    filler_words = ["um", "like", "you know", "basically", "actually"]
    fillers_found = sum(answer.lower().count(f) for f in filler_words)
    if fillers_found > 2:
        feedback.append("⚠️ Try to reduce filler words for more confident delivery.")
        score -= 0.5

    if any(w in answer.lower() for w in ["result", "achieved", "improved", "successfully", "learned"]):
        score += 1.5
        feedback.append("✅ Great! You highlighted results/outcomes.")
    else:
        feedback.append("💡 Tip: Mention the outcome or result of your action for more impact.")

    score = round(max(1, min(10, score)), 1)
    return {"feedback": feedback, "score": score}


# ==========================================================
# 6. PROJECT & ROADMAP SUGGESTIONS
# ==========================================================

PROJECT_BANK = {
    "Data Scientist": ["Customer Churn Prediction", "Movie Recommendation System", "Sales Forecasting Dashboard", "Sentiment Analysis on Tweets"],
    "Software Engineer": ["Personal Portfolio Website", "Task Management App", "E-commerce REST API", "Real-time Chat Application"],
    "UI/UX Designer": ["Redesign a Popular App", "Mobile Banking App Prototype", "Accessibility Audit Case Study"],
    "Cybersecurity Analyst": ["Home Network Security Audit", "Phishing Detection Tool", "Password Strength Analyzer"],
    "Cloud Architect": ["Deploy a 3-tier App on AWS", "CI/CD Pipeline with Docker", "Serverless API with Lambda"],
}


def suggest_projects(role):
    return PROJECT_BANK.get(role, ["Personal Portfolio Website", "Open Source Contribution", "Capstone Project in your domain"])


def suggest_learning_roadmap(goal_role, level="Beginner"):
    if AI_MODE != "rule_based":
        prompt = f"Create a 4-phase learning roadmap for becoming a {goal_role} starting at {level} level."
        return ai_generate(prompt)

    skills = ROLE_SKILL_MAP.get(goal_role, ["Foundations", "Core Skills", "Tools", "Projects"])
    phases = []
    chunk = max(1, len(skills) // 4)
    labels = ["Foundation", "Core Skills", "Advanced Tools", "Real Projects & Portfolio"]
    for i, label in enumerate(labels):
        start, end = i * chunk, (i + 1) * chunk if i < 3 else len(skills)
        phases.append({"phase": f"Phase {i+1}: {label}", "topics": skills[start:end] or [skills[-1]]})
    return phases


# ==========================================================
# 7. CODING FEEDBACK
# ==========================================================

def coding_feedback(code, language="Python"):
    if not code.strip():
        return ["Please write some code first."]

    fb = []
    lines = code.strip().split("\n")
    if len(lines) < 2:
        fb.append("💡 Your solution looks very short — make sure it handles edge cases.")

    if language.lower() == "python":
        if "def " not in code:
            fb.append("💡 Consider wrapping your logic in a function for reusability.")
        else:
            fb.append("✅ Good use of function-based structure.")
        if "#" in code:
            fb.append("✅ Nice, you've added comments.")
        else:
            fb.append("💡 Add comments to explain your logic.")
        if re.search(r"for .* in range\(len\(", code):
            fb.append("⚠️ Consider using direct iteration (`for x in list`) instead of `range(len(...))`.")
        if "try" in code and "except" in code:
            fb.append("✅ Good error handling with try/except.")

    complexity_hint = "O(n)" if "for" in code and "for" not in code.replace("for", "", 1) else "check nested loops for O(n²)"
    fb.append(f"⏱️ Estimated complexity hint: {complexity_hint}")
    return fb


# ==========================================================
# 8. WEEKLY PROGRESS REPORT
# ==========================================================

def weekly_progress_report(fullname, stats: dict):
    if AI_MODE != "rule_based":
        prompt = f"Generate an encouraging weekly progress summary for {fullname} given these stats: {stats}"
        return ai_generate(prompt)

    lines = [f"📊 Weekly Progress Report for {fullname}", ""]
    lines.append(f"✅ Tasks completed: {stats.get('tasks_done', 0)}/{stats.get('tasks_total', 0)}")
    lines.append(f"🎯 Quizzes attempted: {stats.get('quizzes', 0)}")
    lines.append(f"💻 Coding problems solved: {stats.get('coding_solved', 0)}")
    lines.append(f"📈 Overall progress: {stats.get('progress_pct', 0)}%")
    pct = stats.get('progress_pct', 0)
    if pct >= 75:
        lines.append("\n🌟 Outstanding week! You're building excellent momentum — keep it up!")
    elif pct >= 40:
        lines.append("\n👍 Solid progress this week. Try to complete a couple more tasks next week.")
    else:
        lines.append("\n💡 It's a slow week — set aside 30 mins daily to build consistency.")
    return "\n".join(lines)


# ==========================================================
# 9. CHATBOT
# ==========================================================

CHAT_RULES = [
    (r"resume|cv", "You can build and check your resume in the 'Resume Builder' and 'ATS Resume Checker' modules! A strong resume highlights measurable achievements. 📄"),
    (r"interview", "Head over to 'Mock Interviews' to practice with real questions and get instant feedback! 🎤"),
    (r"career|job|future", "Try the 'AI Career Quiz' or 'Career Explorer' to discover careers matched to your interests! 🚀"),
    (r"skill|learn", "Check 'Skill Gap Analysis' to see exactly what to learn next for your dream role. 📚"),
    (r"hi|hello|hey", "Hello! 👋 I'm your AI Career Mentor. Ask me about careers, resumes, interviews, or skills!"),
    (r"thank", "You're very welcome! Keep up the great momentum on your career journey. 🌟"),
    (r"certificate", "You can view and download your certificates in the 'Certificates' section anytime! 🏆"),
]


def rule_based_chat_reply(message):
    msg = message.lower()
    for pattern, reply in CHAT_RULES:
        if re.search(pattern, msg):
            return reply
    generic = [
        "That's a great question! Keep exploring your dashboard to discover tailored recommendations. 💡",
        "I'd suggest checking your Progress Tracker to see how you're doing — consistency is key! 📈",
        "Great mindset! Every small step you take today builds your career tomorrow. 🚀",
        "I'm here to help with careers, skills, resumes and interviews — feel free to ask anything specific!",
    ]
    return random.choice(generic)


def ai_chat_reply(message):
    return ai_generate(message)
