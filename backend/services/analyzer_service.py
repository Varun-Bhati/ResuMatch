from backend.services.text_preprocessor import (
    clean_text,
    normalize_text
)

from backend.services.section_detector import (
    detect_sections
)

from backend.services.esco_service import (
    extract_esco_skills
)

from backend.services.onet_service import (
    extract_onet_software
)

from backend.services.concept_service import (
    merge_concepts
)

from backend.services.resume_insights_service import (
    analyze_resume_insights
)

from backend.services.resume_improvement_service import (
    generate_resume_improvement_suggestions
)

from backend.services.resume_quality_service import (
    analyze_resume_quality
)

from backend.services.resume_scoring_service import (
    calculate_resume_score
)


# ============================================================
# MAIN RESUME ANALYZER
# ============================================================

def analyze_resume(text):
    """
    Main entry point for ResuMatch resume analysis.

    The resume is analyzed using:

    1. Text cleaning and normalization
    2. Resume section detection
    3. ESCO skills and knowledge concepts
    4. O*NET software and technology concepts
    5. Unified concept deduplication
    6. Resume scoring
    7. Score breakdown
    8. Score signals
    9. Resume strengths and weaknesses
    10. Resume improvement suggestions
    11. Resume content and structural quality
    """

    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    if not text or not text.strip():

        return {
            "error": "No resume text was provided."
        }


    # ========================================================
    # 1. CLEAN AND NORMALIZE TEXT
    # ========================================================

    cleaned_text = clean_text(
        text
    )

    normalized_text = normalize_text(
        cleaned_text
    )


    # ========================================================
    # 2. DETECT RESUME SECTIONS
    # ========================================================

    sections = detect_sections(
        cleaned_text
    )


    # ========================================================
    # 3. EXTRACT ESCO CONCEPTS
    # ========================================================

    esco_matches = extract_esco_skills(
        cleaned_text
    )


    # --------------------------------------------------------
    # Separate ESCO skills and knowledge
    # --------------------------------------------------------

    skills = [
        match
        for match in esco_matches
        if match["skill_type"]
        == "skill/competence"
    ]


    knowledge = [
        match
        for match in esco_matches
        if match["skill_type"]
        == "knowledge"
    ]


    # ========================================================
    # 4. EXTRACT O*NET TECHNOLOGIES
    # ========================================================

    onet_software = extract_onet_software(
        cleaned_text
    )


    # ========================================================
    # 5. CREATE UNIFIED TECHNICAL PROFILE
    # ========================================================

    technical_concepts = merge_concepts(
        esco_matches,
        onet_software
    )


    # ========================================================
    # 6. BASIC RESUME STATISTICS
    # ========================================================

    word_count = len(
        cleaned_text.split()
    )


    # ========================================================
    # 7. CALCULATE RESUME SCORE
    # ========================================================

    score_result = calculate_resume_score(
        cleaned_text,
        word_count,
        sections,
        skills,
        knowledge,
        technical_concepts
    )


    # --------------------------------------------------------
    # Extract score information
    # --------------------------------------------------------

    resume_score = score_result[
        "total_score"
    ]


    score_breakdown = score_result[
        "breakdown"
    ]


    score_signals = score_result[
        "signals"
    ]


    # ========================================================
    # 8. ANALYZE RESUME INSIGHTS
    # ========================================================

    insights = analyze_resume_insights(
        word_count,
        sections,
        skills,
        knowledge,
        onet_software
    )


    # ========================================================
    # 9. GENERATE IMPROVEMENT SUGGESTIONS
    # ========================================================

    improvement_suggestions = (
        generate_resume_improvement_suggestions(
            word_count,
            sections,
            skills,
            knowledge,
            onet_software
        )
    )


    # ========================================================
    # 10. ANALYZE RESUME QUALITY
    # ========================================================

    quality_issues = analyze_resume_quality(
        word_count,
        sections,
        skills,
        knowledge,
        onet_software
    )


    # ========================================================
    # 11. RETURN COMPLETE ANALYSIS
    # ========================================================

    return {

        # ----------------------------------------------------
        # Basic statistics
        # ----------------------------------------------------

        "word_count":
            word_count,


        # ----------------------------------------------------
        # Resume score
        # ----------------------------------------------------

        "resume_score":
            resume_score,


        "score_breakdown":
            score_breakdown,


        "score_signals":
            score_signals,


        # ----------------------------------------------------
        # Processed text
        # ----------------------------------------------------

        "cleaned_text":
            cleaned_text,


        "normalized_text":
            normalized_text,


        # ----------------------------------------------------
        # Resume structure
        # ----------------------------------------------------

        "sections":
            sections,


        # ----------------------------------------------------
        # Resume insights
        # ----------------------------------------------------

        "strengths":
            insights["strengths"],


        "weaknesses":
            insights["weaknesses"],


        "missing_sections":
            insights["missing_sections"],


        # ----------------------------------------------------
        # Recommendations
        # ----------------------------------------------------

        "improvement_suggestions":
            improvement_suggestions,


        # ----------------------------------------------------
        # Quality analysis
        # ----------------------------------------------------

        "quality_issues":
            quality_issues,


        # ----------------------------------------------------
        # ESCO
        # ----------------------------------------------------

        "skills":
            skills,


        "knowledge":
            knowledge,


        # ----------------------------------------------------
        # O*NET
        # ----------------------------------------------------

        "onet_software":
            onet_software,


        # ----------------------------------------------------
        # Unified technical profile
        # ----------------------------------------------------

        "technical_concepts":
            technical_concepts,


        "technical_concept_count":
            len(
                technical_concepts
            ),


        # ----------------------------------------------------
        # Separate concept counts
        # ----------------------------------------------------

        "esco_skill_count":
            len(
                skills
            ),


        "esco_knowledge_count":
            len(
                knowledge
            ),


        "onet_software_count":
            len(
                onet_software
            )
    }