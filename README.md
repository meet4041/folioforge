# FolioForge

FolioForge is a PDF-to-portfolio generator that turns a resume PDF into a polished, multi-page portfolio site. The repo now supports:

- command-line generation for local use
- a production-ready Python API backend for Render
- a static upload frontend for Vercel

## Architecture

- `script.py`: local CLI generator
- `web_app.py`: Flask API backend for uploads and generated portfolio hosting
- `frontend/`: static frontend that uploads PDFs to the backend
- `portfolio_renderer.py`: multi-page portfolio generator
- `resume_parser.py`: PDF parsing and section extraction

## Requirements

Install backend dependencies:

```bash
pip install -r requirements.txt
```

## Local Development

Generate a portfolio from a PDF with the CLI:

```bash
python script.py path-to-resume.pdf
```

Run the backend locally:

```bash
python web_app.py
```

The API will start on:

```text
http://127.0.0.1:8000
```

Open the frontend by serving the repo statically, or open:

```text
frontend/index.html
```

The frontend uses `frontend/config.js`, which defaults to `http://127.0.0.1:8000`.

## Backend API

### `GET /api/health`

Returns API health status.

### `POST /api/generate`

Upload a PDF in multipart form-data using the `resume` field.

Successful response:

```json
{
  "job_id": "generated-id",
  "portfolio_url": "https://your-render-service.onrender.com/portfolios/generated-id/index.html",
  "index_path": "generated-id/index.html",
  "expires_in_hours": 24
}
```

## Production Deployment

### Render Backend

This repo includes `render.yaml` for the API service. Render’s Python deployment docs use:

- build command: `pip install -r requirements.txt`
- start command: `gunicorn ...`

Reference: [Render deploy docs](https://render.com/docs/deploy-flask)

Steps:

1. Push this repo to GitHub.
2. Create a new Render Web Service from the repo.
3. Render should pick up `render.yaml`.
4. In Render, attach a persistent disk and mount it at:

```text
/opt/render/project/src/storage
```

Render documents that files are ephemeral by default unless you use a persistent disk. Reference: [Render persistent disks](https://render.com/docs/disks)

5. Set `ALLOWED_ORIGINS` to your Vercel frontend URL.
6. Deploy and copy your Render service URL.

### Vercel Frontend

This repo includes:

- `frontend/index.html`
- `frontend/styles.css`
- `frontend/app.js`
- `vercel.json`

Steps:

1. Import the repo into Vercel.
2. Deploy it as a static site.
3. Update `frontend/config.js` so `window.FOLIOFORGE_API_BASE` points to your Render backend URL.
4. Redeploy Vercel after that change.

Example:

```js
window.FOLIOFORGE_API_BASE = "https://your-render-service.onrender.com";
```

## Environment Variables

Backend variables:

- `PORT`: provided by Render automatically
- `HOST`: optional, defaults to `0.0.0.0`
- `DATA_DIR`: storage directory for uploads and generated portfolios
- `MAX_UPLOAD_MB`: upload size limit in megabytes
- `PORTFOLIO_TTL_HOURS`: how long generated jobs are kept
- `ALLOWED_ORIGINS`: comma-separated list of allowed frontend origins

## Notes

- Generated portfolios are stored per upload using a unique job ID.
- Old uploads and generated sites are cleaned up automatically based on `PORTFOLIO_TTL_HOURS`.
- For a larger-scale product, moving uploads and generated outputs to object storage would be stronger than relying only on disk-backed local storage.

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE).
