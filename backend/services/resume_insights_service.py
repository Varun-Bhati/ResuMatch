def analyze_resume_insights(
    word_count,
    sections,
    skills,
    knowledge,
    technologies
):
    """
    Generate resume strengths and weaknesses from the
    information already extracted by ResuMatch.

    The analysis considers:
    - Resume length
    - Resume structure
    - Recognized ESCO skills
    - Recognized ESCO knowledge
    - Recognized O*NET technologies

    No hard-coded skill list is used.
    """

    strengths = []
    weaknesses = []

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

    # ---------------------------------------------------------
    # Technical concept counts
    # ---------------------------------------------------------

    technical_concept_count = (
        len(skills)
        + len(knowledge)
        + len(technologies)
    )

    # ---------------------------------------------------------
    # Resume length
    # ---------------------------------------------------------

    if word_count >= 250:
        strengths.append(
            "The resume contains a reasonable amount of content."
        )

    elif word_count < 150:
        weaknesses.append(
            "The resume appears too short and may need more detail."
        )

    # ---------------------------------------------------------
    # Resume structure
    # ---------------------------------------------------------

    if len(detected_sections) >= 4:
        strengths.append(
            "The resume contains most of the important resume sections."
        )

    elif len(detected_sections) >= 3:
        strengths.append(
            "The resume has a basic resume structure with several important sections."
        )

    else:
        weaknesses.append(
            "The resume has limited section structure."
        )

    if missing_sections:
        formatted_sections = ", ".join(
            section.capitalize()
            for section in missing_sections
        )

        weaknesses.append(
            f"Missing important section(s): {formatted_sections}."
        )

    # ---------------------------------------------------------
    # Recognized technical profile
    # ---------------------------------------------------------

    if technical_concept_count >= 6:
        strengths.append(
            "The resume demonstrates a broad range of recognized technical concepts."
        )

    elif technical_concept_count >= 3:
        strengths.append(
            "The resume demonstrates several recognized technical concepts."
        )

    elif technical_concept_count > 0:
        strengths.append(
            "The resume contains some recognizable technical concepts."
        )

    else:
        weaknesses.append(
            "No recognizable technical concepts were detected."
        )

    # ---------------------------------------------------------
    # ESCO knowledge
    # ---------------------------------------------------------

    if len(knowledge) >= 4:
        strengths.append(
            "The resume demonstrates a range of relevant knowledge areas."
        )

    # ---------------------------------------------------------
    # Technologies
    # ---------------------------------------------------------

    if len(technologies) >= 3:
        strengths.append(
            "Several software technologies or technical tools are identified."
        )

    elif len(technologies) == 1 or len(technologies) == 2:
        strengths.append(
            "Some software technologies or technical tools are identified."
        )

    elif len(technologies) == 0:
        weaknesses.append(
            "No software technologies or technical tools were detected."
        )

    # ---------------------------------------------------------
    # Explicit skills section
    # ---------------------------------------------------------

    if sections.get("skills") and technical_concept_count > 0:
        strengths.append(
            "A dedicated skills section is present and contains recognizable technical content."
        )

    elif not sections.get("skills"):
        weaknesses.append(
            "A dedicated skills section is missing."
        )

    # ---------------------------------------------------------
    # Return result
    # ---------------------------------------------------------

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "missing_sections": missing_sections
    }