from flask import Blueprint, request, jsonify

import os

from backend.services.resume_service import (
    extract_text_from_pdf,
    extract_text_from_docx
)

from backend.services.analyzer_service import (
    analyze_resume
)

from backend.services.ats_service import (
    analyze_ats
)

from backend.services.keyword_service import (
    analyze_keywords
)


resume_bp = Blueprint(
    "resume",
    __name__
)


@resume_bp.route(
    "/upload-resume",
    methods=["POST"]
)
def upload_resume():

    # ========================================================
    # 1. CHECK FILE
    # ========================================================

    if "resume" not in request.files:

        return jsonify({
            "error": "No resume uploaded"
        }), 400

    file = request.files["resume"]

    if file.filename == "":

        return jsonify({
            "error": "No file selected"
        }), 400

    # ========================================================
    # 2. SAVE FILE
    # ========================================================

    os.makedirs(
        "data/uploads",
        exist_ok=True
    )

    file_path = os.path.join(
        "data/uploads",
        file.filename
    )

    file.save(
        file_path
    )

    # ========================================================
    # 3. EXTRACT TEXT
    # ========================================================

    if file.filename.lower().endswith(".pdf"):

        text = extract_text_from_pdf(
            file_path
        )

    elif file.filename.lower().endswith(".docx"):

        text = extract_text_from_docx(
            file_path
        )

    else:

        return jsonify({
            "error":
                "Only PDF and DOCX files are supported"
        }), 400

    # ========================================================
    # 4. ANALYZE RESUME
    # ========================================================

    analysis = analyze_resume(
        text
    )

    # ========================================================
    # 5. ANALYZE ATS
    # ========================================================

    # ATS keyword analysis requires a job analysis.
    #
    # For a resume-only upload there is no job description,
    # so we do not calculate job-specific keyword matching
    # here.
    #
    # The resume analyzer still provides the resume-level
    # analysis.

    ats = analyze_ats(
        text
    )

    # ========================================================
    # 6. RETURN RESULT
    # ========================================================

    return jsonify({

        "message":
            "Resume uploaded successfully",

        "filename":
            file.filename,

        "text":
            text,

        "analysis":
            analysis,

        "ats":
            ats
    })