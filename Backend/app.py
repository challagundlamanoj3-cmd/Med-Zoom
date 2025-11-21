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
print("EMAIL_ADDRESS loaded?:", bool(os.getenv("EMAIL_ADDRESS")))
print("EMAIL_PASSWORD loaded?:", bool(os.getenv("EMAIL_PASSWORD")))
print("MONGO_URI loaded?:", bool(os.getenv("MONGO_URI")))

app = Flask(__name__)

# Test database connection
try:
    print("[DB] Testing database connection...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # Will throw an exception if can't connect
    print("[DB] Database connection successful!")
except Exception as e:
    print(f"[DB] Database connection failed: {e}")
    import traceback
    traceback.print_exc()

CORS(
    app,
    supports_credentials=True,
    origins=[
        "https://med-zoom-1.onrender.com",  # Your frontend domain
        "https://med-zoom.onrender.com",   # Just in case
        "http://localhost:5173",           # Local development
        "http://127.0.0.1:5173"
    ],
    allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
    methods=["GET", "POST", "OPTIONS"],
    expose_headers=["Access-Control-Allow-Credentials", "Access-Control-Allow-Origin"],
    max_age=86400
)

# ---------------- ENV VARIABLES ----------------
MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("JWT_SECRET")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

client = MongoClient(MONGO_URI)
db = client["medzoom"]
users = db["users"]
otp_store = {}  # Use Redis in production


# ---------------- SEND OTP EMAIL (UPDATED + MORE LOGS) ----------------
def send_otp_email(email, otp):
    print(f"[EMAIL] Attempting to send OTP to {email}")
    print(f"[EMAIL] Using sender: {EMAIL_ADDRESS}")
    
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("⚠ Email credentials missing in .env")
        return False
    
    # Test email format
    if not email or "@" not in email:
        print(f"[EMAIL] Invalid email address: {email}")
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
    except smtplib.SMTPException as e:
        print(f"[SMTP ERROR] SMTP Exception (SSL): {e}")
        return False


# ---------------- GENERATE OTP ----------------
def generate_otp():
    return "".join(random.choices(string.digits, k=6))


# ---------------- TEST ENDPOINT ----------------
@app.get("/test")
def test():
    return jsonify({"message": "Backend running!", "status": "success"}), 200

# ---------------- HEALTH CHECK ENDPOINT ----------------
@app.get("/health")
def health_check():
    try:
        # Test database connection
        db.command('ping')
        response = jsonify({
            "status": "healthy", 
            "timestamp": datetime.datetime.utcnow(),
            "database": "connected",
            "service": "backend-running"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    except Exception as e:
        response = jsonify({
            "status": "unhealthy", 
            "timestamp": datetime.datetime.utcnow(),
            "error": str(e),
            "service": "backend-running"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500


# ---------------- SEND OTP ----------------
@app.post("/send-otp")
def send_otp():
    try:
        print("[SEND OTP] Request received")
        print(f"[SEND OTP] Request data: {request.json}")
        
        data = request.json

        if not data:
            return jsonify({"error": "Invalid request"}), 400

        email = data["email"]
        print(f"[SEND OTP] Processing email: {email}")

        if users.find_one({"email": email}):
            print(f"[SEND OTP] Email already exists: {email}")
            return jsonify({"error": "Email already exists"}), 400

        otp = generate_otp()
        print(f"[SEND OTP] Generated OTP: {otp}")
        
        otp_store[email] = {
            "otp": otp,
            "expires": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        }

        success = send_otp_email(email, otp)
        
        if not success:
            print(f"⚠ Failed to send OTP email to {email}")
            response = jsonify({"error": "Failed to send OTP email. Please check your email address and try again."})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
        
        print(f"✅ OTP email sent successfully to {email}")
        response = jsonify({"message": "OTP sent successfully"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    except Exception as e:
        print(f"[SEND OTP] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500


# ---------------- SIGNUP ----------------
@app.post("/signup")
def signup():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    username = data["username"]
    email = data["email"]
    password = data["password"]
    otp = data["otp"]
    
    print(f"[DEBUG] Signup request for email: {email}")
    print(f"[DEBUG] Provided OTP: {otp}")
    print(f"[DEBUG] OTP store keys: {list(otp_store.keys())}")

    if users.find_one({"email": email}):
        return jsonify({"error": "Email exists"}), 400

    if users.find_one({"username": username}):
        return jsonify({"error": "Username taken"}), 400

    if email not in otp_store:
        print(f"[DEBUG] Email {email} not found in OTP store")
        return jsonify({"error": "OTP missing or expired"}), 400

    print(f"[DEBUG] Stored OTP info: {otp_store[email]}")
    
    if datetime.datetime.utcnow() > otp_store[email]["expires"]:
        del otp_store[email]
        print(f"[DEBUG] OTP expired for {email}")
        return jsonify({"error": "OTP expired"}), 400

    if otp_store[email]["otp"] != otp:
        print(f"[DEBUG] OTP mismatch. Expected: {otp_store[email]['otp']}, Got: {otp}")
        return jsonify({"error": "Invalid OTP"}), 400

    del otp_store[email]

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    users.insert_one({
        "username": username,
        "email": email,
        "password": hashed_pw
    })

    return jsonify({"message": "User created"}), 201


# ---------------- LOGIN ----------------
@app.post("/login")
def login():
    print("[LOGIN] Request received")
    print(f"[LOGIN] Request data: {request.json}")
    print(f"[LOGIN] Request headers: {dict(request.headers)}")
    
    data = request.json
    if not data:
        return jsonify("Invalid request"), 400

    username = data["username"]
    password = data["password"]
    
    print(f"[LOGIN] Attempting login for username: {username}")

    user = users.find_one({"username": username})
    if not user:
        print(f"[LOGIN] User does not exist: {username}")
        return jsonify("User does not exist"), 400

    if not bcrypt.checkpw(password.encode(), user["password"]):
        print(f"[LOGIN] Incorrect password for user: {username}")
        return jsonify("Incorrect password"), 400

    token = jwt.encode(
        {
            "user_id": str(user["_id"]),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
        },
        JWT_SECRET,
        algorithm="HS256"
    )
    
    print(f"[LOGIN] Token generated: {token}")

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
    
    # Add some debugging
    print(f"[LOGIN] Setting cookie: token={token}")
    print(f"[LOGIN] Cookie attributes: {cookie_kwargs}")
    print(f"[LOGIN] Response headers: {dict(resp.headers)}")
    
    return resp


# ---------------- GET USER ----------------
@app.get("/user")
def get_user():
    print("[GET USER] Request received")
    print(f"[GET USER] Request headers: {dict(request.headers)}")
    print(f"[GET USER] Request cookies: {request.cookies}")
    
    # First try to get token from Authorization header (Bearer token)
    auth_header = request.headers.get('Authorization')
    token = None
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split('Bearer ')[1]
        print(f"[GET USER] Token from Authorization header: {token}")
    else:
        # Fallback to cookie method
        token = request.cookies.get("token")
        print(f"[GET USER] Token from cookies: {token}")
    
    print(f"[GET USER] Token received: {token}")
    
    if not token:
        print("[GET USER] No token found")
        return jsonify({"user": None})

    try:
        print(f"[GET USER] Attempting to decode token: {token}")
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        print(f"[GET USER] Token decoded successfully: {decoded}")
        
        user = users.find_one({"_id": ObjectId(decoded["user_id"])}, {"password": 0})
        print(f"[GET USER] User found in database: {user is not None}")
        
        if user:
            user["_id"] = str(user["_id"])

        return jsonify({"user": user})
    except Exception as e:
        print(f"[GET USER] Error decoding token: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"user": None})


# ---------------- LOGOUT ----------------
@app.post("/logout")
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
    return resp


# ---------------- GET ALL USERS (FOR DEBUGGING) ----------------
@app.get("/debug/users")
def get_all_users():
    try:
        all_users = list(users.find({}, {"password": 0}))
        for user in all_users:
            user["_id"] = str(user["_id"])
        return jsonify({"users": all_users, "count": len(all_users)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("[STARTUP] Starting Flask application...")
    print(f"[STARTUP] Environment variables: {dict(os.environ)}")
    print(f"[STARTUP] MONGO_URI present: {bool(os.getenv('MONGO_URI'))}")
    print(f"[STARTUP] JWT_SECRET present: {bool(os.getenv('JWT_SECRET'))}")
    print(f"[STARTUP] EMAIL_ADDRESS present: {bool(os.getenv('EMAIL_ADDRESS'))}")
    print(f"[STARTUP] EMAIL_PASSWORD present: {bool(os.getenv('EMAIL_PASSWORD'))}")
    
    # Use the PORT environment variable provided by Render, default to 3001 for local development
    port = int(os.environ.get("PORT", 3001))
    print(f"[STARTUP] Starting server on port {port}")
    
    try:
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        print(f"[STARTUP] Error starting server: {e}")
        import traceback
        traceback.print_exc()