def analyze_skill_gap(match_result):
    """
    Create a clean skill-gap analysis from
    the resume-to-job matching result.
    """

    if not match_result:
        return {
            "skill_coverage_percentage": 0,
            "matched_skills": [],
            "related_skills": [],
            "missing_skills": [],
            "matched_count": 0,
            "related_count": 0,
            "missing_count": 0
        }

    matched = match_result.get(
        "matched",
        []
    )

    related = match_result.get(
        "related",
        []
    )

    missing = match_result.get(
        "missing",
        []
    )

    # --------------------------------
    # 1. Matched skills
    # --------------------------------

    matched_skills = []

    for item in matched:

        job_concept = item.get(
            "job_concept",
            {}
        )

        label = (
            job_concept.get("preferred_label")
            or
            job_concept.get("technology")
            or
            job_concept.get("element_name")
        )

        if label:
            matched_skills.append(label)

    # --------------------------------
    # 2. Related skills
    # --------------------------------

    related_skills = []

    for item in related:

        resume_concept = item.get(
            "resume_concept",
            {}
        )

        job_concept = item.get(
            "job_concept",
            {}
        )

        resume_label = (
            resume_concept.get("preferred_label")
            or
            resume_concept.get("technology")
            or
            resume_concept.get("element_name")
            or
            ""
        )

        job_label = (
            job_concept.get("preferred_label")
            or
            job_concept.get("technology")
            or
            job_concept.get("element_name")
            or
            ""
        )

        if job_label:

            related_skills.append({
                "resume_skill": resume_label,
                "job_skill": job_label
            })

    # --------------------------------
    # 3. Missing skills
    # --------------------------------

    missing_skills = []

    for concept in missing:

        label = (
            concept.get("preferred_label")
            or
            concept.get("technology")
            or
            concept.get("element_name")
        )

        if label:
            missing_skills.append(label)

    # --------------------------------
    # 4. Remove duplicate matched skills
    # --------------------------------

    matched_skills = list(
        dict.fromkeys(matched_skills)
    )

    # --------------------------------
    # 5. Remove duplicate related skills
    # --------------------------------

    unique_related_skills = []
    seen_related = set()

    for related_skill in related_skills:

        key = (
            related_skill["resume_skill"].lower(),
            related_skill["job_skill"].lower()
        )

        if key in seen_related:
            continue

        seen_related.add(key)

        unique_related_skills.append(
            related_skill
        )

    related_skills = unique_related_skills

    # --------------------------------
    # 6. Remove duplicate missing skills
    # --------------------------------

    missing_skills = list(
        dict.fromkeys(missing_skills)
    )

    # --------------------------------
    # 7. Calculate skill coverage
    # --------------------------------

    job_concept_count = match_result.get(
        "job_concept_count",
        0
    )

    matched_count = len(
        matched_skills
    )

    related_count = len(
        related_skills
    )

    if job_concept_count > 0:

        skill_coverage = round(
            (
                matched_count
                + (related_count * 0.5)
            )
            / job_concept_count
            * 100,
            2
        )

    else:

        skill_coverage = 0

    # --------------------------------
    # 8. Return skill-gap analysis
    # --------------------------------

    return {
        "skill_coverage_percentage":
            skill_coverage,

        "matched_skills":
            matched_skills,

        "related_skills":
            related_skills,

        "missing_skills":
            missing_skills,

        "matched_count":
            matched_count,

        "related_count":
            related_count,

        "missing_count":
            len(missing_skills)
    }