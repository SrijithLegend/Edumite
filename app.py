from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

# Helper functions to safely read and write database json files
def load_data():
    if not os.path.exists(DATA_FILE):
        # Default initialization dataset state if file doesn't exist
        default_state = {
            "apps": [
                { "name": "Google", "url": "https://www.google.com" },
                { "name": "Zoom", "url": "https://zoom.us" },
                { "name": "GitHub", "url": "https://github.com" }
            ],
            "tasks": [
                { "name": "Database Management Assignment #2", "url": "https://classroom.google.com", "category": "assignments", "origin": "college", "date": "2026-06-18" },
                { "name": "Build Dashboard Layout System", "url": "https://github.com", "category": "projects", "origin": "side quest", "date": "2026-06-25" }
            ]
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(default_state, f, indent=4)
        return default_state
    
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    return render_template('dashboard.html')

# --- API ENDPOINTS FOR APPLICATIONS WORKSPACE ---
@app.route('/api/apps', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_apps():
    data = load_data()
    
    if request.method == 'GET':
        return jsonify(data['apps'])
        
    elif request.method == 'POST':
        new_app = request.json
        data['apps'].append(new_app)
        save_data(data)
        return jsonify({"status": "success", "data": data['apps']}), 201

    elif request.method == 'PUT':
        req_data = request.json
        idx = req_data.get('index')
        if idx is not None and 0 <= idx < len(data['apps']):
            data['apps'][idx] = req_data['app']
            save_data(data)
            return jsonify({"status": "success"})
        return jsonify({"error": "Invalid index parameter"}), 400

    elif request.method == 'DELETE':
        idx = request.json.get('index')
        if idx is not None and 0 <= idx < len(data['apps']):
            data['apps'].pop(idx)
            save_data(data)
            return jsonify({"status": "success"})
        return jsonify({"error": "Invalid index parameter"}), 400

# --- API ENDPOINTS FOR INSTITUTIONAL WORKSPACE TASKS ---
@app.route('/api/tasks', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_tasks():
    data = load_data()
    
    if request.method == 'GET':
        return jsonify(data['tasks'])
        
    elif request.method == 'POST':
        new_task = request.json
        data['tasks'].append(new_task)
        save_data(data)
        return jsonify({"status": "success", "data": data['tasks']}), 201

    elif request.method == 'PUT':
        req_data = request.json
        idx = req_data.get('index')
        if idx is not None and 0 <= idx < len(data['tasks']):
            data['tasks'][idx] = req_data['task']
            save_data(data)
            return jsonify({"status": "success"})
        return jsonify({"error": "Invalid index parameter"}), 400

    elif request.method == 'DELETE':
        idx = request.json.get('index')
        if idx is not None and 0 <= idx < len(data['tasks']):
            data['tasks'].pop(idx)
            save_data(data)
            return jsonify({"status": "success"})
        return jsonify({"error": "Invalid index parameter"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)