from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
    
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_student = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    programming_skills = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return f'Student {self.name_student}'

    def serialize(self):
        return {
            "id": self.id,
            "name_student": self.name_student,
            "email": self.email,
            "programming_skills": self.programming_skills,
        }
    
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(200), unique=True, nullable=False)
    topics = db.Column(db.String(200), unique=True, nullable=False)

    def __repr__(self):
        return f'Project {self.project_name}'

    def serialize(self):
        return {
            "id": self.id,
            "project_name": self.project_name,
            "topics": self.topics,
        }

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    submited_date = db.Column(db.Date, nullable=False)

    project = db.relationship('Project', backref='submissions')
    student = db.relationship('Student', backref='submissions')

    def __repr__(self):
        return f'Submission: {self.student.name_student} / {self.submited_date }'

    def serialize(self):
        # Retorna None si ya existe una entrada con los mismos valores
        #existing_submission = Submission.query.filter_by(project_id=self.project_id, student_id=self.student_id).first()
        #if existing_submission:
            #return None  
        
        return {
            "project_id": self.project_id,
            "student_id": self.student_id,
            "submited_date": self.submited_date,
            "student_name": self.student.name_student,
            "project_name": self.project.project_name,
        }