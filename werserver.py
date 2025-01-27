
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)

# MongoDB configuration
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mentor_marketplace'
mongo = PyMongo(app)
mentors_collection = mongo.db.mentors

# Helper function to serialize MongoDB documents
def serialize_mentor(mentor):
    return {
        "id": str(mentor["_id"]),
        "name": mentor["name"],
        "expertise": mentor["expertise"],
        "location": mentor["location"],
        "availability": mentor.get("availability", [])
    }

# 1. Register mentors and add expertise details
@app.route('/mentors', methods=['POST','GET'])
def register_mentor():
    data = request.json
    name = data.get("name")
    expertise = data.get("expertise")
    location = data.get("location")
    availability = data.get("availability", [])

    if not all([name, expertise, location]):
        return jsonify({"error": "Missing required fields: name, expertise, or location."}), 400

    mentor_id = mentors_collection.insert_one({
        "name": name,
        "expertise": expertise,
        "location": location,
        "availability": availability
    }).inserted_id

    return jsonify({
        "message": "Mentor registered successfully!",
        "mentor_id": str(mentor_id),
        "name": name,
        "expertise": expertise,
        "location": location,
        "availability": availability
    }), 201

# 2. Search for mentors based on location
@app.route('/mentors/search', methods=['GET'])
def search_mentors():
    location = request.args.get("location")

    if not location:
        return jsonify({"error": "Location is required to search for mentors."}), 400

    query = {"location": {"$regex": location, "$options": "i"}}  # Case-insensitive match

    mentors = mentors_collection.find(query)
    result = [serialize_mentor(mentor) for mentor in mentors]

    return jsonify(result), 200

# 3. Retrieve mentor availability for scheduling by mentor ID
@app.route('/mentors/availability', methods=['GET'])
def get_mentor_availability():
    mentor_id = request.args.get("id")

    if not mentor_id:
        return jsonify({"error": "Mentor ID is required to retrieve availability."}), 400

    try:
        mentor = mentors_collection.find_one({"_id": ObjectId(mentor_id)})
    except Exception as e:
        return jsonify({"error": "Invalid Mentor ID format."}), 400

    if not mentor:
        return jsonify({"error": "Mentor not found."}), 404

    return jsonify({"availability": mentor.get("availability", [])}), 200

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
