import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, unset_jwt_cookies, get_jwt_identity, get_jwt
from config import Config
from extensions import db, jwt
from models import User, Student, Course, Grade

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs("exports", exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)

    from routes.auth import auth_bp
    from routes.students import students_bp
    from routes.courses import courses_bp
    from routes.grades import grades_bp
    from routes.analytics import analytics_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(grades_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_user():
        try:
            claims = get_jwt()
            return {"current_role": claims.get("role")}
        except Exception:
            return {"current_role": None}

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template(
            "dashboard.html",
            student_count=Student.query.count(),
            course_count=Course.query.count(),
            grade_count=Grade.query.count()
        )

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"status": "error", "message": "Resource not found", "data": None}), 404
        return render_template("error.html", code=404, message="Page not found"), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        if request.path.startswith("/api/"):
            return jsonify({"status": "error", "message": "Internal server error", "data": None}), 500
        return render_template("error.html", code=500, message="Internal server error"), 500

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
