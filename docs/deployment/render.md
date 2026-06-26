# Render Deployment Guide

## Preview Environments
The repository supports automated preview deployments for feature branches.

### Blueprint
Use `render.preview.yaml` to define the isolated services.

### Services
*   **flowforge-backend-preview**: FastAPI web service.
*   **flowforge-frontend-preview**: React static site.

### Environment Variables
#### Backend
*   `MONGO_URL`: Connection string for the preview database.
*   `DB_NAME`: `flowforge_ai_preview`
*   `SECRET_KEY`: Random string for JWT.
*   `BACKEND_CORS_ORIGINS`: JSON list containing the frontend preview URL.

#### Frontend
*   `REACT_APP_BACKEND_URL`: Public URL of the backend preview service.

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
