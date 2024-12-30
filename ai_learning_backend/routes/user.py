from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("<your_mongodb_connection_string>")
db = client.ai_learning
users = db.users

user_bp = Blueprint("user", __name__)

# Signup route
@user_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if users.find_one({"username": username}):
        return jsonify({"error": "User already exists"}), 409

    hashed_password = generate_password_hash(password)
    users.insert_one({"username": username, "password": hashed_password})
    return jsonify({"message": "User registered successfully"}), 201

# Login route
@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = users.find_one({"username": username})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful"}), 200
