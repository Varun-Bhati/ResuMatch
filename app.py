from flask import Flask, render_template

from backend.routes.resume_routes import resume_bp
from backend.routes.job_routes import job_bp
from backend.routes.matching_routes import matching_bp


app = Flask(
    __name__,
    template_folder="frontend"
)


app.register_blueprint(resume_bp)
app.register_blueprint(job_bp)
app.register_blueprint(matching_bp)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze")
def analyze_page():
    return render_template("analyze.html")


@app.route("/match")
def match_page():
    return render_template("match.html")


if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False
    )