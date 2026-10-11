import threading


class Database:
    """Thread-safe in-memory store for academic records."""

    def __init__(self):
        self.lock = threading.RLock()
        self.students = {}
        self.faculty = {}
        self.courses = {}
        self.enrollments = []

    def reset(self):
        """Clear all records; useful for automated tests."""
        with self.lock:
            self.students.clear()
            self.faculty.clear()
            self.courses.clear()
            self.enrollments.clear()


db = Database()
