import os
import shutil
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, request, send_file, send_from_directory
from werkzeug.utils import secure_filename

from portfolio_renderer import generate_site
from resume_parser import parse_resume

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
DEFAULT_DATA_DIR = BASE_DIR / "storage"
UPLOAD_DIR_NAME = "uploads"
PORTFOLIO_DIR_NAME = "portfolios"
DEFAULT_MAX_UPLOAD_MB = 10
DEFAULT_PORTFOLIO_TTL_HOURS = 24


def data_root() -> Path:
    configured = os.getenv("DATA_DIR")
    return Path(configured).expanduser().resolve() if configured else DEFAULT_DATA_DIR.resolve()


def uploads_root() -> Path:
    path = data_root() / UPLOAD_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def portfolios_root() -> Path:
    path = data_root() / PORTFOLIO_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "*").strip()
    if not raw:
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def max_upload_bytes() -> int:
    raw = os.getenv("MAX_UPLOAD_MB", str(DEFAULT_MAX_UPLOAD_MB))
    try:
        size_mb = max(1, int(raw))
    except ValueError:
        size_mb = DEFAULT_MAX_UPLOAD_MB
    return size_mb * 1024 * 1024


def portfolio_ttl_hours() -> int:
    raw = os.getenv("PORTFOLIO_TTL_HOURS", str(DEFAULT_PORTFOLIO_TTL_HOURS))
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_PORTFOLIO_TTL_HOURS


def cleanup_old_jobs() -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=portfolio_ttl_hours())
    for root in (uploads_root(), portfolios_root()):
        for child in root.iterdir():
            try:
                modified_at = datetime.fromtimestamp(child.stat().st_mtime, tz=timezone.utc)
            except FileNotFoundError:
                continue
            if modified_at >= cutoff:
                continue
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                child.unlink(missing_ok=True)


def reset_runtime_data() -> None:
    for root in (uploads_root(), portfolios_root()):
        for child in root.iterdir():
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                child.unlink(missing_ok=True)


def is_pdf_bytes(payload: bytes) -> bool:
    return payload.lstrip().startswith(b"%PDF")


def save_upload(job_id: str, filename: str, payload: bytes) -> Path:
    target_dir = uploads_root() / job_id
    target_dir.mkdir(parents=True, exist_ok=True)
    safe_name = secure_filename(filename) or "resume.pdf"
    if not safe_name.lower().endswith(".pdf"):
        safe_name = f"{safe_name}.pdf"
    target_path = target_dir / safe_name
    target_path.write_bytes(payload)
    return target_path


def portfolio_output_dir(job_id: str) -> Path:
    path = portfolios_root() / job_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def parsed_data_path(job_id: str) -> Path:
    return uploads_root() / job_id / "parsed.json"


def serialize_portfolio_data(data: dict) -> dict:
    return {
        "name": data.get("name", ""),
        "title": data.get("title", ""),
        "location": data.get("location", ""),
        "email": data.get("email", ""),
        "linkedin": data.get("linkedin", ""),
        "github": data.get("github", ""),
        "links": [str(item).strip() for item in data.get("links", []) if str(item).strip()],
        "summary": data.get("summary", ""),
        "education": [
            {
                "school": item.get("school", ""),
                "period": item.get("period", ""),
                "detail": item.get("detail", ""),
                "location": item.get("location", ""),
            }
            for item in data.get("education", [])
        ],
        "experience": [
            {
                "company": item.get("company", ""),
                "period": item.get("period", ""),
                "role": item.get("role", ""),
                "location": item.get("location", ""),
                "bullets": [str(bullet).strip() for bullet in item.get("bullets", []) if str(bullet).strip()],
            }
            for item in data.get("experience", [])
        ],
        "projects": [
            {
                "name": item.get("name", ""),
                "stack": item.get("stack", ""),
                "bullets": [str(bullet).strip() for bullet in item.get("bullets", []) if str(bullet).strip()],
            }
            for item in data.get("projects", [])
        ],
        "skills": {
            str(label).strip(): [str(item).strip() for item in values if str(item).strip()]
            for label, values in data.get("skills", {}).items()
            if str(label).strip()
        },
        "responsibility": {
            "title": data.get("responsibility", {}).get("title", ""),
            "period": data.get("responsibility", {}).get("period", ""),
            "org": data.get("responsibility", {}).get("org", ""),
            "bullets": [
                str(bullet).strip()
                for bullet in data.get("responsibility", {}).get("bullets", [])
                if str(bullet).strip()
            ],
        },
        "achievements": [str(item).strip() for item in data.get("achievements", []) if str(item).strip()],
    }


