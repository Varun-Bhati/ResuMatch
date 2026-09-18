from backend.services.text_preprocessor import (
    clean_text,
    normalize_text
)

from backend.services.esco_service import extract_esco_skills

from backend.services.onet_service import extract_onet_software

from backend.services.concept_service import merge_concepts


def analyze_job_description(text):
    """
    Analyze a job description using:
    1. Text cleaning and normalization
    2. ESCO skills and knowledge
    3. O*NET software and technology concepts
    4. Unified concept deduplication
    """

    if not text or not text.strip():
        return {
            "error": "No job description was provided."
        }

    # --------------------------------
    # 1. Clean and normalize text
    # --------------------------------

    cleaned_text = clean_text(text)
    normalized_text = normalize_text(cleaned_text)

    # --------------------------------
    # 2. Extract ESCO concepts
    # --------------------------------

    esco_matches = extract_esco_skills(cleaned_text)

    skills = [
        match
        for match in esco_matches
        if match["skill_type"] == "skill/competence"
    ]

    knowledge = [
        match
        for match in esco_matches
        if match["skill_type"] == "knowledge"
    ]

    # --------------------------------
    # 3. Extract O*NET technologies
    # --------------------------------

    onet_software = extract_onet_software(
        cleaned_text
    )

    # --------------------------------
    # 4. Create unified job profile
    # --------------------------------

    technical_concepts = merge_concepts(
        esco_matches,
        onet_software
    )

    return {
        "cleaned_text": cleaned_text,

        "normalized_text": normalized_text,

        # ESCO
        "skills": skills,

        "knowledge": knowledge,

        # O*NET
        "onet_software": onet_software,

        # Unified profile
        "technical_concepts": technical_concepts,

        "technical_concept_count": len(
            technical_concepts
        ),

        # Separate counts
        "esco_skill_count": len(skills),

        "esco_knowledge_count": len(knowledge),

        "onet_software_count": len(
            onet_software
        )
    }