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
otp_store = {}  # use Redis in production

# ---------------- CORS SETTINGS ----------------
CORS(
    app,
    supports_credentials=True,
    origins=[
        "https://med-zoom-1.onrender.com",  # frontend
        "https://med-zoom.onrender.com",   # backend host-friendly
        "http://localhost:5173"            # local development
    ],
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    expose_headers=["Access-Control-Allow-Credentials"],
    max_age=86400
)

# ---------------- EMAIL OTP ----------------
def send_otp_email(email, otp):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return False

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email
    msg["Subject"] = "MedZoom - OTP Verification"

    msg.attach(MIMEText(f"<h2>Your OTP: {otp}</h2>", "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        server.starttls(context=ssl.create_default_context())
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

def generate_otp():
    return "".join(random.choices(string.digits, k=6))


# ---------------- HEALTH CHECK ----------------
@app.route("/health", methods=["GET"])
def health_check():
    try:
        db.command("ping")
        return jsonify({"status": "healthy"}), 200
    except:
        return jsonify({"status": "db-error"}), 500


# ---------------- SEND OTP ----------------
@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json
    email = data.get("email")

    if users.find_one({"email": email}):
        return jsonify({"error": "Email already exists"}), 400

    otp = generate_otp()
    otp_store[email] = {"otp": otp, "expires": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}

    if send_otp_email(email, otp):
        return jsonify({"message": "OTP sent"}), 200
    return jsonify({"error": "Failed to send OTP"}), 500


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username, email, password, otp = data.values()

    if users.find_one({"email": email}):
        return jsonify({"error": "Email exists"}), 400

    if email not in otp_store or otp_store[email]["otp"] != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users.insert_one({"username": username, "email": email, "password": hashed})
    del otp_store[email]

    return jsonify({"message": "User created"}), 201


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = users.find_one({"username": data["username"]})

    if not user or not bcrypt.checkpw(data["password"].encode(), user["password"]):
        return jsonify("Invalid credentials"), 400

    token = jwt.encode({"user_id": str(user["_id"]), "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)}, JWT_SECRET)

    resp = make_response(jsonify("Success"))
    resp.set_cookie("token", token, httponly=True, secure=True, samesite="None")

    return resp


# ---------------- GET USER ----------------
@app.route("/user", methods=["GET"])
def get_user():
    token = request.cookies.get("token")
    if not token:
        return jsonify({"user": None})

    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = users.find_one({"_id": ObjectId(decoded["user_id"])}, {"password": 0})
        user["_id"] = str(user["_id"])
        return jsonify({"user": user})
    except:
        return jsonify({"user": None})


# ---------------- LOGOUT ----------------
@app.route("/logout", methods=["POST"])
def logout():
    resp = make_response(jsonify("Logged out"))
    resp.set_cookie("token", "", expires=0, httponly=True, secure=True, samesite="None")
    return resp



# ---------------- FIX: HANDLE OPTIONS REQUEST ----------------
@app.before_request
def preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response, 200


# ---------------- START SERVER ----------------
if __name__ == "__main__":
    print("🚀 Starting backend...")
    
    required_vars = ['MONGO_URI', 'JWT_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"⚠ WARNING: Missing environment variables: {missing_vars}")
        print("Backend will still run, but some features may not work.")

    # Test MongoDB
    try:
        client.server_info()
        print("Database connection OK")
    except Exception as e:
        print(f"⚠ DB Connection Issue: {e}")

    port = int(os.environ.get("PORT", 3001))
    print(f"Running on port {port}")

    app.run(host="0.0.0.0", port=port, debug=False)
