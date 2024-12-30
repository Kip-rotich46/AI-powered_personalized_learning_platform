from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)

# Set up MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client.learning_platform

# JWT Secret key
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a more secure secret key
jwt = JWTManager(app)

# User Registration Route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    # Check if the user already exists
    if db.users.find_one({"username": username}):
        return jsonify({"msg": "Username already exists"}), 400
    
    # Hash password before saving
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Save user to database
    user = {
        "username": username,
        "password": hashed_password
    }
    
    db.users.insert_one(user)
    return jsonify({"msg": "User created successfully"}), 201

# User Login Route (JWT Authentication)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    user = db.users.find_one({"username": username})
    
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({"msg": "Bad username or password"}), 401
    
    # Create JWT Token
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# Get all courses (public)
@app.route('/courses', methods=['GET'])
def get_courses():
    courses = list(db.courses.find())
    for course in courses:
        course.pop('_id')  # Remove the MongoDB _id field for cleaner response
    return jsonify(courses)

# Create new course (protected, requires JWT)
@app.route('/courses', methods=['POST'])
@jwt_required()
def create_course():
    data = request.get_json()
    
    # Get course data from the request
    course = {
        "name": data['name'],
        "description": data['description'],
        "modules": data['modules']
    }
    
    db.courses.insert_one(course)
    return jsonify({"msg": "Course created successfully"}), 201

# User Profile Route (protected, requires JWT)
@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    # Get the username from the JWT identity
    current_user = get_jwt_identity()
    user = db.users.find_one({"username": current_user})
    user.pop('_id')
    user.pop('password')
    return jsonify(user)

if __name__ == '__main__':
    app.run(debug=True)
