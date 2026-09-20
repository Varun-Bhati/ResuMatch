import re


from backend.services.section_detector import detect_sections


def detect_resume_sections(text):
    """
    Use the centralized ResuMatch section detector.

    This keeps ATS section detection consistent
    with the main resume analysis pipeline.
    """

    return detect_sections(text)


def detect_contact_information(text):
    """
    Detect common professional contact information.
    """

    email_found = bool(
        re.search(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            text
        )
    )

    phone_found = bool(
        re.search(
            r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)",
            text
        )
    )

    linkedin_found = bool(
        re.search(
            r"(?:https?://)?(?:www\.)?linkedin\.com/",
            text,
            re.IGNORECASE
        )
    )

    github_found = bool(
        re.search(
            r"(?:https?://)?(?:www\.)?github\.com/",
            text,
            re.IGNORECASE
        )
    )

    return {
        "email_found": email_found,
        "phone_found": phone_found,
        "linkedin_found": linkedin_found,
        "github_found": github_found,
    }


def calculate_length_score(word_count):
    """
    Calculate the ATS contribution from resume length.

    Maximum: 15

    ATS should not require an exact resume length.
    It should mainly flag resumes that are unusually short
    or excessively long.
    """

    if 300 <= word_count <= 900:
        return 15

    if 200 <= word_count < 300:
        return 12

    if 901 <= word_count <= 1100:
        return 12

    if 150 <= word_count < 200:
        return 9

    if 1101 <= word_count <= 1200:
        return 9

    if 100 <= word_count < 150:
        return 5

    if 1201 <= word_count <= 1400:
        return 5

    return 0


def calculate_contact_score(contact):
    """
    Calculate ATS contact information score.

    Maximum: 20
    """

    score = 0

    if contact["email_found"]:
        score += 7

    if contact["phone_found"]:
        score += 7

    if contact["linkedin_found"]:
        score += 3

    if contact["github_found"]:
        score += 3

    return score


def calculate_structure_score(sections):
    """
    Calculate ATS-friendly resume structure.

    Maximum: 45
    """

    score = 0

    # Core sections
    if sections["experience"]:
        score += 12

    if sections["education"]:
        score += 10

    if sections["skills"]:
        score += 10

    if sections["projects"]:
        score += 8

    # Optional but useful
    if sections["summary"]:
        score += 3

    if sections["certifications"]:
        score += 2

    return score


def calculate_formatting_score(text):
    """
    Detect basic text-level formatting signals that can
    affect ATS readability.

    Maximum: 20

    This does not attempt to inspect the original visual PDF
    layout. It only evaluates the extracted text.
    """

    score = 20
    issues = []

    # ---------------------------------------------------------
    # Repeated punctuation / extraction artifacts
    # ---------------------------------------------------------

    if re.search(
        r"[!?]{2,}|\.{4,}|,{2,}",
        text
    ):
        score -= 4
        issues.append(
            "Inconsistent punctuation patterns detected."
        )

    # ---------------------------------------------------------
    # Excessive unusual symbols
    # ---------------------------------------------------------

    # Allow common resume punctuation, including Unicode
    # punctuation that can legitimately appear in resumes
    # or be produced by OCR.
    symbol_matches = re.findall(
        r"[^\w\s.,:;!?@#$%&()+/#'.\[\]{}|_\\–—•·“”‘’\-]",
        text
    )

    if len(symbol_matches) > 10:
        score -= 4
        issues.append(
            "A high number of unusual characters were detected in the extracted text."
        )

    # ---------------------------------------------------------
    # Extremely long lines
    # ---------------------------------------------------------

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    long_lines = [
        line
        for line in lines
        if len(line) > 180
    ]

    if len(long_lines) >= 3:
        score -= 4
        issues.append(
            "Several unusually long text lines were detected."
        )

    # ---------------------------------------------------------
    # Excessive blank-line fragmentation
    # ---------------------------------------------------------

    blank_line_count = len(
        re.findall(
            r"\n\s*\n\s*\n",
            text
        )
    )

    if blank_line_count >= 5:
        score -= 3
        issues.append(
            "The extracted resume text contains excessive blank-line fragmentation."
        )

    # ---------------------------------------------------------
    # Repeated headings
    # ---------------------------------------------------------

    heading_occurrences = {}

    common_headings = [
        "summary",
        "experience",
        "education",
        "skills",
        "projects",
        "certifications",
    ]

    for heading in common_headings:

        count = len(
            re.findall(
                rf"^\s*{re.escape(heading)}\s*$",
                text,
                re.IGNORECASE | re.MULTILINE
            )
        )

        heading_occurrences[heading] = count

    if any(
        count > 1
        for count in heading_occurrences.values()
    ):
        score -= 3
        issues.append(
            "Repeated standard section headings were detected."
        )

    return max(score, 0), issues


