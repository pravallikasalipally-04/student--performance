from functools import wraps
from flask import request, jsonify, redirect, url_for, flash
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def method_override():
    return request.form.get("_method", "").upper()

def api_or_form_error(message, status=400):
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": message, "data": None}), status
    flash(message, "danger")
    return redirect(request.referrer or url_for("students.list_students"))

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "admin":
                if request.path.startswith("/api/"):
                    return jsonify({"status": "error", "message": "Admin access required", "data": None}), 403
                flash("Admin access required.", "danger")
                return redirect(url_for("login"))
        except Exception:
            if request.path.startswith("/api/"):
                return jsonify({"status": "error", "message": "Authentication required", "data": None}), 401
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def login_required_any(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            if request.path.startswith("/api/"):
                return jsonify({"status": "error", "message": "Authentication required", "data": None}), 401
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper
