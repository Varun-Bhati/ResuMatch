import re


SECTION_PATTERNS = {

    "summary": [
        r"\bsummary\b",
        r"\bprofessional summary\b",
        r"\bcareer summary\b",
        r"\bprofile\b",
        r"\bobjective\b",
        r"\bcareer objective\b",
    ],

    "education": [
        r"\beducation\b",
        r"\bacademic background\b",
        r"\bacademic qualification\b",
        r"\bqualifications\b",
    ],

    "experience": [
        r"\bexperience\b",
        r"\bwork experience\b",
        r"\bprofessional experience\b",
        r"\bemployment\b",
        r"\bwork history\b",
    ],

    "projects": [
        r"\bproject\b",
        r"\bprojects\b",
        r"\bpersonal projects\b",
        r"\bacademic projects\b",
        r"\bproject experience\b",
    ],

    "skills": [
        r"\bskills\b",
        r"\btechnical skills\b",
        r"\bcore skills\b",
        r"\btechnical expertise\b",
        r"\btechnologies\b",
    ],

    "certifications": [
        r"\bcertifications\b",
        r"\bcertificates\b",
        r"\bprofessional certifications\b",
    ],
}


def detect_sections(text):

    """
    Detect important resume sections from extracted text.
    """

    if not text:
        return {}

    detected_sections = {}

    for section, patterns in SECTION_PATTERNS.items():

        detected_sections[section] = any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in patterns
        )

    return detected_sections