from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import bcrypt
import jwt
import datetime
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import random
import string

# ---------------- LOAD ENV ----------------
load_dotenv()

# ---------------- ENV VARIABLES ----------------
MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("JWT_SECRET")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

app = Flask(__name__)

client = MongoClient(MONGO_URI)
db = client["medzoom"]
users = db["users"]
otp_store = {}  # Use Redis in production

CORS(
    app,
    supports_credentials=True,
    origins=[
        "https://med-zoom-1.onrender.com"  # Production frontend
    ],
    allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Origin", "Access-Control-Allow-Credentials"],
    methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    expose_headers=["Access-Control-Allow-Credentials", "Access-Control-Allow-Origin"],
    max_age=86400
)

# ---------------- SEND OTP EMAIL ----------------
def send_otp_email(email, otp):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return False
    
    # Test email format
    if not email or "@" not in email:
        return False

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email
    msg["Subject"] = "MedZoom - Email Verification OTP"

    body = f"""
    <html>
        <body>
            <h2>Welcome to MedZoom!</h2>
            <p>Your OTP is:</p>
            <h1 style="color:green;">{otp}</h1>
            <p>This OTP expires in 10 minutes.</p>
        </body>
    </html>
    """

    msg.attach(MIMEText(body, "html"))

    # Try STARTTLS (Port 587)
    try:
        print("[SMTP] Connecting to smtp.gmail.com:587 (STARTTLS)...")
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()

        print("[SMTP] Logging in...", EMAIL_ADDRESS)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        print("[SMTP] Sending email...")
        server.send_message(msg)
        server.quit()

        print("[SMTP] Email successfully sent!")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"[SMTP ERROR] Authentication failed: {e}")
        print("→ Check App Password & 2-Step Verification")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"[SMTP ERROR] Recipient refused: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"[SMTP ERROR] SMTP Exception: {e}")
        return False
    except Exception as e:
        print(f"[SMTP ERROR] STARTTLS failed: {type(e).__name__}: {e}")
        print("Trying SSL fallback...")

    # Try SSL (Port 465)
    try:
        context = ssl.create_default_context()
        print("[SMTP] Connecting to smtp.gmail.com:465 (SSL)...")
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=15)

        print("[SMTP] Logging in...")
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        print("[SMTP] Sending email...")
        server.send_message(msg)
        server.quit()

        print("[SMTP] Email successfully sent via SSL!")
        return True

    except Exception as e:
        print(f"[SMTP ERROR] SSL failed: {type(e).__name__}: {e}")
        return False

# ---------------- GENERATE OTP ----------------
def generate_otp():
    return "".join(random.choices(string.digits, k=6))

