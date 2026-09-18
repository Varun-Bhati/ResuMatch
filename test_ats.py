from backend.services.analyzer_service import analyze_resume
from backend.services.keyword_service import analyze_keywords
from backend.services.ats_service import analyze_ats


# ============================================================
# TEST RESUME
# ============================================================

resume_text = """
John Doe
john@example.com
+91 9876543210
linkedin.com/in/johndoe
github.com/johndoe

SUMMARY

Computer Science student interested in software development,
machine learning, data processing, and backend engineering.

EDUCATION

B.Tech Computer Science Engineering

EXPERIENCE

Software Development Intern

Worked with Python, Flask, SQL, Git, Docker and REST APIs.
Built backend services and processed structured data.

PROJECTS

Resume Analyzer

Built a resume analysis application using Python, Flask,
machine learning, Apache Spark, SQL and data processing.

SKILLS

Python
Flask
SQL
Docker
Git
Machine Learning
Apache Spark
REST APIs
Data Processing
"""


# ============================================================
# TEST JOB DESCRIPTION
# ============================================================

job_description = """
We are looking for a software developer with experience in
Python, Flask, SQL, Docker, Git, Machine Learning,
Apache Spark, Kubernetes, AWS, REST APIs, databases,
data pipelines, and cloud technologies.
"""


print("=" * 80)
print("RESUMATCH FULL PIPELINE DIAGNOSTIC")
print("=" * 80)


# ============================================================
# 1. ANALYZE RESUME
# ============================================================

resume_analysis = analyze_resume(
    resume_text
)

print()
print("=" * 80)
print("RESUME ANALYSIS")
print("=" * 80)

print()
print("Resume score:")
print(
    resume_analysis.get(
        "resume_score"
    )
)

resume_concepts = resume_analysis.get(
    "technical_concepts",
    []
)

print()
print("Resume concepts:")
print(
    len(resume_concepts)
)

for concept in resume_concepts:

    label = (
        concept.get("preferred_label")
        or
        concept.get("technology")
        or
        concept.get("element_name")
    )

    if label:
        print(
            f"  - {label}"
        )


# ============================================================
# 2. ANALYZE JOB DESCRIPTION
# ============================================================

job_analysis = analyze_resume(
    job_description
)

print()
print("=" * 80)
print("JOB ANALYSIS")
print("=" * 80)

job_concepts = job_analysis.get(
    "technical_concepts",
    []
)

print()
print("Job concepts:")
print(
    len(job_concepts)
)

for concept in job_concepts:

    label = (
        concept.get("preferred_label")
        or
        concept.get("technology")
        or
        concept.get("element_name")
    )

    if label:
        print(
            f"  - {label}"
        )


# ============================================================
# 3. KEYWORD ANALYSIS
# ============================================================

keyword_analysis = analyze_keywords(
    resume_analysis,
    job_analysis
)

print()
print("=" * 80)
print("KEYWORD ANALYSIS")
print("=" * 80)

print()
print("Keyword coverage:")
print(
    keyword_analysis.get(
        "keyword_coverage_percentage"
    )
)

print()
print("Matched keywords:")

for keyword in keyword_analysis.get(
    "matched_keywords",
    []
):

    print(
        f"  - {keyword}"
    )


print()
print("Related keywords:")

for keyword in keyword_analysis.get(
    "related_keywords",
    []
):

    print(
        f"  - "
        f"{keyword.get('resume_concept')}"
        f" -> "
        f"{keyword.get('job_keyword')}"
    )


print()
print("Missing keywords:")

for keyword in keyword_analysis.get(
    "missing_keywords",
    []
):

    print(
        f"  - {keyword}"
    )


# ============================================================
# 4. JOB-SPECIFIC ATS
# ============================================================

ats_analysis = analyze_ats(
    resume_text,
    keyword_analysis
)

print()
print("=" * 80)
print("ATS ANALYSIS")
print("=" * 80)

print()
print("ATS:")

print(
    ats_analysis.get(
        "ats_score"
    )
)

print()
print("ATS details:")

print(
    f"  Length score: "
    f"{ats_analysis.get('length_score')}"
)

print(
    f"  Contact score: "
    f"{ats_analysis.get('contact_score')}"
)

print(
    f"  Structure score: "
    f"{ats_analysis.get('structure_score')}"
)

print(
    f"  Formatting score: "
    f"{ats_analysis.get('formatting_score')}"
)

print(
    f"  Keyword score: "
    f"{ats_analysis.get('keyword_score')}"
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)