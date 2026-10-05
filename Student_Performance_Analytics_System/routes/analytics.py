import os
import pandas as pd
import numpy as np
from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from extensions import db
from models import Grade, Student, Course
from utils import admin_required

analytics_bp = Blueprint("analytics", __name__)

def dataframe_from_db():
    rows = db.session.query(
        Grade.id, Student.name.label("student"), Student.email,
        Course.name.label("course"), Course.code, Grade.score, Grade.date
    ).join(Student, Grade.student_id == Student.id).join(Course, Grade.course_id == Course.id).all()
    return pd.DataFrame([{
        "id": r.id, "student": r.student, "email": r.email,
        "course": r.course, "code": r.code, "score": r.score, "date": r.date
    } for r in rows])

@analytics_bp.route("/analytics")
@admin_required
def analytics():
    df = dataframe_from_db()
    if df.empty:
        stats = {"mean": 0, "median": 0, "std": 0}
        course_avg = []
        ranking = []
    else:
        selected_course = request.args.get("course", "").strip()
        selected_student = request.args.get("student", "").strip()
        filtered = df.copy()
        if selected_course:
            filtered = filtered[filtered["code"] == selected_course]
        if selected_student:
            filtered = filtered[filtered["student"].str.contains(selected_student, case=False, na=False)]

        stats = {
            "mean": round(float(np.mean(filtered["score"])), 2) if len(filtered) else 0,
            "median": round(float(np.median(filtered["score"])), 2) if len(filtered) else 0,
            "std": round(float(np.std(filtered["score"])), 2) if len(filtered) else 0
        }
        course_avg = (filtered.groupby(["code", "course"])["score"].mean()
                      .round(2).reset_index().sort_values("score", ascending=False).to_dict("records"))
        ranking = (filtered.groupby(["student", "course"])["score"].mean()
                   .round(2).reset_index().sort_values(["course", "score"], ascending=[True, False])
                   .to_dict("records"))
    courses = Course.query.all()
    return render_template("analytics.html", stats=stats, course_avg=course_avg,
                           ranking=ranking, courses=courses)

@analytics_bp.route("/analytics/upload", methods=["POST"])
@admin_required
def upload_csv():
    file = request.files.get("file")
    if not file or not file.filename.lower().endswith(".csv"):
        flash("Please upload a .csv file.", "danger")
        return redirect(url_for("analytics.analytics"))

    path = os.path.join("uploads", file.filename)
    file.save(path)
    try:
        df = pd.read_csv(path)
        required = {"student_id", "course_id", "score", "date"}
        if not required.issubset(df.columns):
            flash("CSV must contain student_id, course_id, score, date columns.", "danger")
            return redirect(url_for("analytics.analytics"))

        inserted = 0
        for _, row in df.iterrows():
            if not 0 <= float(row["score"]) <= 100:
                continue
            if not Student.query.get(int(row["student_id"])) or not Course.query.get(int(row["course_id"])):
                continue
            grade = Grade(student_id=int(row["student_id"]), course_id=int(row["course_id"]),
                          score=float(row["score"]), date=pd.to_datetime(row["date"]).date())
            db.session.add(grade)
            inserted += 1
        db.session.commit()
        flash(f"CSV imported. {inserted} grade rows added.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"CSV import failed: {e}", "danger")
    return redirect(url_for("analytics.analytics"))

@analytics_bp.route("/analytics/export/<fmt>")
@admin_required
def export_report(fmt):
    df = dataframe_from_db()
    if df.empty:
        df = pd.DataFrame(columns=["student", "email", "course", "code", "score", "date"])

    if fmt == "csv":
        path = "exports/student_analytics.csv"
        df.to_csv(path, index=False)
        return send_file(path, as_attachment=True, download_name="student_analytics.csv")

    if fmt == "xlsx":
        path = "exports/student_analytics.xlsx"
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Report", index=False)
        return send_file(path, as_attachment=True, download_name="student_analytics.xlsx")

    flash("Unsupported format.", "danger")
    return redirect(url_for("analytics.analytics"))
