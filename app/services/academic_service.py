from database.db import db


class AcademicService:
    """Business rules for student academic management."""

    GRADE_POINTS = {
        "O": 10.0,
        "A+": 9.0,
        "A": 8.0,
        "B+": 7.0,
        "B": 6.0,
        "C": 5.0,
        "P": 4.0,
        "F": 0.0,
    }

    @staticmethod
    def add_student(student_id, name, email):
        if not all(
            isinstance(v, str) and v.strip()
            for v in (student_id, name, email)
        ):
            raise ValueError("Student ID, name and email are required.")

        with db.lock:
            if student_id in db.students:
                raise ValueError(f"Student '{student_id}' already exists.")

            student = {
                "student_id": student_id,
                "name": name.strip(),
                "email": email.strip(),
            }
            db.students[student_id] = student
            return student.copy()

    @staticmethod
    def get_student(student_id):
        with db.lock:
            student = db.students.get(student_id)
            return student.copy() if student else None

    @staticmethod
    def add_faculty(faculty_id, name, email):
        if not all(
            isinstance(v, str) and v.strip()
            for v in (faculty_id, name, email)
        ):
            raise ValueError("Faculty ID, name and email are required.")

        with db.lock:
            if faculty_id in db.faculty:
                raise ValueError(f"Faculty '{faculty_id}' already exists.")

            faculty = {
                "faculty_id": faculty_id,
                "name": name.strip(),
                "email": email.strip(),
            }
            db.faculty[faculty_id] = faculty
            return faculty.copy()

    @staticmethod
    def add_course(course_id, title, credits, faculty_id=None):
        if not isinstance(course_id, str) or not course_id.strip():
            raise ValueError("Course ID is required.")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Course title is required.")
        if isinstance(credits, bool) or not isinstance(credits, int):
            raise ValueError("Credits must be a positive integer.")
        if credits < 1:
            raise ValueError("Credits must be a positive integer.")

        with db.lock:
            if course_id in db.courses:
                raise ValueError(f"Course '{course_id}' already exists.")
            if faculty_id and faculty_id not in db.faculty:
                raise ValueError("Faculty not found.")

            course = {
                "course_id": course_id,
                "title": title.strip(),
                "credits": credits,
                "faculty_id": faculty_id,
            }
            db.courses[course_id] = course
            return course.copy()

    @staticmethod
    def enroll_student(student_id, course_id, semester):
        if not isinstance(semester, str) or not semester.strip():
            raise ValueError("Semester is required.")

        with db.lock:
            if student_id not in db.students:
                raise ValueError("Student not found.")
            if course_id not in db.courses:
                raise ValueError("Course not found.")

            existing = [
                e for e in db.enrollments
                if e["student_id"] == student_id
                and e["semester"] == semester.strip()
            ]

            if any(e["course_id"] == course_id for e in existing):
                raise ValueError("Student is already enrolled in this course.")

            current_credits = sum(
                db.courses[e["course_id"]]["credits"] for e in existing
            )
            course_credits = db.courses[course_id]["credits"]

            if current_credits + course_credits > 18:
                raise ValueError("Semester credit limit of 18 exceeded.")

            enrollment = {
                "student_id": student_id,
                "course_id": course_id,
                "semester": semester.strip(),
                "grade": None,
            }
            db.enrollments.append(enrollment)
            return enrollment.copy()

    @staticmethod
    def assign_grade(student_id, course_id, semester, grade):
        if not isinstance(grade, str):
            raise ValueError("Invalid grade.")
        grade = grade.strip().upper()
        if grade not in AcademicService.GRADE_POINTS:
            raise ValueError("Invalid grade.")

        with db.lock:
            for enrollment in db.enrollments:
                if (
                    enrollment["student_id"] == student_id
                    and enrollment["course_id"] == course_id
                    and enrollment["semester"] == semester
                ):
                    enrollment["grade"] = grade
                    return enrollment.copy()

            raise ValueError("Matching enrollment not found.")

    @staticmethod
    def calculate_gpa(student_id, semester):
        with db.lock:
            if student_id not in db.students:
                raise ValueError("Student not found.")

            records = [
                e for e in db.enrollments
                if e["student_id"] == student_id
                and e["semester"] == semester
                and e["grade"] is not None
            ]

            if not records:
                return {"student_id": student_id, "semester": semester,
                        "gpa": None, "graded_courses": 0}

            total_points = 0.0
            total_credits = 0

            for enrollment in records:
                credits = db.courses[enrollment["course_id"]]["credits"]
                points = AcademicService.GRADE_POINTS[enrollment["grade"]]
                total_points += points * credits
                total_credits += credits

            return {
                "student_id": student_id,
                "semester": semester,
                "gpa": round(total_points / total_credits, 2),
                "graded_courses": len(records),
            }
