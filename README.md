# DevSecOps Vulnerable Notes App

A deliberately vulnerable Flask application for a **controlled, instructor-led DevSecOps workshop**. Participants can scan it, identify weaknesses, and progressively remediate them in a CI/CD pipeline.

> **Safety notice:** This app is intentionally insecure. Run it only on your own machine or an isolated workshop environment. Do not expose it to the public internet, use real credentials, or store real data. Debug mode is enabled intentionally.

## Run locally

Requirements: Python 3.9+.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

Demo login:
- Username: `student`
- Password: `student123`

The app creates `workshop.db` on first run. Keep the app bound to localhost if you adapt the run command; do not expose this training app publicly.

## Run with Docker

```bash
docker build -t vulnerable-notes:workshop .
docker run --rm -p 127.0.0.1:5000:5000 vulnerable-notes:workshop
```

The included Dockerfile and Compose configuration contain intentional misconfigurations for scanning. Avoid using `docker-compose.yml` on a shared or production host.

## Workshop challenge map

| Area | Intentionally introduced issue | Suggested tool / check |
|---|---|---|
| `app.py` | Hardcoded app secret and demo admin credentials | Gitleaks / secret scanning |
| `/login` | SQL query built by concatenating user input | SonarQube / SAST |
| `/search` | User input rendered as HTML without escaping | SAST / secure code review |
| `/notes` | User-controlled owner selector; broken access control | Manual review / DAST |
| `requirements.txt` | Older dependency versions | Dependency-Check / pip-audit |
| `Dockerfile` | Old base image and root execution | Hadolint / Trivy |
| `docker-compose.yml` | Privileged container | Container configuration review |
| `k8s/deployment.yaml` | Privileged container and missing pod hardening | Kubescape / Checkov |

## Suggested workshop flow

1. Run the app locally and inspect the source.
2. Run secret scanning and identify committed credentials.
3. Run SAST and review the SQL injection and XSS findings.
4. Scan dependencies and the container image.
5. Review Docker and Kubernetes configuration.
6. Fix the findings and rerun the pipeline.
7. Configure the pipeline to fail when agreed security gates are not met.

## Important

This repository is a teaching fixture, not a production starter template. The vulnerabilities are intentionally present and should be removed before any deployment. The GitHub Actions workflow is only a basic syntax/install check; participants are expected to add security scanning stages during the workshop.
