# MED ZOOM-AI - Render Deployment Health Check

This document provides information about the health check endpoints for your deployed application.

## Backend Health Check

Endpoint: `/health`

Returns:
```json
{
  "status": "healthy",
  "timestamp": "ISO formatted timestamp"
}
```

## Frontend Health Check

The frontend doesn't have a dedicated health check endpoint, but you can verify it's working by accessing the main page.

## Monitoring on Render

Render automatically monitors your services:

1. **Backend Service**:
   - Health check interval: Every 30 seconds
   - Timeout: 5 seconds
   - Restart policy: Automatic restart on failure

2. **Frontend Service**:
   - Static sites are served directly from Render's CDN
   - High availability with automatic failover

## Custom Health Checks

If you need more advanced health checking, you can:

1. Add additional endpoints to your backend in `app.py`
2. Configure custom health check paths in the Render dashboard
3. Set up notifications for downtime alerts

## Logs and Debugging

View logs in real-time from the Render dashboard:
- Backend logs show Python/Flask application output
- Frontend logs show build process and CDN events

Common log entries to look for:
- Database connection successes/failures
- Email sending successes/failures
- User authentication events
- API request/response patterns