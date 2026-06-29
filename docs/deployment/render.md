# Render Deployment Guide

## Preview Environments
The repository supports automated preview deployments for feature branches.

### Blueprint
Use `render.preview.yaml` to define the isolated services.

### Services
*   **flowforge-backend-preview**: FastAPI web service.
*   **flowforge-frontend-preview**: React static site.

### Health and Readiness
The backend provides two diagnostic endpoints:
*   `/api/health`: General health check, returns 503 if database is disconnected.
*   `/api/ready`: Readiness probe used by Render, returns 503 if database is disconnected.

### Environment Variables
#### Backend
*   `MONGO_URL`: Connection string for the preview database. **Note:** Use `mongodb+srv` for Atlas. Ensure special characters in the password are URL-encoded.
*   `DB_NAME`: `flowforge_ai_preview` (default for previews)
*   `SECRET_KEY`: Random string for JWT.
*   `BACKEND_CORS_ORIGINS`: Comma-separated list or JSON list containing the frontend preview URL.

#### Frontend
*   `REACT_APP_BACKEND_URL`: Public URL of the backend preview service (e.g., `https://flowforge-backend-preview.onrender.com`).

### MongoDB Connection Troubleshooting
If registration fails with "Service is temporarily unavailable", check the Render logs for "Bad auth" or "Connection timeout".

To verify credentials from the backend environment, run:
```bash
python scripts/verify_mongodb.py
```
This script will safely test connection, authentication, and write access without exposing your `MONGO_URL`.

### Bootstrap Procedure
To establish the first Platform Owner in the preview environment:
1. Register a user via the frontend.
2. Run the bootstrap script in the backend environment:
   ```bash
   python scripts/bootstrap_owner.py <email>
   ```

### Verification
Run the automated smoke test:
```bash
export FLOWFORGE_BACKEND_URL="https://your-backend.onrender.com"
python scripts/smoke_test.py
```