def normalize_portfolio_data(payload: dict) -> dict:
    serialized = serialize_portfolio_data(payload or {})
    if not serialized["title"]:
        serialized["title"] = "Portfolio"
    if not serialized["name"]:
        serialized["name"] = "Portfolio Owner"
    if not serialized["summary"]:
        serialized["summary"] = f"{serialized['name']} is a {serialized['title']}."
    return serialized


def save_parsed_data(job_id: str, data: dict) -> None:
    parsed_data_path(job_id).write_text(json.dumps(serialize_portfolio_data(data), indent=2), encoding="utf-8")


def load_parsed_data(job_id: str) -> dict:
    path = parsed_data_path(job_id)
    if not path.exists():
        raise FileNotFoundError("Parsed resume data was not found for this job.")
    return normalize_portfolio_data(json.loads(path.read_text(encoding="utf-8")))


def generate_portfolio(job_id: str, pdf_path: Path | None = None, data: dict | None = None) -> Path:
    output_dir = portfolio_output_dir(job_id)
    portfolio_data = normalize_portfolio_data(data) if data is not None else parse_resume(pdf_path)
    generate_site(portfolio_data, output_dir)
    return output_dir / "index.html"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = max_upload_bytes()

    def resolve_origin() -> str:
        origin = request.headers.get("Origin", "")
        origins = allowed_origins()
        if "*" in origins:
            return origin or "*"
        if origin and origin in origins:
            return origin
        return origins[0] if origins else "*"

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = resolve_origin()
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        response.headers["Vary"] = "Origin"
        return response

    @app.errorhandler(413)
    def payload_too_large(_error):
        return (
            jsonify(
                {
                    "error": "File too large.",
                    "max_upload_mb": max_upload_bytes() // (1024 * 1024),
                }
            ),
            413,
        )

    @app.get("/")
    def root():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.get("/api")
    def api_root():
        return jsonify(
            {
                "name": "FolioForge API",
                "status": "ok",
                "generate_endpoint": "/api/generate",
                "health_endpoint": "/api/health",
            }
        )

    @app.get("/styles.css")
    def frontend_styles():
        return send_from_directory(FRONTEND_DIR, "styles.css", mimetype="text/css")

    @app.get("/app.js")
    def frontend_app():
        return send_from_directory(FRONTEND_DIR, "app.js", mimetype="application/javascript")

    @app.get("/config.js")
    def frontend_config():
        return send_from_directory(FRONTEND_DIR, "config.js", mimetype="application/javascript")

    @app.get("/frontend-logo.png")
    def frontend_logo():
        return send_from_directory(FRONTEND_DIR, "logo.png", mimetype="image/png")

    @app.get("/api/health")
    def health():
        cleanup_old_jobs()
        return jsonify({"status": "ok"})

    @app.route("/api/parse", methods=["POST", "OPTIONS"])
    def parse_resume_preview():
        if request.method == "OPTIONS":
            return ("", 204)

        cleanup_old_jobs()

        upload = request.files.get("resume")
        if upload is None:
            return jsonify({"error": "Please upload a resume PDF in the `resume` field."}), 400

        filename = upload.filename or "resume.pdf"
        if not filename.lower().endswith(".pdf"):
            return jsonify({"error": "Only PDF files are supported."}), 400

        file_bytes = upload.read()
        if not file_bytes:
            return jsonify({"error": "Uploaded file is empty."}), 400
        if not is_pdf_bytes(file_bytes):
            return jsonify({"error": "The uploaded file does not look like a valid PDF."}), 400

        job_id = uuid4().hex
        saved_pdf = save_upload(job_id, filename, file_bytes)

        try:
            parsed_data = parse_resume(saved_pdf)
            save_parsed_data(job_id, parsed_data)
        except Exception as exc:
            shutil.rmtree(uploads_root() / job_id, ignore_errors=True)
            shutil.rmtree(portfolios_root() / job_id, ignore_errors=True)
            return jsonify({"error": f"Resume parsing failed: {exc}"}), 500

        return (
            jsonify(
                {
                    "job_id": job_id,
                    "data": serialize_portfolio_data(parsed_data),
                }
            ),
            201,
        )

    @app.route("/api/generate", methods=["POST", "OPTIONS"])
    def generate():
        if request.method == "OPTIONS":
            return ("", 204)

        cleanup_old_jobs()

        if request.is_json:
            payload = request.get_json(silent=True) or {}
            job_id = str(payload.get("job_id", "")).strip()
            if not job_id:
                return jsonify({"error": "A valid job_id is required to generate a reviewed portfolio."}), 400

            try:
                stored_data = load_parsed_data(job_id)
            except FileNotFoundError as exc:
                return jsonify({"error": str(exc)}), 404

            incoming_data = payload.get("data")
            portfolio_data = normalize_portfolio_data(incoming_data or stored_data)
            save_parsed_data(job_id, portfolio_data)

            try:
                index_file = generate_portfolio(job_id, data=portfolio_data)
            except Exception as exc:
                return jsonify({"error": f"Portfolio generation failed: {exc}"}), 500

            portfolio_url = f"{request.host_url}portfolios/{job_id}/index.html"
            return (
                jsonify(
                    {
                        "job_id": job_id,
                        "portfolio_url": portfolio_url,
                        "index_path": str(index_file.relative_to(portfolios_root())),
                        "expires_in_hours": portfolio_ttl_hours(),
                    }
                ),
                201,
            )

        upload = request.files.get("resume")
        if upload is None:
            return jsonify({"error": "Please upload a resume PDF in the `resume` field."}), 400

        filename = upload.filename or "resume.pdf"
        if not filename.lower().endswith(".pdf"):
            return jsonify({"error": "Only PDF files are supported."}), 400

        file_bytes = upload.read()
        if not file_bytes:
            return jsonify({"error": "Uploaded file is empty."}), 400
        if not is_pdf_bytes(file_bytes):
            return jsonify({"error": "The uploaded file does not look like a valid PDF."}), 400

        job_id = uuid4().hex
        saved_pdf = save_upload(job_id, filename, file_bytes)

        try:
            parsed_data = parse_resume(saved_pdf)
            save_parsed_data(job_id, parsed_data)
            index_file = generate_portfolio(job_id, data=parsed_data)
        except Exception as exc:
            shutil.rmtree(uploads_root() / job_id, ignore_errors=True)
            shutil.rmtree(portfolios_root() / job_id, ignore_errors=True)
            return jsonify({"error": f"Portfolio generation failed: {exc}"}), 500

        portfolio_url = f"{request.host_url}portfolios/{job_id}/index.html"
        return (
            jsonify(
                {
                    "job_id": job_id,
                    "portfolio_url": portfolio_url,
                    "index_path": str(index_file.relative_to(portfolios_root())),
                    "expires_in_hours": portfolio_ttl_hours(),
                }
            ),
            201,
        )

    @app.get("/portfolios/<job_id>/")
    def portfolio_index(job_id: str):
        return send_from_directory(portfolios_root() / job_id, "index.html")

    @app.get("/portfolios/<job_id>/<path:filename>")
    def portfolio_asset(job_id: str, filename: str):
        return send_from_directory(portfolios_root() / job_id, filename)

    @app.get("/logo.png")
    def logo():
        return send_file(BASE_DIR / "logo.png", mimetype="image/png")

    return app


app = create_app()


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reset_runtime_data()
    print(f"FolioForge API running on http://{host}:{port}")
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
