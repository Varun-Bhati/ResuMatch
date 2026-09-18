from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

import os

from backend.services.resume_service import (
    extract_text_from_pdf,
    extract_text_from_docx
)

from backend.services.analyzer_service import analyze_resume
from backend.services.job_service import analyze_job_description
from backend.services.matching_service import match_resume_to_job
from backend.services.skill_gap_service import analyze_skill_gap
from backend.services.ats_service import analyze_ats
from backend.services.keyword_service import analyze_keywords
from backend.services.recommendation_service import analyze_recommendations


matching_bp = Blueprint("matching", __name__)


@matching_bp.route("/match-resume", methods=["POST"])
def match_resume():

    # --------------------------------
    # 1. Validate resume
    # --------------------------------

    if "resume" not in request.files:
        return jsonify({
            "error": "No resume uploaded."
        }), 400

    resume_file = request.files["resume"]

    if resume_file.filename == "":
        return jsonify({
            "error": "No resume file selected."
        }), 400


    # --------------------------------
    # 2. Validate job description
    # --------------------------------

    job_description = request.form.get(
        "job_description",
        ""
    )

    if not job_description.strip():
        return jsonify({
            "error": "No job description was provided."
        }), 400


    # --------------------------------
    # 3. Save uploaded resume
    # --------------------------------

    os.makedirs(
        "data/uploads",
        exist_ok=True
    )

    safe_filename = secure_filename(
        resume_file.filename
    )

    file_path = os.path.join(
        "data/uploads",
        safe_filename
    )

    resume_file.save(file_path)


    # --------------------------------
    # 4. Extract resume text
    # --------------------------------

    # Check whether the uploaded file is empty

    if os.path.getsize(file_path) == 0:
        return jsonify({
            "error": "The uploaded resume file is empty."
        }), 400


    if resume_file.filename.lower().endswith(".pdf"):

        try:
            resume_text = extract_text_from_pdf(
                file_path
            )

        except Exception:
            return jsonify({
                "error": "The uploaded PDF could not be read."
            }), 400


    elif resume_file.filename.lower().endswith(".docx"):

        try:
            resume_text = extract_text_from_docx(
                file_path
            )

        except Exception:
            return jsonify({
                "error": "The uploaded DOCX could not be read."
            }), 400


    else:

        return jsonify({
            "error": "Only PDF and DOCX files are supported."
        }), 400


    # Check whether the file contains readable text

    if not resume_text or not resume_text.strip():
        return jsonify({
            "error": "No readable text was found in the resume."
        }), 400


    # --------------------------------
    # 5. Analyze resume
    # --------------------------------

    resume_analysis = analyze_resume(
        resume_text
    )


    # --------------------------------
    # 6. Analyze job description
    # --------------------------------

    job_analysis = analyze_job_description(
        job_description
    )


    # --------------------------------
    # 7. Get unified technical concepts
    # --------------------------------

    resume_concepts = (
        resume_analysis.get(
            "technical_concepts",
            []
        )
    )

    job_concepts = (
        job_analysis.get(
            "technical_concepts",
            []
        )
    )


    # --------------------------------
    # 8. Match resume against job
    # --------------------------------

    match_result = match_resume_to_job(
        resume_concepts,
        job_concepts
    )


    # --------------------------------
    # 9. Analyze skill gaps
    # --------------------------------

    skill_gap = analyze_skill_gap(
        match_result
    )


    # --------------------------------
    # 10. Analyze keyword coverage
    # --------------------------------

    keyword_analysis = analyze_keywords(
        resume_analysis,
        job_analysis
    )


    # --------------------------------
    # 11. Analyze ATS compatibility
    # --------------------------------

    ats_analysis = analyze_ats(
        resume_text,
        keyword_analysis
    )


    # --------------------------------
    # 12. Generate recommendations
    # --------------------------------

    recommendations = analyze_recommendations(
        skill_gap
    )


    # --------------------------------
    # 13. Return complete result
    # --------------------------------

    return jsonify({

        "message":
            "Resume and job description matched successfully",

        "resume_analysis":
            resume_analysis,

        "job_analysis":
            job_analysis,

        "match":
            match_result,

        "skill_gap":
            skill_gap,

        "ats":
            ats_analysis,

        "keywords":
            keyword_analysis,

        "recommendations":
            recommendations
    })