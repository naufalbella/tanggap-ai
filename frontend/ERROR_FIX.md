# Frontend Error Fix - Documentation

## Problem

Frontend mengalami error saat di-deploy ke Cloud Run:

1. **Error 405** pada `/api/analyze` - Method Not Allowed
2. **Parse Error** pada `/api/query` - Unexpected token '<'

## Root Cause

Frontend mencoba mengakses backend menggunakan **same-origin** (empty string) yang berarti request dikirim ke nginx server frontend sendiri, bukan ke backend API service yang terpisah.

```javascript
// MASALAH: Production menggunakan empty string (same origin)
API_BASE_URL: window.location.hostname === "localhost"
    ? "http://localhost:8080"
    : "", // ❌ Ini salah untuk Cloud Run
```

Di Cloud Run, frontend dan backend adalah **service terpisah** dengan URL berbeda:

-   Frontend: `https://tanggap-ai-frontend-xxx.run.app`
-   Backend: `https://tanggap-ai-backend-xxx.run.app`

## Solution

### 1. Buat file `config.js` terpisah

File ini akan di-generate saat deployment dengan backend URL yang benar:

```javascript
// config.js
window.BACKEND_URL = "https://tanggap-ai-backend-xxx.run.app";
```

### 2. Update `app.js` untuk menggunakan `window.BACKEND_URL`

```javascript
const CONFIG = {
    API_BASE_URL:
        window.location.hostname === "localhost"
            ? "http://localhost:8080"
            : window.BACKEND_URL || "",
};
```

### 3. Include `config.js` di `index.html`

```html
<!-- Load config first, then app -->
<script src="config.js"></script>
<script src="app.js"></script>
```

### 4. Update `deploy.sh` untuk generate `config.js`

```bash
# Get Backend URL
export BACKEND_URL=$(gcloud run services describe tanggap-ai-backend \
    --region=europe-west1 \
    --format='value(status.url)')

# Create config.js file
cat > config.js << EOF
window.BACKEND_URL = '${BACKEND_URL}';
EOF
```

### 5. Update `Dockerfile` untuk copy `config.js`

```dockerfile
COPY config.js /usr/share/nginx/html/config.js
```

## Files Changed

1. ✅ `frontend/config.js` - Baru
2. ✅ `frontend/app.js` - Updated
3. ✅ `frontend/index.html` - Updated (include config.js)
4. ✅ `frontend/deploy.sh` - Updated (generate config.js)
5. ✅ `frontend/Dockerfile` - Updated (copy config.js)

## How It Works

### Local Development

1. `config.js` contains: `window.BACKEND_URL = 'http://localhost:8080'`
2. Frontend connects to local backend on port 8080
3. Test dengan: `python -m http.server 3000`

### Production Deployment

1. `deploy.sh` gets backend URL dari Cloud Run
2. Generates `config.js` with production backend URL
3. Dockerfile copies `config.js` to container
4. Frontend connects to correct backend service

## Testing

### 1. Verify Configuration

```bash
cd frontend
./test-config.sh
```

### 2. Test Locally

```bash
# Terminal 1: Start backend
cd backend
python -m app.main

# Terminal 2: Start frontend
cd frontend
python -m http.server 3000

# Open browser
open http://localhost:3000
```

### 3. Test Production

```bash
# Deploy
cd frontend
./deploy.sh

# Get URL
export FRONTEND_URL=$(gcloud run services describe tanggap-ai-frontend \
  --region=europe-west1 --format='value(status.url)')

# Open in browser
open $FRONTEND_URL
```

## Expected Behavior

### ✅ Analyze Feedback

1. Enter feedback text
2. Click "Analyze Feedback"
3. See results with sentiment, category, priority, etc.
4. No more 405 errors

### ✅ View History

1. History table loads automatically
2. Shows past analyses
3. Filters work (sentiment, category)
4. No more parse errors

## Troubleshooting

### Still getting 405 errors?

Check `config.js` in browser DevTools:

```javascript
// Open browser console
console.log(window.BACKEND_URL);
// Should show: https://tanggap-ai-backend-xxx.run.app
```

### Backend URL not set?

Re-deploy with correct config:

```bash
cd frontend
./deploy.sh  # This will regenerate config.js
```

### CORS errors?

Backend already has CORS enabled. Check:

1. Backend is running: `curl BACKEND_URL/health`
2. CORS headers present in response
3. Frontend URL is accessible

## Summary

✅ **Problem Fixed**: Frontend now correctly connects to backend service
✅ **Solution**: Use external `config.js` with backend URL
✅ **Deployment**: Automated via `deploy.sh`
✅ **Testing**: Works both locally and in production

The error was caused by trying to use same-origin requests in a multi-service Cloud Run environment. The solution uses a configuration file that's generated during deployment with the correct backend URL.
