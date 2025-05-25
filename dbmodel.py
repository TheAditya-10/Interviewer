from flask_sqlalchemy import SQLAlchemy
import enum
import config  # <-- Change this line

db = SQLAlchemy()

def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    db.init_app(app)

class ExperienceLevel(enum.Enum):
    Intern = "Intern"
    Fressher = "Fressher"
    Intermediate = "Intermediate"
    Expert = "Expert"

class Job(db.Model):
    __tablename__ = 'job'
    J_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    required_experience = db.Column(db.Enum(ExperienceLevel), nullable=False)
    skill_req = db.Column(db.JSON, nullable=False)
    min_qualification = db.Column(db.String(255), nullable=False)
    soft_skill_req = db.Column(db.JSON, nullable=False)

    interviews = db.relationship("Interview", back_populates="job")

class Candidate(db.Model):
    __tablename__ = 'candidate'
    C_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    skills = db.Column(db.JSON, nullable=False)
    soft_skills = db.Column(db.JSON, nullable=False)
    achievements = db.Column(db.JSON, nullable=False)
    experience = db.Column(db.Enum(ExperienceLevel), nullable=False)
    max_qualification = db.Column(db.String(255), nullable=False)

    interviews = db.relationship("Interview", back_populates="candidate")

class Interview(db.Model):
    __tablename__ = 'interview'
    J_id = db.Column(db.Integer, db.ForeignKey('job.J_id'), nullable=False)
    C_id = db.Column(db.Integer, db.ForeignKey('candidate.C_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    skill_order = db.Column(db.JSON, nullable=False)
    report = db.Column(db.String(1024), nullable=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Interval, nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('J_id', 'C_id'),
    )

    job = db.relationship("Job", back_populates="interviews")
    candidate = db.relationship("Candidate", back_populates="interviews")
