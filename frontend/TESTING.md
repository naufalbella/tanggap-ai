# TanggapAI Frontend - Local Testing Guide

## Quick Start for Local Testing

### 1. Start Backend First

Make sure your backend is running on port 8080:

```bash
cd ../backend
export GOOGLE_CLOUD_PROJECT=your-project-id
export AGENT_URL=http://localhost:8080
python -m app.main
```

### 2. Start Frontend

In a new terminal:

```bash
cd frontend
python -m http.server 3000
```

### 3. Open Browser

Navigate to: http://localhost:3000

## Testing Checklist

-   [ ] Form submission works
-   [ ] Analysis results display correctly
-   [ ] History table loads
-   [ ] Sentiment filter works
-   [ ] Category filter works
-   [ ] Refresh button works
-   [ ] Error messages display correctly
-   [ ] Mobile responsive design works

## Common Issues

### Issue: "Failed to analyze feedback"

**Solution**: Check that backend is running on port 8080

```bash
curl http://localhost:8080/health
```

### Issue: "Failed to load history"

**Solution**:

1. Check BigQuery connection
2. Verify backend has access to BigQuery
3. Check console for specific error

### Issue: CORS errors

**Solution**: Backend already has CORS enabled. If you still see errors:

```python
# In backend/app/main.py, verify:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should be present
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Test Data

Try these sample feedbacks:

1. **Positive**: "Product quality is excellent, very satisfied!"
2. **Negative**: "Delivery was 3 days late, very disappointed"
3. **Technical**: "Website is slow during peak hours"
4. **Payment**: "Payment failed multiple times"
5. **Service**: "Customer service was very helpful"

## Browser Developer Tools

Open DevTools (F12) to:

1. **Console**: Check for JavaScript errors
2. **Network**: Monitor API requests
3. **Application**: Check if running in correct mode

## Production Testing

After deploying:

```bash
# Get frontend URL
export FRONTEND_URL=$(gcloud run services describe tanggap-ai-frontend \
  --region=europe-west1 --format='value(status.url)')

# Test frontend
open $FRONTEND_URL

# Check health
curl $FRONTEND_URL/health
```

## Performance Testing

Test with various feedback lengths:

-   Short (< 50 chars)
-   Medium (50-200 chars)
-   Long (> 200 chars)

Monitor:

-   Response time
-   Loading states
-   Error handling
