from __future__ import annotations

from flask import Flask, jsonify, render_template_string, request
import re
from typing import Dict, List, Tuple

app = Flask(__name__)

SKILL_PATTERNS: Dict[str, re.Pattern] = {
    "Python": re.compile(r"\bpython\b", re.I),
    "NumPy": re.compile(r"\bnumpy\b", re.I),
    "Pandas": re.compile(r"\bpandas\b", re.I),
    "SQL": re.compile(r"\bsql\b", re.I),
    "Machine Learning": re.compile(r"\bmachine learning\b|\bml\b", re.I),
    "Data Analysis": re.compile(r"\bdata analysis\b|\bdata analytics\b", re.I),
    "Excel": re.compile(r"\bexcel\b", re.I),
    "Communication": re.compile(r"\bcommunication\b|\bcollaborat(?:ion|ive)\b|\bteamwork\b", re.I),
}

SECTION_PATTERNS: Dict[str, re.Pattern] = {
    "Education": re.compile(r"\beducation\b", re.I),
    "Experience": re.compile(r"\bexperience\b", re.I),
    "Projects": re.compile(r"\bprojects\b|\bproject\b", re.I),
    "Skills": re.compile(r"\bskills\b|\bskill\b", re.I),
    "Certifications": re.compile(r"\bcertifications\b|\bcertificate\b", re.I),
    "Summary": re.compile(r"\bsummary\b|\bobjective\b", re.I),
}

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Resume Analyzer</title>
    <style>
        :root {
            font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color-scheme: dark;
            color: #e2e8f0;
            background: #090b14;
        }
        body {
            margin: 0;
            min-height: 100vh;
            background: radial-gradient(circle at top, rgba(56, 189, 248, 0.12), transparent 18%),
                        linear-gradient(180deg, #020617 0%, #090b14 100%);
            color: #e2e8f0;
        }
        .container {
            max-width: 960px;
            margin: 0 auto;
            padding: 2rem 1.5rem 3rem;
        }
        .card {
            background: rgba(15, 23, 42, 0.92);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 28px;
            padding: 1.75rem;
            backdrop-filter: blur(18px);
            box-shadow: 0 24px 56px rgba(0, 0, 0, 0.28);
        }
        h1, h2 {
            margin: 0 0 1rem;
            font-weight: 700;
        }
        p {
            margin: 0 0 1rem;
            color: #94a3b8;
            line-height: 1.75;
        }
        textarea {
            width: 100%;
            min-height: 220px;
            padding: 1rem;
            border-radius: 18px;
            border: 1px solid rgba(148, 163, 184, 0.16);
            background: rgba(15, 23, 42, 0.9);
            color: #e2e8f0;
            resize: vertical;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            font-size: 0.98rem;
        }
        button {
            border: none;
            border-radius: 16px;
            padding: 0.95rem 1.5rem;
            background: linear-gradient(135deg, #38bdf8, #6366f1);
            color: white;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        button:hover {
            transform: translateY(-1px);
            box-shadow: 0 16px 32px rgba(56, 189, 248, 0.28);
        }
        .result {
            margin-top: 1.75rem;
            display: grid;
            gap: 1rem;
        }
        .result-summary,
        .result-skill-list,
        .result-section {
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 22px;
            padding: 1.35rem;
        }
        .badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin-top: 0.75rem;
        }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.65rem 0.9rem;
            border-radius: 999px;
            background: rgba(56, 189, 248, 0.12);
            color: #cbd5e1;
            border: 1px solid rgba(56, 189, 248, 0.22);
            font-size: 0.95rem;
            font-weight: 600;
        }
        .skill-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 0.85rem;
        }
        .skill-box {
            padding: 0.85rem 1rem;
            border-radius: 18px;
            border: 1px solid rgba(148, 163, 184, 0.14);
            background: rgba(15, 23, 42, 0.98);
        }
        .skill-box.match {
            border-color: #22c55e;
            background: rgba(34, 197, 94, 0.08);
        }
        .skill-box.no-match {
            border-color: #ef4444;
            background: rgba(239, 68, 68, 0.1);
        }
        .recommendation {
            margin-top: 0.5rem;
            padding: 1rem;
            border-radius: 18px;
            background: rgba(63, 63, 70, 0.9);
            color: #f8fafc;
        }
        .status-pill {
            display: inline-flex;
            align-items: center;
            padding: 0.45rem 0.75rem;
            border-radius: 999px;
            font-weight: 700;
        }
        .status-pill.good { background: #16a34a; }
        .status-pill.okay { background: #f59e0b; }
        .status-pill.needs { background: #dc2626; }
        @media (max-width: 720px) {
            .container { padding: 1.25rem; }
            .hero { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>Resume Analyzer</h1>
            <p>Paste resume text below and get a quick skill match score, missing skills, and section coverage feedback.</p>
            <form method="post">
                <textarea name="resume_text" placeholder="Paste your resume text here...">{{ resume_text }}</textarea>
                <button type="submit">Analyze Resume</button>
            </form>
        </div>

        {% if result %}
            <div class="result">
                <div class="result-summary card">
                    <h2>Summary</h2>
                    <p><strong>Score:</strong> {{ result.percentage }}%</p>
                    <p><strong>Matched:</strong> {{ result.matched }} / {{ result.total }} required skills</p>
                    <p><strong>Experience detected:</strong> {{ result.experience_years }} years</p>
                    <div class="badges">
                        {% for section in result.sections %}
                            <span class="badge">{{ section }}</span>
                        {% endfor %}
                    </div>
                    <div class="recommendation">
                        <strong>Recommendation:</strong> {{ result.recommendation }}
                    </div>
                </div>

                <div class="result-section card">
                    <h2>Skill Match</h2>
                    <div class="skill-grid">
                        {% for skill in result.skills %}
                            <div class="skill-box {{ 'match' if skill[1] else 'no-match' }}">
                                {{ skill[0] }}
                            </div>
                        {% endfor %}
                    </div>
                </div>

                <div class="result-section card">
                    <h2>Missing Skills</h2>
                    {% if result.missing_skills %}
                        <div class="badges">
                            {% for missing in result.missing_skills %}
                                <span class="badge">{{ missing }}</span>
                            {% endfor %}
                        </div>
                    {% else %}
                        <p>Excellent! All required skills are present in the resume.</p>
                    {% endif %}
                </div>

                {% if result.missing_sections %}
                    <div class="result-section card">
                        <h2>Suggested Sections</h2>
                        <div class="badges">
                            {% for section in result.missing_sections %}
                                <span class="badge">{{ section }}</span>
                            {% endfor %}
                        </div>
                    </div>
                {% endif %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""


def normalize_text(text: str) -> str:
    return text.strip()


def find_skills(text: str) -> List[Tuple[str, bool]]:
    return [(skill, bool(pattern.search(text))) for skill, pattern in SKILL_PATTERNS.items()]


def find_sections(text: str) -> List[str]:
    return [name for name, pattern in SECTION_PATTERNS.items() if pattern.search(text)]


def extract_experience_years(text: str) -> int:
    normalized = re.sub(r"[–—]", "-", text)
    ranges = re.findall(r"(\d+)\s*(?:\+|\-|to)\s*(\d+)\s*(?:years?|yrs?)", normalized, re.I)
    singles = re.findall(r"(\d+)\s*\+?\s*(?:years?|yrs?)", normalized, re.I)
    values = [int(value) for _, value in ranges] + [int(value) for value in singles]
    return max(values) if values else 0


def generate_recommendation(score: float, detected_sections: List[str]) -> str:
    if score >= 80:
        base = "Your resume demonstrates strong skill coverage."
        detail = "Keep your project descriptions clear and tailored to the role."
    elif score >= 60:
        base = "Good skill coverage, but there is still room to improve."
        detail = "Add missing keywords and make sure your experience is highlighted."  
    elif score >= 40:
        base = "Your resume includes some key skills, but it needs more polish."
        detail = "Include more examples of tools, projects, and measurable results."
    else:
        base = "The resume is missing several required skills."
        detail = "Use a dedicated skills section and emphasize relevant experience."

    if "Skills" not in detected_sections:
        detail += " Add a dedicated Skills section to improve readability."

    if "Experience" not in detected_sections:
        detail += " Add an Experience section with role details and achievements."

    return f"{base} {detail}"


def build_result(text: str) -> Dict[str, object]:
    normalized = normalize_text(text)
    skills = find_skills(normalized)
    matched = sum(1 for _, found in skills if found)
    total = len(SKILL_PATTERNS)
    percentage = round((matched / total) * 100, 2) if total else 0.0
    detected_sections = find_sections(normalized)
    missing_skills = [skill for skill, found in skills if not found]
    missing_sections = [name for name in SECTION_PATTERNS if name not in detected_sections]

    return {
        "skills": skills,
        "matched": matched,
        "total": total,
        "percentage": percentage,
        "missing_skills": missing_skills,
        "experience_years": extract_experience_years(normalized),
        "sections": detected_sections or ["No section headings found"],
        "missing_sections": missing_sections,
        "recommendation": generate_recommendation(percentage, detected_sections),
    }


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    resume_text = ""
    result = None

    if request.method == "POST":
        resume_text = request.form.get("resume_text", "")
        result = build_result(resume_text)

    return render_template_string(PAGE_TEMPLATE, resume_text=resume_text, result=result)


@app.route("/api/analyze", methods=["POST"])
def analyze_resume_api() -> Any:
    payload = request.get_json(silent=True) or {}
    resume_text = payload.get("resume_text", "")
    return jsonify(build_result(resume_text))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)


def generate_recommendation(score: float, sections: list[str]) -> str:
    if score >= 80:
        base = "Your resume already matches the required skill set strongly."
        detail = "Focus on clear project and experience descriptions to keep it strong."
    elif score >= 60:
        base = "Good skill coverage, but there is room to improve."
        detail = "Add any missing technical terms and stronger section headings."
    elif score >= 40:
        base = "Your resume has some key skills, but it needs more polish."
        detail = "Include more examples of relevant tools and projects."
    else:
        base = "The resume is missing several required skills."
        detail = "Highlight technical experience and update the skills section."

    if "Skills" not in sections:
        detail += " Make sure the resume includes a dedicated Skills section."

    return f"{base} {detail}"


@app.route("/", methods=["GET", "POST"])
def index():
    resume_text = ""
    result = None

    if request.method == "POST":
        resume_text = request.form.get("resume_text", "")
        result = analyze_resume(resume_text)

    return render_template_string(PAGE_TEMPLATE, resume_text=resume_text, result=result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)