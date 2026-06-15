import html
from email.parser import BytesParser
from email.policy import default
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from portfolio_renderer import generate_site
from resume_parser import parse_resume

HOST = "127.0.0.1"
PORT = 8000
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploaded_resumes"
OUTPUT_DIR = BASE_DIR / "generated_portfolio"


def render_upload_page(message: str = "") -> str:
    status = f'<p class="status">{html.escape(message)}</p>' if message else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FolioForge Upload</title>
    <style>
        *{{box-sizing:border-box}}
        :root{{
            --bg:#f6f7f2;
            --bg-soft:#edf1e8;
            --panel:#ffffff;
            --panel-edge:rgba(17,24,39,.08);
            --text:#1f2937;
            --muted:rgba(31,41,55,.68);
            --soft:rgba(31,41,55,.52);
            --accent:#1f8a70;
            --accent-strong:#166a56;
            --accent-soft:rgba(31,138,112,.10);
            --line:rgba(31,138,112,.20);
            --shadow:0 20px 50px rgba(22,106,86,.10);
        }}
        body{{
            margin:0;
            min-height:100vh;
            display:grid;
            place-items:center;
            padding:24px 16px;
            color:var(--text);
            background:
                radial-gradient(circle at 15% 18%, rgba(31,138,112,.08), transparent 22%),
                radial-gradient(circle at 82% 24%, rgba(154,205,50,.08), transparent 18%),
                radial-gradient(circle at 50% 100%, rgba(255,255,255,.8), transparent 24%),
                linear-gradient(180deg, var(--bg) 0%, var(--bg-soft) 100%);
            font-family:"Inter","Segoe UI",Arial,sans-serif;
            overflow:hidden;
        }}
        body::before,
        body::after{{
            content:"";
            position:fixed;
            border-radius:999px;
            filter:blur(50px);
            pointer-events:none;
        }}
        body::before{{
            width:260px;
            height:260px;
            background:rgba(31,138,112,.08);
            top:-60px;
            left:-40px;
        }}
        body::after{{
            width:220px;
            height:220px;
            background:rgba(154,205,50,.08);
            right:-40px;
            bottom:-40px;
        }}
        .panel{{
            width:min(460px, 100%);
            border:1.5px solid rgba(31,138,112,.22);
            background:
                linear-gradient(180deg, rgba(255,255,255,.96), rgba(255,255,255,.92)),
                var(--panel);
            backdrop-filter:blur(14px);
            border-radius:24px;
            box-shadow:var(--shadow);
            padding:0;
            overflow:hidden;
            position:relative;
        }}
        .panel::before{{
            content:"";
            position:absolute;
            inset:0;
            background:linear-gradient(135deg, rgba(31,138,112,.04), transparent 34%, transparent 66%, rgba(154,205,50,.04));
            pointer-events:none;
        }}
        .layout{{
            display:block;
            position:relative;
            z-index:1;
        }}
        .hero,
        .form-shell{{padding:12px 18px}}
        .hero{{border-bottom:1px solid rgba(255,255,255,.06);text-align:center}}
        .brand-logo{{
            width:min(280px, 84%);
            height:auto;
            display:block;
            margin:0 auto 0;
            object-fit:contain;
        }}
        h1{{
            margin:0 0 2px;
            font-family:"Georgia","Times New Roman",serif;
            font-size:clamp(1.25rem, 4vw, 1.55rem);
            line-height:1.02;
            letter-spacing:-.03em;
        }}
        p{{margin:0;color:var(--muted);line-height:1.65}}
        .intro{{max-width:none;font-size:.92rem;margin:0 auto;text-align:center;white-space:nowrap}}
        .form-shell{{
            display:flex;
            flex-direction:column;
            justify-content:center;
            gap:8px;
        }}
        .form-card{{
            padding:0;
            border-radius:0;
            border:0;
            background:transparent;
        }}
        .form-card h2{{
            margin:0 0 4px;
            font-family:"Georgia","Times New Roman",serif;
            font-size:1.05rem;
            font-weight:600;
        }}
        .form-copy{{
            color:var(--soft);
            font-size:.86rem;
        }}
        .status{{
            margin-top:12px;
            padding:12px 14px;
            border-radius:14px;
            background:rgba(47,143,131,.08);
            border:1px solid var(--line);
            color:var(--accent);
            font-size:.95rem;
        }}
        form{{display:grid;gap:12px;margin-top:14px}}
        .dropzone{{
            display:grid;
            gap:8px;
            padding:16px;
            border:1px dashed var(--line);
            border-radius:16px;
            background:linear-gradient(180deg, #fcfcfd, #f7f8fb);
            text-align:left;
            transition:border-color .2s ease, transform .2s ease, background .2s ease;
        }}
        .dropzone:hover{{
            border-color:rgba(47,143,131,.35);
            transform:translateY(-1px);
        }}
        .dropzone strong{{
            font-size:.95rem;
            color:var(--text);
        }}
        .row{{
            display:flex;
            align-items:center;
            gap:12px;
            flex-wrap:wrap;
        }}
        input[type="file"]{{
            position:absolute;
            width:1px;
            height:1px;
            padding:0;
            margin:-1px;
            overflow:hidden;
            clip:rect(0, 0, 0, 0);
            border:0;
        }}
        .file-button{{
            display:inline-flex;
            align-items:center;
            justify-content:center;
            min-height:38px;
            padding:0 14px;
            border-radius:12px;
            border:1px solid var(--line);
            background:#fff;
            color:var(--text);
            font-weight:600;
            cursor:pointer;
        }}
        .file-name{{
            font-size:.88rem;
            color:var(--muted);
            overflow-wrap:anywhere;
        }}
        button{{
            width:100%;
            min-height:44px;
            padding:0 18px;
            border-radius:14px;
            border:0;
            background:linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%);
            color:#fff;
            font-weight:700;
            font-size:.92rem;
            cursor:pointer;
            box-shadow:0 10px 24px rgba(47,143,131,.22);
        }}
        button:hover{{transform:translateY(-1px)}}
        .note{{font-size:.94rem;color:var(--muted)}}
        @media (max-width: 640px){{
            body{{padding:18px}}
            .hero,
            .form-shell{{padding:12px 16px}}
            h1{{font-size:clamp(1.15rem, 8vw, 1.4rem)}}
            .eyebrow{{font-size:1.45rem}}
            .dropzone{{padding:16px}}
            .row{{align-items:flex-start;flex-direction:column}}
        }}
    </style>
