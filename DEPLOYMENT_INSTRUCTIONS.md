# Deploying MED ZOOM-AI to Render

This guide will help you deploy your MED ZOOM-AI application to Render so it works on all laptops and devices.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. Your MongoDB Atlas connection string
3. Your email credentials for sending OTP emails

## Deployment Steps

### 1. Fork or Push Your Code to GitHub

Render deploys from Git repositories. You'll need to either:
- Push your code to a GitHub repository
- Fork this repository if it's already on GitHub

### 2. Create a New Web Service on Render

1. Go to your Render dashboard
2. Click "New+" and select "Web Service"
3. Connect your GitHub account and select your repository
4. Configure the service:
   - Name: `medzoom-backend`
   - Environment: Python 3
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --bind 0.0.0.0:$PORT Backend.app:app`
   - Branch: main (or master)

### 3. Configure Environment Variables for Backend

In the Render dashboard for your backend service, go to "Environment Variables" and add:

```
MONGO_URI=your_mongodb_connection_string
JWT_SECRET=your_secure_jwt_secret
EMAIL_ADDRESS=your_email_for_sending_otp
EMAIL_PASSWORD=your_email_app_password
```

### 4. Deploy the Frontend

1. Go back to your Render dashboard
2. Click "New+" and select "Static Site"
3. Connect the same GitHub repository
4. Configure the site:
   - Name: `medzoom-frontend`
   - Build command: `npm install && npm run build`
   - Publish directory: `dist`
   - Branch: main (or master)

### 5. Configure Environment Variables for Frontend

Add this environment variable for the frontend:

```
VITE_API_BASE_URL=https://med-zoom.onrender.com
```

(Note: You'll get the actual backend URL after deploying the backend service)

### 6. Update CORS Settings (if needed)

If you encounter CORS issues, you may need to update the CORS origins in `Backend/app.py` to include your frontend URL.

## Important Notes

1. **MongoDB Connection**: Make sure your MongoDB Atlas cluster allows connections from anywhere (0.0.0.0/0) or specifically from Render's IP ranges.

2. **Email Configuration**: Gmail requires app passwords for SMTP authentication. Make sure you've set this up correctly.

3. **First Deployment**: The first deployment may take a few minutes as Render provisions resources.

4. **Auto Scaling**: Render automatically scales your application based on traffic.

5. **Custom Domains**: You can configure custom domains in the Render dashboard after deployment.

## Troubleshooting

### Backend Issues
- Check logs in Render dashboard for error messages
- Ensure all environment variables are correctly set
- Verify MongoDB connection string works locally

### Frontend Issues
- Check that `VITE_API_BASE_URL` points to your deployed backend
- Verify CORS settings in the backend allow requests from your frontend

### Performance
- Initial requests to Render free tier apps may be slow as they spin down after inactivity
- Consider upgrading to a paid plan for production use

## Updating Your Application

To update your deployed application:
1. Push changes to your GitHub repository
2. Render will automatically detect changes and redeploy
3. Or manually trigger a deploy from the Render dashboard

Your MED ZOOM-AI application will now be accessible from any device with an internet connection!