def calculate_keyword_component(keyword_analysis):
    """
    Calculate the job-specific keyword component.

    Maximum: 30

    This component is only used when a job description
    has been supplied.
    """

    if not keyword_analysis:
        return {
            "score": None,
            "coverage": None,
            "matched_keywords": [],
            "related_keywords": [],
            "missing_keywords": [],
        }

    coverage = float(
        keyword_analysis.get(
            "keyword_coverage_percentage",
            0.0
        )
    )

    matched_keywords = keyword_analysis.get(
        "matched_keywords",
        []
    )

    related_keywords = keyword_analysis.get(
        "related_keywords",
        []
    )

    missing_keywords = keyword_analysis.get(
        "missing_keywords",
        []
    )

    keyword_score = round(
        coverage * 0.30,
        2
    )

    return {
        "score": keyword_score,
        "coverage": coverage,
        "matched_keywords": matched_keywords,
        "related_keywords": related_keywords,
        "missing_keywords": missing_keywords,
    }


def calculate_standalone_ats_score(
    length_score,
    contact_score,
    structure_score,
    formatting_score
):
    """
    Calculate ATS score when no job description exists.

    Maximum: 100

    Components:

    Length       15
    Contact      20
    Structure    45
    Formatting   20
    """

    return round(
        min(
            length_score
            + contact_score
            + structure_score
            + formatting_score,
            100
        ),
        2
    )


def calculate_job_ats_score(
    length_score,
    contact_score,
    structure_score,
    formatting_score,
    keyword_score
):
    """
    Calculate ATS score when a job description exists.

    Maximum: 100

    Job-specific keyword coverage receives a dedicated
    30-point component.

    The remaining 70 points come from general ATS signals.
    """

    general_score = (
        length_score
        + contact_score
        + structure_score
        + formatting_score
    )

    # General ATS signals have a maximum of 100.
    # Normalize them to a 70-point component.
    general_weighted_score = (
        general_score * 0.70
    )

    ats_score = (
        general_weighted_score
        + keyword_score
    )

    return round(
        min(ats_score, 100),
        2
    )


