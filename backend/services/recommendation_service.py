def analyze_recommendations(skill_gap):
    """
    Generate recommendations from the detected skill gaps.

    Recommendations are based on concepts already detected
    by ESCO and O*NET. No manually maintained skill list.
    """

    if not skill_gap:
        return {
            "recommendations": [],
            "recommendation_count": 0
        }

    missing_skills = skill_gap.get(
        "missing_skills",
        []
    )

    related_skills = skill_gap.get(
        "related_skills",
        []
    )

    recommendations = []

    # --------------------------------
    # 1. Recommendations for missing skills
    # --------------------------------

    for skill in missing_skills:

        if isinstance(skill, dict):

            label = (
                skill.get("preferred_label")
                or skill.get("technology")
                or skill.get("element_name")
                or skill.get("matched_term")
                or ""
            )

        else:
            label = str(skill)

        if not label:
            continue

        recommendations.append({
            "type": "skill_gap",
            "skill": label,
            "message": (
                f"Consider developing your skills in {label} "
                "because it appears in the target job requirements."
            )
        })

    # --------------------------------
    # 2. Recommendations for related skills
    # --------------------------------

    for related in related_skills:

        if not isinstance(related, dict):
            continue

        resume_skill = related.get(
            "resume_skill",
            ""
        )

        job_skill = related.get(
            "job_skill",
            ""
        )

        if not job_skill:
            continue

        recommendations.append({
            "type": "related_skill",
            "skill": job_skill,
            "message": (
                f"Your existing skill in {resume_skill} "
                f"is related to {job_skill}. "
                "Consider strengthening the broader skill."
            )
        })

    # --------------------------------
    # 3. Remove duplicate recommendations
    # --------------------------------

    unique_recommendations = []
    seen = set()

    for recommendation in recommendations:

        key = (
            recommendation["type"],
            recommendation["skill"].lower()
        )

        if key in seen:
            continue

        seen.add(key)
        unique_recommendations.append(
            recommendation
        )

    # --------------------------------
    # 4. Return recommendations
    # --------------------------------

    return {
        "recommendations":
            unique_recommendations,

        "recommendation_count":
            len(unique_recommendations)
    }