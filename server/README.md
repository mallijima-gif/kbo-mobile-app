# KBO Mobile API Server

FastAPI server for the mobile-only KBO app.

## Local run

```bash
cd server
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API

- `GET /health`
- `GET /api/v1/schedules`
- `GET /api/v1/standings`
- `GET /api/v1/players`

## Render deploy

This repository includes [render.yaml](C:\Users\malli\OneDrive\Desktop\야구어플\render.yaml), so Render can create the web service automatically.

### 1. Push this project to GitHub

Render deploys from a Git repository, so the project needs to be in GitHub first.

### 2. Create the service in Render

1. Sign in to Render.
2. Choose `New +` -> `Blueprint`.
3. Select the GitHub repository that contains this project.
4. Render will detect `render.yaml`.
5. Create the service as-is.

### 3. Wait for first deploy

Render will run:

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The server should come up at a URL like:

```text
https://kbo-mobile-api.onrender.com
```

### 4. Verify the deployed server

Open these in a browser:

- `/health`
- `/api/v1/standings`
- `/api/v1/players`
- `/api/v1/schedules`

Example:

```text
https://kbo-mobile-api.onrender.com/health
```

If the response is `{"status":"ok"}`, deployment succeeded.

## Notes

- Responses are cached for 5 minutes to keep the app fast.
- If live parsing fails, the server returns sample data with `"source": "sample"`.
- Render free web services can sleep when idle, so the first request after inactivity may be slow.