def analyze_ats(
    text,
    keyword_analysis=None
):
    """
    Perform ATS compatibility analysis on resume text.

    The analysis evaluates:

    1. Resume length
    2. Contact information
    3. Standard resume structure
    4. Extracted-text formatting signals
    5. Job-specific keyword coverage when available

    When no job description is supplied, the ATS score
    evaluates general ATS readiness.

    When a job description is supplied, keyword coverage
    contributes up to 30 points.
    """

    if not text or not text.strip():
        return {
            "error": "No resume text was provided."
        }

    text = text.strip()

    # ---------------------------------------------------------
    # 1. Word count
    # ---------------------------------------------------------

    words = text.split()
    word_count = len(words)

    # ---------------------------------------------------------
    # 2. Resume sections
    # ---------------------------------------------------------

    detected_sections = detect_resume_sections(
        text
    )

    # ---------------------------------------------------------
    # 3. Contact information
    # ---------------------------------------------------------

    contact = detect_contact_information(
        text
    )

    # ---------------------------------------------------------
    # 4. Individual ATS components
    # ---------------------------------------------------------

    length_score = calculate_length_score(
        word_count
    )

    contact_score = calculate_contact_score(
        contact
    )

    structure_score = calculate_structure_score(
        detected_sections
    )

    formatting_score, formatting_issues = (
        calculate_formatting_score(text)
    )

    # ---------------------------------------------------------
    # 5. Keyword component
    # ---------------------------------------------------------

    keyword_result = calculate_keyword_component(
        keyword_analysis
    )

    keyword_score = keyword_result["score"]

    # ---------------------------------------------------------
    # 6. Final ATS score
    # ---------------------------------------------------------

    if keyword_analysis:

        ats_score = calculate_job_ats_score(
            length_score,
            contact_score,
            structure_score,
            formatting_score,
            keyword_score
        )

    else:

        ats_score = calculate_standalone_ats_score(
            length_score,
            contact_score,
            structure_score,
            formatting_score
        )

    # ---------------------------------------------------------
    # 7. Generate ATS issues
    # ---------------------------------------------------------

    issues = []

    if not contact["email_found"]:
        issues.append(
            "Email address not detected."
        )

    if not contact["phone_found"]:
        issues.append(
            "Phone number not detected."
        )

    if (
        not contact["linkedin_found"]
        and not contact["github_found"]
    ):
        issues.append(
            "No LinkedIn or GitHub profile link detected."
        )

    if not detected_sections["experience"]:
        issues.append(
            "Experience section not detected."
        )

    if not detected_sections["education"]:
        issues.append(
            "Education section not detected."
        )

    if not detected_sections["skills"]:
        issues.append(
            "Skills section not detected."
        )

    if not detected_sections["projects"]:
        issues.append(
            "Projects section not detected."
        )

    if word_count < 100:
        issues.append(
            "Resume contains very little text and may not provide enough information for reliable ATS matching."
        )

    elif word_count < 150:
        issues.append(
            "Resume is relatively short and may benefit from more relevant detail."
        )

    if word_count > 1200:
        issues.append(
            "Resume may contain more content than necessary for ATS-focused applications."
        )

    issues.extend(
        formatting_issues
    )

    if (
        keyword_analysis
        and keyword_result["missing_keywords"]
    ):
        issues.append(
            f"{len(keyword_result['missing_keywords'])} "
            "job-specific keyword(s) missing from the resume."
        )

    # ---------------------------------------------------------
    # 8. Score breakdown
    # ---------------------------------------------------------

    if keyword_analysis:

        score_breakdown = [
            {
                "category": "Resume length",
                "score": length_score,
                "max_score": 15,
                "description": (
                    "Evaluates whether the resume contains "
                    "a reasonable amount of text."
                ),
            },
            {
                "category": "Contact information",
                "score": contact_score,
                "max_score": 20,
                "description": (
                    "Checks for email, phone, LinkedIn, "
                    "and GitHub contact signals."
                ),
            },
            {
                "category": "Resume structure",
                "score": structure_score,
                "max_score": 45,
                "description": (
                    "Checks for standard resume sections "
                    "that ATS systems can identify."
                ),
            },
            {
                "category": "Text formatting",
                "score": formatting_score,
                "max_score": 20,
                "description": (
                    "Evaluates extracted-text signals that "
                    "may interfere with machine readability."
                ),
            },
            {
                "category": "Job keyword coverage",
                "score": keyword_score,
                "max_score": 30,
                "description": (
                    "Measures how well recognized resume "
                    "concepts cover the supplied job description."
                ),
            },
        ]

    else:

        score_breakdown = [
            {
                "category": "Resume length",
                "score": length_score,
                "max_score": 15,
                "description": (
                    "Evaluates whether the resume contains "
                    "a reasonable amount of text."
                ),
            },
            {
                "category": "Contact information",
                "score": contact_score,
                "max_score": 20,
                "description": (
                    "Checks for email, phone, LinkedIn, "
                    "and GitHub contact signals."
                ),
            },
            {
                "category": "Resume structure",
                "score": structure_score,
                "max_score": 45,
                "description": (
                    "Checks for standard resume sections "
                    "that ATS systems can identify."
                ),
            },
            {
                "category": "Text formatting",
                "score": formatting_score,
                "max_score": 20,
                "description": (
                    "Evaluates extracted-text signals that "
                    "may interfere with machine readability."
                ),
            },
        ]

    # ---------------------------------------------------------
    # 9. Final result
    # ---------------------------------------------------------

    return {
        "ats_score": ats_score,

        "structural_score": structure_score,

        "keyword_score": (
            keyword_score
            if keyword_score is not None
            else 0.0
        ),

        "keyword_coverage_percentage": (
            keyword_result["coverage"]
            if keyword_result["coverage"] is not None
            else 0.0
        ),

        "matched_keywords": (
            keyword_result["matched_keywords"]
        ),

        "related_keywords": (
            keyword_result["related_keywords"]
        ),

        "missing_keywords": (
            keyword_result["missing_keywords"]
        ),

        "word_count": word_count,

        "email_found": contact["email_found"],

        "phone_found": contact["phone_found"],

        "linkedin_found": contact["linkedin_found"],

        "github_found": contact["github_found"],

        "sections": detected_sections,

        "score_breakdown": score_breakdown,

        "issues": issues,

        "issue_count": len(issues),
    }