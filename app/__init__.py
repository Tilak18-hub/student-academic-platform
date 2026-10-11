from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return {
            "status": "UP",
            "service": "Student Academic Management Platform",
            "version": "1.0.0",
        }, 200

    return app
