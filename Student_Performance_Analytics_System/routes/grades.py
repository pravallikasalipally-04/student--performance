from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Grade, Student, Course
from utils import admin_required, method_override

grades_bp = Blueprint("grades", __name__)

@grades_bp.route("/grades", methods=["GET", "POST"])
@admin_required
def grades_collection():
    if request.method == "GET":
        grades = Grade.query.order_by(Grade.date.desc()).all()
        return render_template("grades.html", grades=grades)

    student_id = request.form.get("student_id", type=int)
    course_id = request.form.get("course_id", type=int)
    score = request.form.get("score", type=float)
    date_text = request.form.get("date", "")

    if not student_id or not course_id or score is None or not 0 <= score <= 100:
        flash("Student, course and score 0-100 are required.", "danger")
        return redirect(url_for("grades.grades_collection"))

    grade_date = datetime.strptime(date_text, "%Y-%m-%d").date() if date_text else datetime.today().date()
    db.session.add(Grade(student_id=student_id, course_id=course_id, score=score, date=grade_date))
    db.session.commit()
    flash("Grade assigned.", "success")
    return redirect(url_for("grades.grades_collection"))

@grades_bp.route("/grades/new")
@admin_required
def new_grade():
    return render_template("grade_form.html", grade=None,
                           students=Student.query.all(), courses=Course.query.all())

@grades_bp.route("/grades/<int:id>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@admin_required
def grade_detail(id):
    grade = Grade.query.get_or_404(id)
    if request.method == "GET":
        return render_template("grade_detail.html", grade=grade)

    if request.method == "DELETE" or method_override() == "DELETE":
        db.session.delete(grade)
        db.session.commit()
        flash("Grade deleted.", "success")
        return redirect(url_for("grades.grades_collection"))

    if request.method in ("PUT", "PATCH") or method_override() in ("PUT", "PATCH"):
        score = request.form.get("score", type=float)
        if score is None or not 0 <= score <= 100:
            flash("Score must be between 0 and 100.", "danger")
            return redirect(url_for("grades.grade_detail", id=id))
        grade.score = score
        date_text = request.form.get("date", "")
        if date_text:
            grade.date = datetime.strptime(date_text, "%Y-%m-%d").date()
        db.session.commit()
        flash("Grade updated.", "success")
        return redirect(url_for("grades.grade_detail", id=id))
