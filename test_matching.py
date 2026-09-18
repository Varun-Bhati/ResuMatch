from backend.services.analyzer_service import analyze_resume
from backend.services.matching_service import match_resume_to_job


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
Git
Machine Learning
Apache Spark
REST APIs
Data Processing
"""


job_description = """
We are looking for a software developer with experience in
Python, Flask, SQL, Docker, Git, Machine Learning,
Apache Spark, Kubernetes, AWS, REST APIs, databases,
data pipelines, and cloud technologies.
"""


print("=" * 80)
print("RESUMATCH RESUME TO JOB MATCHING DIAGNOSTIC")
print("=" * 80)


resume_analysis = analyze_resume(
    resume_text
)


job_analysis = analyze_resume(
    job_description
)


resume_concepts = resume_analysis.get(
    "technical_concepts",
    []
)


job_concepts = job_analysis.get(
    "technical_concepts",
    []
)


print()
print("=" * 80)
print("CONCEPT COUNTS")
print("=" * 80)

print()
print("Resume concepts:")
print(len(resume_concepts))

print()
print("Job concepts:")
print(len(job_concepts))


matching_result = match_resume_to_job(
    resume_concepts,
    job_concepts
)


print()
print("=" * 80)
print("MATCH RESULT")
print("=" * 80)


print()
print("Match percentage:")
print(
    matching_result.get(
        "match_percentage"
    )
)


print()
print("Matched count:")
print(
    matching_result.get(
        "matched_count"
    )
)


print()
print("Related count:")
print(
    matching_result.get(
        "related_count"
    )
)


print()
print("Missing count:")
print(
    matching_result.get(
        "missing_count"
    )
)


print()
print("Matched concepts:")

for item in matching_result.get(
    "matched",
    []
):

    resume_concept = item.get(
        "resume_concept",
        {}
    )

    job_concept = item.get(
        "job_concept",
        {}
    )

    resume_label = (
        resume_concept.get(
            "preferred_label"
        )
        or
        resume_concept.get(
            "technology"
        )
        or
        resume_concept.get(
            "element_name"
        )
    )

    job_label = (
        job_concept.get(
            "preferred_label"
        )
        or
        job_concept.get(
            "technology"
        )
        or
        job_concept.get(
            "element_name"
        )
    )

    print(
        f"  - {resume_label}"
        f" -> "
        f"{job_label}"
    )


print()
print("Related concepts:")

for item in matching_result.get(
    "related",
    []
):

    resume_concept = item.get(
        "resume_concept",
        {}
    )

    job_concept = item.get(
        "job_concept",
        {}
    )

    resume_label = (
        resume_concept.get(
            "preferred_label"
        )
        or
        resume_concept.get(
            "technology"
        )
        or
        resume_concept.get(
            "element_name"
        )
    )

    job_label = (
        job_concept.get(
            "preferred_label"
        )
        or
        job_concept.get(
            "technology"
        )
        or
        job_concept.get(
            "element_name"
        )
    )

    print(
        f"  - {resume_label}"
        f" -> "
        f"{job_label}"
        f" "
        f"({item.get('match_type')})"
    )


print()
print("Missing concepts:")

for concept in matching_result.get(
    "missing",
    []
):

    label = (
        concept.get(
            "preferred_label"
        )
        or
        concept.get(
            "technology"
        )
        or
        concept.get(
            "element_name"
        )
    )

    print(
        f"  - {label}"
    )


print()
print("=" * 80)
print("MATCHING DIAGNOSTIC COMPLETE")
print("=" * 80)