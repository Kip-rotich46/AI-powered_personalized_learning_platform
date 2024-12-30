from flask import Blueprint, request, jsonify
from pymongo import MongoClient

client = MongoClient("<your_mongodb_connection_string>")
db = client.ai_learning
quizzes = db.quizzes

quiz_bp = Blueprint("quiz", __name__)

# Create a quiz
@quiz_bp.route("/create", methods=["POST"])
def create_quiz():
    data = request.get_json()
    quiz = {
        "title": data.get("title"),
        "questions": data.get("questions"),  # List of questions
    }
    quizzes.insert_one(quiz)
    return jsonify({"message": "Quiz created successfully"}), 201

# Get quizzes
@quiz_bp.route("/", methods=["GET"])
def get_quizzes():
    all_quizzes = list(quizzes.find({}, {"_id": 0}))
    return jsonify(all_quizzes), 200
