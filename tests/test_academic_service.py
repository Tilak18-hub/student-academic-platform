import pytest

from app import create_app
from app.services.academic_service import AcademicService
from database.db import db


@pytest.fixture(autouse=True)
def reset_database():
    db.reset()
    yield
    db.reset()


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def setup_student_and_courses():
    AcademicService.add_student("S101", "Test Student", "student@example.com")
    AcademicService.add_faculty("F101", "Test Faculty", "faculty@example.com")
    AcademicService.add_course("C101", "Python", 4, "F101")
    AcademicService.add_course("C102", "DevOps", 5, "F101")
    AcademicService.add_course("C103", "AI", 6, "F101")
    AcademicService.add_course("C104", "Cloud", 4, "F101")


def test_add_and_get_student():
    student = AcademicService.add_student(
        "S101", "Test Student", "student@example.com"
    )
    assert student["student_id"] == "S101"
    assert AcademicService.get_student("S101")["name"] == "Test Student"


def test_duplicate_student_rejected():
    AcademicService.add_student("S101", "Student", "s@example.com")
    with pytest.raises(ValueError, match="already exists"):
        AcademicService.add_student("S101", "Duplicate", "d@example.com")


def test_course_enrollment_and_credit_limit():
    setup_student_and_courses()
    AcademicService.enroll_student("S101", "C101", "Semester 1")
    AcademicService.enroll_student("S101", "C102", "Semester 1")
    AcademicService.enroll_student("S101", "C103", "Semester 1")

    with pytest.raises(ValueError, match="credit limit"):
        AcademicService.enroll_student("S101", "C104", "Semester 1")


def test_duplicate_enrollment_rejected():
    setup_student_and_courses()
    AcademicService.enroll_student("S101", "C101", "Semester 1")

    with pytest.raises(ValueError, match="already enrolled"):
        AcademicService.enroll_student("S101", "C101", "Semester 1")


def test_unknown_student_cannot_enroll():
    AcademicService.add_course("C101", "Python", 4)

    with pytest.raises(ValueError, match="Student not found"):
        AcademicService.enroll_student("UNKNOWN", "C101", "Semester 1")


def test_grade_assignment_and_gpa():
    setup_student_and_courses()
    AcademicService.enroll_student("S101", "C101", "Semester 1")
    AcademicService.enroll_student("S101", "C102", "Semester 1")

    AcademicService.assign_grade("S101", "C101", "Semester 1", "O")
    AcademicService.assign_grade("S101", "C102", "Semester 1", "A")

    result = AcademicService.calculate_gpa("S101", "Semester 1")
    assert result["gpa"] == 8.89
    assert result["graded_courses"] == 2


def test_invalid_grade_rejected():
    setup_student_and_courses()
    AcademicService.enroll_student("S101", "C101", "Semester 1")

    with pytest.raises(ValueError, match="Invalid grade"):
        AcademicService.assign_grade("S101", "C101", "Semester 1", "Z")


def test_health_and_student_api(client):
    response = client.get("/health")
    assert response.status_code == 200

    response = client.post("/api/students", json={
        "student_id": "S201",
        "name": "API Student",
        "email": "api@example.com",
    })
    assert response.status_code == 201

    response = client.get("/api/students/S201")
    assert response.status_code == 200
    assert response.get_json()["name"] == "API Student"
