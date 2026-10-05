from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Student
from utils import admin_required, method_override

students_bp = Blueprint("students", __name__)

def student_data(s):
    return {"id": s.id, "name": s.name, "email": s.email}

@students_bp.route("/students", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@admin_required
def students_collection():
    if request.method == "GET":
        q = request.args.get("q", "").strip()
        students = Student.query.filter(
            (Student.name.ilike(f"%{q}%")) | (Student.email.ilike(f"%{q}%"))
        ).all() if q else Student.query.all()
        return render_template("students.html", students=students, q=q)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        if not name or not email:
            flash("Name and email are required.", "danger")
            return redirect(url_for("students.new_student"))
        try:
            db.session.add(Student(name=name, email=email))
            db.session.commit()
            flash("Student created successfully.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Email already exists.", "danger")
        return redirect(url_for("students.students_collection"))

@students_bp.route("/students/new")
@admin_required
def new_student():
    return render_template("student_form.html", student=None, action=url_for("students.students_collection"))

@students_bp.route("/students/<int:id>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@admin_required
def student_detail(id):
    student = Student.query.get_or_404(id)

    if request.method == "GET":
        return render_template("student_detail.html", student=student)

    if request.method == "DELETE" or method_override() == "DELETE":
        db.session.delete(student)
        db.session.commit()
        flash("Student deleted.", "success")
        return redirect(url_for("students.students_collection"))

    if request.method in ("PUT", "PATCH") or method_override() in ("PUT", "PATCH"):
        name = request.form.get("name", student.name).strip()
        email = request.form.get("email", student.email).strip()
        if not name or not email:
            flash("Name and email are required.", "danger")
            return redirect(url_for("students.edit_student", id=id))
        student.name = name
        student.email = email
        try:
            db.session.commit()
            flash("Student updated.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Email already exists.", "danger")
        return redirect(url_for("students.student_detail", id=id))

@students_bp.route("/students/<int:id>/edit")
@admin_required
def edit_student(id):
    return render_template("student_form.html", student=Student.query.get_or_404(id),
                           action=url_for("students.student_detail", id=id))

@students_bp.route("/students/<int:id>/delete", methods=["POST"])
@admin_required
def delete_student_confirm(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted.", "success")
    return redirect(url_for("students.students_collection"))
