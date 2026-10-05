from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from extensions import db
from models import User, Student, Course, Grade
from utils import admin_required, login_required_any

api_bp = Blueprint("api", __name__, url_prefix="/api")

def require_admin_json():
    verify_jwt_in_request()
    if get_jwt().get("role") != "admin":
        return False
    return True

def student_json(s):
    return {"id": s.id, "name": s.name, "email": s.email}

def course_json(c):
    return {"id": c.id, "name": c.name, "code": c.code}

def grade_json(g):
    return {"id": g.id, "student_id": g.student_id, "course_id": g.course_id,
            "score": g.score, "date": g.date.isoformat()}

@api_bp.route("/students", methods=["GET", "POST"])
@login_required_any
def api_students():
    if request.method == "GET":
        claims = get_jwt()
        if claims.get("role") == "student":
            s = Student.query.get(claims.get("student_id"))
            return jsonify({"status": "success", "data": [student_json(s)] if s else []})
        return jsonify({"status": "success", "data": [student_json(s) for s in Student.query.all()]})

    if not require_admin_json():
        return jsonify({"status": "error", "message": "Admin access required", "data": None}), 403
    data = request.get_json(silent=True) or {}
    if not data.get("name") or not data.get("email"):
        return jsonify({"status": "error", "message": "name and email are required", "data": None}), 400
    try:
        s = Student(name=data["name"], email=data["email"])
        db.session.add(s)
        db.session.commit()
        return jsonify({"status": "success", "message": "Student created", "data": student_json(s)}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Email already exists", "data": None}), 409

@api_bp.route("/students/<int:id>", methods=["GET", "PUT", "PATCH", "DELETE"])
@login_required_any
def api_student(id):
    s = Student.query.get_or_404(id)
    claims = get_jwt()
    if claims.get("role") == "student" and claims.get("student_id") != s.id:
        return jsonify({"status": "error", "message": "You can only view your own data", "data": None}), 403

    if request.method == "GET":
        return jsonify({"status": "success", "data": student_json(s)})

    if claims.get("role") != "admin":
        return jsonify({"status": "error", "message": "Admin access required", "data": None}), 403

    data = request.get_json(silent=True) or {}
    if request.method == "PUT":
        if not data.get("name") or not data.get("email"):
            return jsonify({"status": "error", "message": "PUT requires name and email", "data": None}), 400
        s.name, s.email = data["name"], data["email"]
    elif request.method == "PATCH":
        if "name" in data: s.name = data["name"]
        if "email" in data: s.email = data["email"]
    elif request.method == "DELETE":
        db.session.delete(s)
        db.session.commit()
        return jsonify({"status": "success", "message": "Student deleted", "data": None})
    try:
        db.session.commit()
        return jsonify({"status": "success", "message": "Student updated", "data": student_json(s)})
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Email already exists", "data": None}), 409

@api_bp.route("/courses", methods=["GET", "POST"])
@login_required_any
def api_courses():
    if request.method == "GET":
        return jsonify({"status": "success", "data": [course_json(c) for c in Course.query.all()]})
    if not require_admin_json():
        return jsonify({"status": "error", "message": "Admin access required", "data": None}), 403
    data = request.get_json(silent=True) or {}
    if not data.get("name") or not data.get("code"):
        return jsonify({"status": "error", "message": "name and code are required", "data": None}), 400
    try:
        c = Course(name=data["name"], code=data["code"].upper())
        db.session.add(c)
        db.session.commit()
        return jsonify({"status": "success", "message": "Course created", "data": course_json(c)}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Course code already exists", "data": None}), 409

@api_bp.route("/courses/<int:id>", methods=["GET", "PUT", "PATCH", "DELETE"])
@login_required_any
def api_course(id):
    c = Course.query.get_or_404(id)
    if request.method == "GET":
        return jsonify({"status": "success", "data": course_json(c)})
    if not require_admin_json():
        return jsonify({"status": "error", "message": "Admin access required", "data": None}), 403
    data = request.get_json(silent=True) or {}
    if request.method == "PUT":
        if not data.get("name") or not data.get("code"):
            return jsonify({"status": "error", "message": "PUT requires name and code", "data": None}), 400
        c.name, c.code = data["name"], data["code"].upper()
    elif request.method == "PATCH":
        if "name" in data: c.name = data["name"]
        if "code" in data: c.code = data["code"].upper()
    else:
        db.session.delete(c)
        try:
            db.session.commit()
            return jsonify({"status": "success", "message": "Course deleted", "data": None})
        except IntegrityError:
            db.session.rollback()
            return jsonify({"status": "error", "message": "Course has grades", "data": None}), 409
    try:
        db.session.commit()
        return jsonify({"status": "success", "message": "Course updated", "data": course_json(c)})
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Course code already exists", "data": None}), 409

@api_bp.route("/grades", methods=["GET", "POST"])
@login_required_any
def api_grades():
    claims = get_jwt()
    if request.method == "GET":
        grades = Grade.query.filter_by(student_id=claims.get("student_id")).all() if claims.get("role") == "student" else Grade.query.all()
        return jsonify({"status": "success", "data": [grade_json(g) for g in grades]})

    if not require_admin_json():
        return jsonify({"status": "error", "message": "Admin access required", "data": None}), 403
    data = request.get_json(silent=True) or {}
    try:
        score = float(data["score"])
        if not 0 <= score <= 100:
            raise ValueError()
        g = Grade(student_id=int(data["student_id"]), course_id=int(data["course_id"]),
                  score=score, date=datetime.strptime(data.get("date", datetime.today().strftime("%Y-%m-%d")), "%Y-%m-%d").date())
        db.session.add(g)
        db.session.commit()
        return jsonify({"status": "success", "message": "Grade created", "data": grade_json(g)}), 201
    except (KeyError, ValueError, TypeError):
        return jsonify({"status": "error", "message": "Valid student_id, course_id and score 0-100 are required", "data": None}), 400

@api_bp.route("/grades/<int:id>", methods=["GET", "PUT", "PATCH", "DELETE"])
@login_required_any
def api_grade(id):
    g = Grade.query.get_or_404(id)
    claims = get_jwt()
    if claims.get("role") == "student" and g.student_id != claims.get("student_id"):
        return jsonify({"status": "error", "message": "You can only view your own grades", "data": None}), 403
    if request.method == "GET":
        return jsonify({"status": "success", "data": grade_json(g)})
    if claims.get("role") != "admin":
        return jsonify({"status": "error", "message": "Admin access required", "data": None}), 403

    data = request.get_json(silent=True) or {}
    if request.method == "DELETE":
        db.session.delete(g)
        db.session.commit()
        return jsonify({"status": "success", "message": "Grade deleted", "data": None})
    if "score" in data:
        score = float(data["score"])
        if not 0 <= score <= 100:
            return jsonify({"status": "error", "message": "Score must be 0-100", "data": None}), 400
        g.score = score
    if "student_id" in data: g.student_id = int(data["student_id"])
    if "course_id" in data: g.course_id = int(data["course_id"])
    if "date" in data: g.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
    db.session.commit()
    return jsonify({"status": "success", "message": "Grade updated", "data": grade_json(g)})