</head>
<body>
    <main class="panel">
        <div class="layout">
            <section class="hero">
                <div>
                    <img src="/logo.png" alt="FolioForge logo" class="brand-logo">
                    <h1>Upload CV</h1>
                    <p class="intro">Turn your resume PDF into a portfolio site.</p>
                </div>
            </section>
            <section class="form-shell">
                <div class="form-card">
                    <h2>Select file</h2>
                    <p class="form-copy">Choose one PDF and generate instantly.</p>
                    <form method="post" action="/upload" enctype="multipart/form-data" target="_blank">
                        <label class="dropzone">
                            <div class="row">
                                <span class="file-button">Browse file</span>
                                <span class="file-name" id="file-name">No file selected</span>
                            </div>
                            <input type="file" name="resume" accept=".pdf,application/pdf" required>
                        </label>
                        <button type="submit">Generate Portfolio</button>
                    </form>
                    {status}
                </div>
            </section>
        </div>
    </main>
    <script>
        (function() {{
            const input = document.querySelector('input[type="file"]');
            const nameBox = document.getElementById('file-name');
            if (!input || !nameBox) return;
            input.addEventListener('change', function() {{
                const file = input.files && input.files[0];
                nameBox.textContent = file ? file.name : 'No file selected';
            }});
        }})();
    </script>
</body>
</html>
"""


def clean_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_uploaded_pdf(filename: str, payload: bytes) -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = Path(filename).name or "resume.pdf"
    if not safe_name.lower().endswith(".pdf"):
        safe_name = f"{safe_name}.pdf"
    target = UPLOAD_DIR / safe_name
    target.write_bytes(payload)
    return target


def generate_portfolio_from_pdf(pdf_path: Path, output_dir: Path = OUTPUT_DIR) -> Path:
    clean_output_dir(output_dir)
    data = parse_resume(pdf_path)
    generate_site(data, output_dir)
    return output_dir / "index.html"


class PortfolioHandler(BaseHTTPRequestHandler):
    server_version = "FolioForgeHTTP/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_html(render_upload_page())
            return

        if parsed.path == "/logo.png":
            file_path = BASE_DIR / "logo.png"
            if not file_path.exists():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self.send_file(file_path)
            return

        if parsed.path.startswith("/portfolio/"):
            relative = parsed.path.removeprefix("/portfolio/")
            file_path = (OUTPUT_DIR / relative).resolve()
            if OUTPUT_DIR.resolve() not in file_path.parents and file_path != OUTPUT_DIR.resolve():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            if not file_path.exists() or not file_path.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self.send_file(file_path)
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/upload":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type.lower():
            self.send_html(render_upload_page("Upload failed: invalid form data."), status=HTTPStatus.BAD_REQUEST)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        payload = self.rfile.read(content_length)
        filename, file_bytes = self._extract_uploaded_file(payload, content_type)

        if not filename or not file_bytes:
            self.send_html(render_upload_page("Please choose a PDF file before submitting."), status=HTTPStatus.BAD_REQUEST)
            return
        if not filename.lower().endswith(".pdf"):
            self.send_html(render_upload_page("Only PDF files are supported."), status=HTTPStatus.BAD_REQUEST)
            return

        try:
            saved_pdf = save_uploaded_pdf(filename, file_bytes)
            generate_portfolio_from_pdf(saved_pdf)
        except Exception as exc:
            self.send_html(render_upload_page(f"Generation failed: {exc}"), status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", "/portfolio/index.html")
        self.end_headers()

    def send_html(self, body: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def send_file(self, file_path: Path) -> None:
        suffix = file_path.suffix.lower()
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".svg": "image/svg+xml; charset=utf-8",
        }.get(suffix, "application/octet-stream")
        payload = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _extract_uploaded_file(self, payload: bytes, content_type: str) -> tuple[str, bytes]:
        message = BytesParser(policy=default).parsebytes(
            f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8") + payload
        )
        for part in message.iter_parts():
            if part.get_content_disposition() != "form-data":
                continue
            if part.get_param("name", header="content-disposition") != "resume":
                continue
            filename = part.get_filename() or ""
            file_bytes = part.get_payload(decode=True) or b""
            return filename, file_bytes
        return "", b""


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), PortfolioHandler)
    print(f"Open http://{HOST}:{PORT} in your browser")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
