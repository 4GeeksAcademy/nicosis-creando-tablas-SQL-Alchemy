"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from api.utils import APIException, generate_sitemap
from api.models import db, Student, Project, Submission
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands
from sqlalchemy import desc
from datetime import datetime

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

# 1.2 Insertar Student
@app.route('/student', methods=['POST'])
def add_student():

    request_body = request.get_json()  
    new_student = Student(name_student=request_body['name_student'], email=request_body['email'], programming_skills=request_body['programming_skills'])
    db.session.add(new_student)
    db.session.commit()
    return jsonify('student added:',new_student.serialize()), 200

# 1.3 Recupera todos los esutdiantes de la base de datos usando SQLAlchemy. Muestra su nombre y su email
@app.route('/student', methods=['GET'])
def get_students():
    students = Student.query.all()
    #all_students = list(map(lambda x: x.serialize(), student))
    student_data = [{'id': student.id, 'name_student': student.name_student, 'email': student.email} for student in students]
    print(student_data)
    return jsonify(student_data), 200

# 1.4 Recupera el estudiante cuyo **id** es el más alto de todos. Muestra su **nombre** y su **email**.
@app.route('/student/alto', methods=['GET'])
def get_student_alto_id():
    student = Student.query.order_by(desc(Student.id)).first()
    student_data = {'id': student.id, 'name_student': student.name_student}
    print(student_data)
    return jsonify(student_data), 200

# 1.5 Recupera SOLAMENTE los estudiantes de la base de datos que SÍ tenian conocimientos previos de programación. Muestra su nombre y email. 
@app.route('/student/check', methods=['GET'])
def get_student_check():
    students = Student.query.filter_by(programming_skills=True).all()
    student_data = [student.serialize() for student in students]
    print(student_data)
    return jsonify(student_data), 200


# 2.1 Recupera todos los proyectos y muestralos por el terminal
@app.route('/project', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    all_projects = list(map(lambda x: x.serialize(), projects))
    print(all_projects)
    return jsonify(all_projects), 200

# 2.2 Recupera todos los proyectos que tratan sobre el topic “JavaScript”.
@app.route('/project/js', methods=['GET'])
def get_project_js():
    projects = Project.query.filter(Project.topics.like('%JavaScript%')).all()
    all_projects = [project.serialize() for project in projects]
    return jsonify(all_projects), 200

# 2.2 Recuperar proyectos en base a un string
@app.route('/project/<string:palabra>', methods=['GET'])
def get_project_param(palabra):
    projects = Project.query.filter(Project.topics.ilike(f'%{palabra}%')).all()
    all_projects = [project.serialize() for project in projects]
    print(all_projects)
    return jsonify(all_projects), 200

# 3.2 Recupera todos los proyectos entregados por Alexander  // <int:student_id>
@app.route('/project/<int:student_id>', methods=['GET'])
def get_project_by_student_id(student_id):
    students = Student.query.get(student_id)
    all_projects = [project.serialize() for project in students.submissions]
    print(all_projects)
    return jsonify(all_projects), 200

# 3.3 Recupera todos los proyectos de todos lo estudiantes cuya fecha de entrega ha sido antes del 17 de Abril de 2023
@app.route('/submission/<string:date>', methods=['GET'])
def get_project_before_date(date):

    submissions = Submission.query.filter(Submission.submited_date < date).all()
    all_subm = [subm.serialize() for subm in submissions]
    #for all_subm in submissions:
    print(all_subm)
    return jsonify(all_subm), 200

# 3.3b Solo para terminal
def get_project_before_date2(date):
    submissions = Submission.query.filter(Submission.submited_date < date).all()
    for submission in submissions:
        print(submission)

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)

    # Lo necesitamos para pdoer ejecutar código Python normal fuera del entorno de Flask
    #with app.app_context():
        #Iteración 1.3
        #get_students()
        #Iteración 1.4
        #get_student_alto_id()
        #Iteración 1.5
        #get_student_check()
        #Iteración 2.1
        #get_projects()
        #Iteración 2.2
        #get_project_param("JavaScript")
        #Iteración 3.2
        #get_project_by_student_id(4)
        #Iteración 3.3
        #get_project_before_date2(datetime(2023, 5, 7))
        #get_project_before_date(datetime(2023, 5, 7))

