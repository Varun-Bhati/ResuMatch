from flask import Blueprint, request, jsonify

from backend.services.job_service import analyze_job_description


job_bp = Blueprint("job", __name__)


@job_bp.route("/analyze-job", methods=["POST"])
def analyze_job():
    """
    Analyze a job description submitted by the user.
    """

    data = request.get_json(silent=True)

    if not data or "job_description" not in data:
        return jsonify({
            "error": "No job description was provided."
        }), 400

    job_description = data["job_description"]

    if not isinstance(job_description, str) or not job_description.strip():
        return jsonify({
            "error": "Job description cannot be empty."
        }), 400

    analysis = analyze_job_description(job_description)

    return jsonify({
        "message": "Job description analyzed successfully",
        "analysis": analysis
    })