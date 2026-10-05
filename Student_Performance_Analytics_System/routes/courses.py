from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Course
from utils import admin_required, method_override

courses_bp = Blueprint("courses", __name__)

@courses_bp.route("/courses", methods=["GET", "POST"])
@admin_required
def courses_collection():
    if request.method == "GET":
        courses = Course.query.all()
        return render_template("courses.html", courses=courses)

    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip().upper()
    if not name or not code:
        flash("Course name and code are required.", "danger")
        return redirect(url_for("courses.new_course"))
    try:
        db.session.add(Course(name=name, code=code))
        db.session.commit()
        flash("Course created.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Course code already exists.", "danger")
    return redirect(url_for("courses.courses_collection"))

@courses_bp.route("/courses/new")
@admin_required
def new_course():
    return render_template("course_form.html", course=None, action=url_for("courses.courses_collection"))

@courses_bp.route("/courses/<int:id>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@admin_required
def course_detail(id):
    course = Course.query.get_or_404(id)

    if request.method == "GET":
        return render_template("course_detail.html", course=course)

    if request.method == "DELETE" or method_override() == "DELETE":
        db.session.delete(course)
        try:
            db.session.commit()
            flash("Course deleted.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Cannot delete course while grades reference it.", "danger")
        return redirect(url_for("courses.courses_collection"))

    if request.method in ("PUT", "PATCH") or method_override() in ("PUT", "PATCH"):
        course.name = request.form.get("name", course.name).strip()
        course.code = request.form.get("code", course.code).strip().upper()
        try:
            db.session.commit()
            flash("Course updated.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Course code already exists.", "danger")
        return redirect(url_for("courses.course_detail", id=id))

@courses_bp.route("/courses/<int:id>/edit")
@admin_required
def edit_course(id):
    return render_template("course_form.html", course=Course.query.get_or_404(id),
                           action=url_for("courses.course_detail", id=id))
