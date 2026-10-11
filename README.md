# Student Academic Management Platform

A Python Flask application developed as a DevOps mini project.

## Technology Stack

- Python 3.11
- Flask
- Pytest and pytest-cov
- Jenkins
- Docker
- Kubernetes / Minikube

## Run Locally

Create and activate a Python 3.11 virtual environment, then install dependencies:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Health Check

Open `http://127.0.0.1:5000/health` when running locally.

## Project Scope

The student implementation will cover student and faculty records, course
management, semester enrollment validation, grade management, and GPA
calculation, followed by automated testing and CI/CD deployment.
