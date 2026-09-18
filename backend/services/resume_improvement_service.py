def generate_resume_improvement_suggestions(
    word_count,
    sections,
    skills,
    knowledge,
    technologies
):
    """
    Generate actionable resume improvement suggestions
    from the information already extracted by ResuMatch.

    No hard-coded skill list is used.

    Suggestions are based on:
    - resume structure
    - content length
    - recognized skills
    - recognized knowledge areas
    - recognized technologies
    """

    suggestions = []

    important_sections = [
        "summary",
        "education",
        "experience",
        "projects",
        "skills"
    ]

    missing_sections = [
        section
        for section in important_sections
        if not sections.get(section)
    ]

    # --------------------------------
    # Content length
    # --------------------------------

    if word_count < 150:

        suggestions.append(
            "Add more relevant detail to your resume so your experience, projects, and skills are clearly described."
        )

    elif word_count > 1200:

        suggestions.append(
            "Consider reducing unnecessary content and keeping the resume focused on the most relevant experience and skills."
        )

    # --------------------------------
    # Missing sections
    # --------------------------------

    if missing_sections:

        formatted_sections = ", ".join(
            section.capitalize()
            for section in missing_sections
        )

        suggestions.append(
            f"Consider adding the missing resume section(s): {formatted_sections}."
        )

    # --------------------------------
    # Technical content
    # --------------------------------

    has_recognized_skills = len(skills) > 0

    has_recognized_knowledge = len(knowledge) > 0

    has_recognized_technologies = len(technologies) > 0

    has_recognized_technical_content = (
        has_recognized_skills
        or has_recognized_knowledge
        or has_recognized_technologies
    )

    # --------------------------------
    # Skills section
    # --------------------------------

    if not sections.get("skills"):

        if has_recognized_technical_content:

            suggestions.append(
                "Consider adding a dedicated Skills section to make your recognized technical abilities easier to identify."
            )

        else:

            suggestions.append(
                "Add a dedicated Skills section and make your relevant skills explicit so they can be recognized by resume analysis and ATS systems."
            )

    elif not has_recognized_technical_content:

        suggestions.append(
            "Make your relevant skills, tools, and technical knowledge more explicit so they can be recognized by resume analysis and ATS systems."
        )

    elif has_recognized_skills and len(skills) < 2:

        suggestions.append(
            "Consider making more of your relevant skills explicit in the resume."
        )

    # --------------------------------
    # Knowledge areas
    # --------------------------------

    if not has_recognized_knowledge:

        suggestions.append(
            "Add relevant knowledge areas where they strengthen your qualifications for the roles you are targeting."
        )

    # --------------------------------
    # Technologies
    # --------------------------------

    if not has_recognized_technologies:

        suggestions.append(
            "Mention the software, tools, frameworks, or technologies you have actually used in your projects or experience."
        )

    # --------------------------------
    # Final result
    # --------------------------------

    if not suggestions:

        suggestions.append(
            "Your resume has a solid basic structure. Continue tailoring the content to the specific roles you apply for."
        )

    return suggestions