def analyze_resume_quality(
    word_count,
    sections,
    skills,
    knowledge,
    technologies
):
    """
    Identify resume formatting and content quality issues
    from information already extracted by ResuMatch.

    No hard-coded skill list is used.

    The checks are based on:
    - resume length
    - resume structure
    - recognized skills
    - recognized knowledge areas
    - recognized technologies
    """

    issues = []

    important_sections = [
        "summary",
        "education",
        "experience",
        "projects",
        "skills"
    ]

    detected_sections = [
        section
        for section in important_sections
        if sections.get(section)
    ]

    missing_sections = [
        section
        for section in important_sections
        if not sections.get(section)
    ]

    # --------------------------------
    # Content length
    # --------------------------------

    if word_count < 100:

        issues.append(
            "The resume contains very little content and may need substantially more detail."
        )

    elif word_count < 150:

        issues.append(
            "The resume is relatively short and may need more detail about experience, projects, or qualifications."
        )

    elif word_count > 1200:

        issues.append(
            "The resume contains a large amount of content and may benefit from tighter, more relevant wording."
        )

    # --------------------------------
    # Resume structure
    # --------------------------------

    if len(detected_sections) <= 2:

        issues.append(
            "The resume has limited section structure. Consider organizing the content into clear standard resume sections."
        )

    elif missing_sections:

        issues.append(
            "The resume structure is missing one or more standard sections."
        )

    # --------------------------------
    # Skills and technical content
    # --------------------------------

    has_recognized_skills = len(skills) > 0

    has_recognized_knowledge = len(knowledge) > 0

    has_recognized_technologies = len(technologies) > 0

    has_recognized_technical_content = (
        has_recognized_skills
        or has_recognized_knowledge
        or has_recognized_technologies
    )

    # No technical or professional concepts
    # were recognized at all.
    if not has_recognized_technical_content:

        issues.append(
            "Very little technical or professional content was recognized. Make relevant skills, tools, and technologies explicit."
        )

    # Technical concepts were recognized, but
    # there is no dedicated Skills section.
    elif not sections.get("skills"):

        issues.append(
            "Recognized technical content was found, but a dedicated skills section was not detected."
        )

    # --------------------------------
    # Knowledge coverage
    # --------------------------------

    # Only flag missing knowledge when there are
    # no recognized skills to provide technical
    # evidence.
    if (
        not has_recognized_knowledge
        and not has_recognized_skills
        and has_recognized_technologies
    ):

        issues.append(
            "No recognized knowledge areas were detected. Consider describing relevant technical or domain knowledge where it supports your qualifications."
        )

    # --------------------------------
    # Technology coverage
    # --------------------------------

    # Only flag missing technologies when there
    # are no recognized skills or knowledge areas.
    if (
        not has_recognized_technologies
        and not has_recognized_skills
        and not has_recognized_knowledge
    ):

        issues.append(
            "No software technologies or technical tools were detected. Mention tools or technologies you have actually used where relevant."
        )

    # --------------------------------
    # Overall result
    # --------------------------------

    if not issues:

        issues.append(
            "No major content or structural issues were detected from the available resume analysis signals."
        )

    return issues