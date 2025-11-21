# MED ZOOM-AI

Medical consultation platform with AI assistance.

## Deploy to Render

To deploy this application to Render for public access:

1. Follow the instructions in [DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md)
2. Use the [render.yaml](render.yaml) configuration file for automatic deployment

## Setup Instructions

1. Install dependencies:
   ```
   npm install
   ```

2. Create a `.env` file in the Backend directory with your MongoDB URI, JWT secret, and email credentials:
   ```
   MONGO_URI=your_mongodb_uri
   JWT_SECRET=your_jwt_secret
   EMAIL_ADDRESS=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   ```

3. Run the backend:
   ```
   python app.py
   ```

4. Run the frontend:
   ```
   npm run dev
   ```

## Accessing the Application on Local Network

To access your application from devices connected to the same WiFi network:

1. **Find your computer's IP address**:
   - On Windows, open Command Prompt and run `ipconfig`
   - Look for "IPv4 Address" under your active network connection

2. **Access the application**:
   - On your computer: Visit `http://localhost:5174`
   - On other devices on the same network: Visit `http://YOUR_IP_ADDRESS:5174`
   - Example: If your IP is 192.168.1.100, visit `http://192.168.1.100:5174`

3. **Backend API**:
   - The backend API is accessible at `http://YOUR_IP_ADDRESS:3002`
   - All data is stored in MongoDB Atlas (cloud database)

### Security Considerations

1. Change the JWT secret in your `.env` file to a strong random string
2. Ensure your MongoDB connection uses SSL/TLS
3. For production use, consider using a reverse proxy like Nginx with SSL termination

### Data Storage

All data is stored in MongoDB Atlas (cloud database) as configured in your `.env` file:
```
MONGO_URI="mongodb+srv://username:password@cluster0.pk04lhx.mongodb.net/medzoom"
```

User data is securely stored with bcrypt-hashed passwords and JWT-based authentication.

## Components

- **Frontend**: React/Vite application in `loginreg/`
- **Backend**: Flask API in `Backend/`

## Features

- User authentication (signup/login/logout)
- Email verification with OTP
- Secure password storage
- Session management