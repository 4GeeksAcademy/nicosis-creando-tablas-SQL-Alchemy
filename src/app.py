"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from api.utils import APIException, generate_sitemap
from api.models import db, Student
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands
from sqlalchemy import desc

#from models import Person

ENV = os.getenv("FLASK_ENV")
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False

# database condiguration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type = True)
db.init_app(app)

# Allow CORS requests to this API
CORS(app)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0 # avoid cache memory
    return response


@app.route('/student', methods=['GET'])
def get_student():
    students = Student.query.all()
    #all_students = list(map(lambda x: x.serialize(), student))
    student_data = [{'name_student': student.name_student, 'email': student.email} for student in students]
    return jsonify(student_data), 200

@app.route('/student/alto', methods=['GET'])
def get_student_alto_id():
    #students = Student.query.all()
    student = Student.query.order_by(desc(Student.id)).first()
    student_data = {'id': student.id, 'name_student': student.name_student}
    return jsonify(student_data), 200

@app.route('/student/check', methods=['GET'])
def get_student_check():
    students = Student.query.filter_by(programming_skills=True).all()
    student_data = [student.serialize() for student in students]
    return jsonify(student_data), 200

@app.route('/student', methods=['POST'])
def add_student():

    request_body = request.get_json()  
    new_student = Student(name_student=request_body['name_student'], email=request_body['email'], programming_skills=request_body['programming_skills'])
    db.session.add(new_student)
    db.session.commit()
    return jsonify('student added:',new_student.serialize()), 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
