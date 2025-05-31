from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Job(db.Model):
    __tablename__ = 'job'
    J_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_title = db.Column(db.String(255), nullable=False)  # <-- Add this line
    required_experience = db.Column(db.String(50), nullable=False)
    skill_req = db.Column(db.JSON, nullable=False)
    min_qualification = db.Column(db.String(255), nullable=False)
    soft_skill_req = db.Column(db.JSON, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    interviews = db.relationship("Interview", back_populates="job")

class Candidate(db.Model):
    __tablename__ = 'candidate'
    C_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    dob = db.Column(db.Date)
    password = db.Column(db.String(255))
    skills = db.Column(db.JSON)
    soft_skills = db.Column(db.JSON)
    achievements = db.Column(db.JSON)
    experience = db.Column(db.String(50))
    max_qualification = db.Column(db.String(255))

    interviews = db.relationship("Interview", back_populates="candidate")

class Interview(db.Model):
    __tablename__ = 'interview'
    J_id = db.Column(db.Integer, db.ForeignKey('job.J_id'), nullable=False)
    C_id = db.Column(db.Integer, db.ForeignKey('candidate.C_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    skill_order = db.Column(db.JSON, nullable=False)
    report = db.Column(db.Text, nullable=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # duration in minutes

    __table_args__ = (
        db.PrimaryKeyConstraint('J_id', 'C_id'),
    )

    job = db.relationship("Job", back_populates="interviews")
    candidate = db.relationship("Candidate", back_populates="interviews")
