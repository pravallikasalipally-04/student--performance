from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, get_jwt_identity, get_jwt
from extensions import db
from models import User, Student
from utils import admin_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        flash("Invalid email or password.", "danger")
        return render_template("login.html"), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "student_id": user.student_id}
    )
    response = make_response(redirect(url_for("dashboard")))
    set_access_cookies(response, token)
    return response

@auth_bp.route("/logout")
def logout():
    response = make_response(redirect(url_for("index")))
    unset_jwt_cookies(response)
    return response

@auth_bp.route("/admin/create", methods=["GET", "POST"])
def create_admin():
    if request.method == "GET":
        return render_template("register.html", admin_mode=True)

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not name or not email or len(password) < 6:
        flash("Name, email and password (minimum 6 characters) are required.", "danger")
        return render_template("register.html", admin_mode=True), 400

    if User.query.filter_by(email=email).first():
        flash("Email already exists.", "danger")
        return render_template("register.html", admin_mode=True), 409

    user = User(name=name, email=email, role="admin")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash("Admin created. Please login.", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route("/student/register", methods=["GET", "POST"])
def student_register():
    if request.method == "GET":
        return render_template("register.html", admin_mode=False)

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    student_id = request.form.get("student_id", type=int)

    student = Student.query.get(student_id) if student_id else None
    if not name or not email or len(password) < 6 or not student:
        flash("Provide valid name, email, password and an existing student ID.", "danger")
        return render_template("register.html", admin_mode=False), 400

    if User.query.filter_by(email=email).first():
        flash("Email already exists.", "danger")
        return render_template("register.html", admin_mode=False), 409

    user = User(name=name, email=email, role="student", student_id=student.id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash("Student account created. Please login.", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    user = User.query.filter_by(email=data.get("email")).first()
    if not user or not user.check_password(data.get("password", "")):
        return jsonify({"status": "error", "message": "Invalid credentials", "data": None}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "student_id": user.student_id}
    )
    return jsonify({
        "status": "success",
        "message": "Login successful",
        "data": {"access_token": token, "role": user.role, "user_id": user.id}
    }), 200
