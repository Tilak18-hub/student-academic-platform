from flask import Flask


def create_app():
    app = Flask(__name__)

    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/health")
    def health():
        return {
            "status": "UP",
            "service": "Student Academic Management Platform",
            "version": "1.0.0",
        }, 200

    return app
