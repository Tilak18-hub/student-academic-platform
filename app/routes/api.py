from flask import Blueprint, jsonify, request
from app.services.academic_service import AcademicService

api_bp = Blueprint("api", __name__)


def execute(action, success_status=200):
    try:
        return jsonify(action()), success_status
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except (TypeError, KeyError):
        return jsonify({"error": "Invalid request data."}), 400


@api_bp.get("/students/<student_id>")
def get_student(student_id):
    student = AcademicService.get_student(student_id)
    if student is None:
        return jsonify({"error": "Student not found."}), 404
    return jsonify(student), 200


@api_bp.post("/students")
def add_student():
    data = request.get_json(silent=True) or {}
    return execute(
        lambda: AcademicService.add_student(
            data.get("student_id"), data.get("name"), data.get("email")
        ),
        201,
    )


@api_bp.post("/faculty")
def add_faculty():
    data = request.get_json(silent=True) or {}
    return execute(
        lambda: AcademicService.add_faculty(
            data.get("faculty_id"), data.get("name"), data.get("email")
        ),
        201,
    )


@api_bp.post("/courses")
def add_course():
    data = request.get_json(silent=True) or {}
    return execute(
        lambda: AcademicService.add_course(
            data.get("course_id"),
            data.get("title"),
            data.get("credits"),
            data.get("faculty_id"),
        ),
        201,
    )


@api_bp.post("/enrollments")
def enroll_student():
    data = request.get_json(silent=True) or {}
    return execute(
        lambda: AcademicService.enroll_student(
            data.get("student_id"),
            data.get("course_id"),
            data.get("semester"),
        ),
        201,
    )


@api_bp.post("/grades")
def assign_grade():
    data = request.get_json(silent=True) or {}
    return execute(
        lambda: AcademicService.assign_grade(
            data.get("student_id"),
            data.get("course_id"),
            data.get("semester"),
            data.get("grade"),
        )
    )


@api_bp.get("/students/<student_id>/gpa")
def calculate_gpa(student_id):
    semester = request.args.get("semester", "").strip()
    if not semester:
        return jsonify({"error": "Semester query parameter is required."}), 400
    return execute(lambda: AcademicService.calculate_gpa(student_id, semester))