# ---------------- HEALTH CHECK ENDPOINT ----------------
@app.route("/health", methods=["GET"])
def health_check():
    # Check environment variables
    env_check = {
        "MONGO_URI": bool(os.getenv("MONGO_URI")),
        "JWT_SECRET": bool(os.getenv("JWT_SECRET")),
        "EMAIL_ADDRESS": bool(os.getenv("EMAIL_ADDRESS")),
        "EMAIL_PASSWORD": bool(os.getenv("EMAIL_PASSWORD"))
    }
    
    # Check database connection
    db_status = "unknown"
    try:
        db.command('ping')
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Overall status
    overall_status = "healthy" if all(env_check.values()) and db_status == "connected" else "unhealthy"
    
    response = jsonify({
        "status": overall_status,
        "timestamp": datetime.datetime.utcnow(),
        "environment": env_check,
        "database": db_status,
        "service": "backend-running"
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    
    return response, 200 if overall_status == "healthy" else 500

# ---------------- SEND OTP ----------------
@app.route("/send-otp", methods=["POST"])
def send_otp():
    try:
        data = request.json

        if not data:
            return jsonify({"error": "Invalid request"}), 400

        email = data["email"]

        if users.find_one({"email": email}):
            return jsonify({"error": "Email already exists"}), 400

        otp = generate_otp()
        
        otp_store[email] = {
            "otp": otp,
            "expires": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        }

        success = send_otp_email(email, otp)
        
        if not success:
            response = jsonify({"error": "Failed to send OTP email. Please check your email address and try again."})
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response, 500
        
        response = jsonify({"message": "OTP sent successfully"})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    username = data["username"]
    email = data["email"]
    password = data["password"]
    otp = data["otp"]

    if users.find_one({"email": email}):
        return jsonify({"error": "Email exists"}), 400

    if users.find_one({"username": username}):
        return jsonify({"error": "Username taken"}), 400

    if email not in otp_store:
        return jsonify({"error": "OTP missing or expired"}), 400

    if datetime.datetime.utcnow() > otp_store[email]["expires"]:
        del otp_store[email]
        return jsonify({"error": "OTP expired"}), 400

    if otp_store[email]["otp"] != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    del otp_store[email]

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    users.insert_one({
        "username": username,
        "email": email,
        "password": hashed_pw
    })

    response = jsonify({"message": "User created"})
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response, 201

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data:
        return jsonify("Invalid request"), 400

    username = data["username"]
    password = data["password"]

    user = users.find_one({"username": username})
    if not user:
        return jsonify("User does not exist"), 400

    if not bcrypt.checkpw(password.encode(), user["password"]):
        return jsonify("Incorrect password"), 400

    token = jwt.encode(
        {
            "user_id": str(user["_id"]),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
        },
        JWT_SECRET,
        algorithm="HS256"
    )

    resp = make_response(jsonify("Success"))
    # Configure cookie for production deployment
    cookie_kwargs = {
        "httponly": True,
        "samesite": "None",
        "secure": True  # Should be True in production
    }
    
    # For local development, use different settings
    if os.environ.get("FLASK_ENV") == "development":
        cookie_kwargs["samesite"] = "Lax"
        cookie_kwargs["secure"] = False
    
    resp.set_cookie("token", token, **cookie_kwargs)
    
    # Add CORS headers explicitly
    resp.headers.add('Access-Control-Allow-Credentials', 'true')
    resp.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    
    return resp

# ---------------- GET USER ----------------
@app.route("/user", methods=["GET"])
def get_user():
    # First try to get token from Authorization header (Bearer token)
    auth_header = request.headers.get('Authorization')
    token = None
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split('Bearer ')[1]
    else:
        # Fallback to cookie method
        token = request.cookies.get("token")
    
    if not token:
        return jsonify({"user": None})

    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        
        user = users.find_one({"_id": ObjectId(decoded["user_id"])}, {"password": 0})
        
        if user:
            user["_id"] = str(user["_id"])

        response = jsonify({"user": user})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    except Exception as e:
        response = jsonify({"user": None})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

# ---------------- LOGOUT ----------------
@app.route("/logout", methods=["POST"])
def logout():
    resp = make_response(jsonify("Logged out"))
    # Configure cookie for production deployment
    cookie_kwargs = {
        "expires": 0,
        "httponly": True,
        "samesite": "None",
        "secure": True  # Should be True in production
    }
    
    # For local development, use different settings
    if os.environ.get("FLASK_ENV") == "development":
        cookie_kwargs["samesite"] = "Lax"
        cookie_kwargs["secure"] = False
    
    resp.set_cookie("token", "", **cookie_kwargs)
    resp.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    resp.headers.add('Access-Control-Allow-Credentials', 'true')
    return resp

if __name__ == "__main__":
    # Validate required environment variables
    required_vars = ['MONGO_URI', 'JWT_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {missing_vars}")
        exit(1)
    
    # Test database connection before starting
    try:
        client.server_info()
        print("Database connection successful")
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        exit(1)
    
    # Use the PORT environment variable provided by Render, default to 3001 for local development
    port = int(os.environ.get("PORT", 3001))
    print(f"Starting server on port {port}")
    
    app.run(host="0.0.0.0", port=port, debug=False)