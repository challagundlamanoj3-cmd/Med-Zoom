# Deployment Guide for Local Network Access

This guide explains how to make your MED ZOOM-AI application accessible from devices connected to the same WiFi network while keeping data stored in MongoDB Atlas cloud database.

## Prerequisites

1. Your laptop running Windows 25H2
2. Stable internet connection
3. Devices connected to the same WiFi network
4. MongoDB Atlas account (already configured)

## Step-by-Step Deployment

### 1. Prepare Your Application

Ensure your backend is configured to listen on all interfaces:
```python
# In Backend/app.py
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3002, debug=True)
```

### 2. Configure Your Network

1. **Find your computer's IP address**
   - Open Command Prompt and run `ipconfig`
   - Look for "IPv4 Address" under your active network connection
   - Example: 192.168.1.100

2. **Update frontend configuration**
   - Edit `loginreg/.env`
   - Set: `VITE_API_BASE_URL=http://YOUR_IP_ADDRESS:3002`
   - Example: `VITE_API_BASE_URL=http://192.168.1.100:3002`

3. **Run your backend**
   ```bash
   cd Backend
   python app.py
   ```

4. **Run your frontend**
   ```bash
   cd loginreg
   npm run dev
   ```

### 3. Security Recommendations

1. **Change your JWT secret**
   - In `Backend/.env`, update `JWT_SECRET` to a strong random string

2. **Secure MongoDB connection**
   - Ensure your MongoDB URI uses SSL/TLS
   - Your current URI already includes `ssl=true`

3. **Consider rate limiting**
   - Add rate limiting middleware to your Flask app to prevent abuse

4. **Use HTTPS in production**
   - For permanent deployment, consider using a reverse proxy like Nginx with Let's Encrypt SSL certificates

### 4. Data Storage Information

Your application stores data in MongoDB Atlas, not locally on your laptop:
- Database: MongoDB Atlas cluster
- Connection: Secure TLS connection
- Location: Cloud database (not on your physical machine)
- Redundancy: Automatically replicated across multiple servers

### 5. Testing Local Network Access

1. **Local testing**
   - Visit http://localhost:5174 to test locally

2. **Network testing**
   - From another device on the same network, visit `http://YOUR_LOCAL_IP:5174`
   - Find your local IP with `ipconfig` (Windows) or `ifconfig` (Mac/Linux)

### 6. Troubleshooting

**Issue: Cannot access from other devices on the network**
- Verify your computer's firewall allows incoming connections on ports 3002 and 5174
- Ensure all devices are connected to the same WiFi network
- Check that the backend and frontend applications are running

**Issue: Connection timeouts**
- Confirm your laptop's firewall allows incoming connections on ports 3002 and 5174
- Check that the backend is actually running
- Verify your IP address hasn't changed

**Issue: CORS errors**
- The backend is already configured to accept requests from any origin

## Maintenance

1. **Monitor your IP address**
   - IP addresses may change when you reconnect to WiFi
   - Check your IP address each time you want to access the application

2. **Keep applications running**
   - Use process managers like PM2 for Node.js or systemd services for Python
   - Consider using task scheduler to auto-start applications on boot

3. **Regular backups**
   - MongoDB Atlas provides automatic backups
   - Regularly backup your code and configuration files

By following this guide, your MED ZOOM-AI application will be accessible from any device connected to your local WiFi network while keeping your data securely stored in MongoDB Atlas cloud database.