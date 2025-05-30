from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import pymysql
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import wave
import vosk
import json

import config  
from dbmodel import db, Job, Candidate, Interview
from resumereader import extract_candidate_data
from scheduler import get_skill_order

pymysql.install_as_MySQLdb()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
db.init_app(app)

# Serve job list for dropdown
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    jobs = Job.query.all()
    job_list = [
        {
            "J_id": job.J_id,
            "min_qualification": job.min_qualification
        } for job in jobs
    ]
    return jsonify({"jobs": job_list})

# Store uploaded resumes here
UPLOAD_FOLDER = 'static/resumes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Handle application submission
@app.route('/api/apply', methods=['POST'])
def apply_job():
    job_id = request.form.get('job_id')
    interview_date = request.form.get('interview_date')
    interview_time = request.form.get('interview_time')
    c_id = request.form.get('c_id')
    resume = request.files.get('resume')
    create_password = request.form.get('create_password')  # for new candidates

    if not (job_id and interview_date and interview_time):
        return jsonify({"message": "Missing required fields"}), 400

    candidate = None
    if c_id:
        password = request.form.get('password')
        candidate = Candidate.query.get(int(c_id))
        if not candidate:
            return jsonify({"message": "Candidate ID not found."}), 400
        if not password or candidate.password != password:
            return jsonify({"message": "Incorrect password."}), 400
    else:
        if not resume or not resume.filename.endswith('.pdf') or not create_password:
            return jsonify({"message": "Resume and password required."}), 400
        filename = secure_filename(resume.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume.save(resume_path)
        candidate_data = extract_candidate_data(resume_path)
        dob = candidate_data.get('dob')
        if not dob or dob.strip() == "":
            dob = "2000-01-01"
        candidate = Candidate(
            name=candidate_data.get('name', 'Unknown'),
            dob=dob,
            password=create_password,
            skills=candidate_data.get('skills', []),
            soft_skills=candidate_data.get('soft_skills', []),
            achievements=candidate_data.get('achievements', []),
            experience=candidate_data.get('experience', 'Fresher'),
            max_qualification=candidate_data.get('max_qualification', '')
        )
        db.session.add(candidate)
        db.session.commit()

    # Fetch candidate and job skills
    candidate_skills = candidate.skills if candidate.skills else []
    print("Candidate skills:", candidate_skills)
    job_obj = db.session.get(Job, int(job_id))  # updated for SQLAlchemy 2.x
    job_skills = job_obj.skill_req if job_obj and job_obj.skill_req else []
    print("Job skills:", job_skills)
    # Get skill order using LLM
    skill_order = get_skill_order(candidate_skills, job_skills)

    # Check for duplicate interview
    existing_interview = Interview.query.filter_by(J_id=int(job_id), C_id=candidate.C_id).first()
    if existing_interview:
        return jsonify({"message": "You have already applied for this job."}), 400

    # Save interview
    start_datetime = datetime.strptime(f"{interview_date} {interview_time}", "%Y-%m-%d %H:%M")
    new_interview = Interview(
        J_id=int(job_id),
        C_id=candidate.C_id,
        score=0,
        skill_order=skill_order,
        report="",
        start_datetime=start_datetime,
        duration=30
    )
    db.session.add(new_interview)
    db.session.commit()

    return jsonify({
        "message": "Application submitted successfully!",
        "c_id": candidate.C_id,
        "interview_date": interview_date,
        "interview_time": interview_time,
        "job_id": job_id
    })

@app.route('/api/job', methods=['POST'])
def post_job():
    data = request.form if request.form else request.json
    required_experience = data.get('required_experience')
    skill_req = data.get('skill_req')
    min_qualification = data.get('min_qualification')
    soft_skill_req = data.get('soft_skill_req')

    if not (required_experience and skill_req and min_qualification and soft_skill_req):
        return jsonify({"message": "All fields are required."}), 400

    import json
    try:
        skill_req_json = json.loads(skill_req)
        soft_skill_req_json = json.loads(soft_skill_req)
    except Exception:
        return jsonify({"message": "Skill fields must be valid JSON arrays."}), 400

    job = Job(
        required_experience=required_experience,
        skill_req=skill_req_json,
        min_qualification=min_qualification,
        soft_skill_req=soft_skill_req_json
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({"message": "Job posted successfully!", "J_id": job.J_id})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply')
def apply():
    return render_template('apply.html')

@app.route('/interview')
def interview():
    return render_template('interview.html')

@app.route('/job')
def job():
    return render_template('job.html')


vosk_model = vosk.Model("vosk-model-small-en-us-0.15")  # Path to your Vosk model

@app.route('/api/stt', methods=['POST'])
def stt():
    audio = request.files['audio']
    # Save audio to a dummy file for now
    dummy_path = os.path.join("static", "dummy_transcript.txt")
    wf = wave.open(audio, "rb")
    rec = vosk.KaldiRecognizer(vosk_model, wf.getframerate())
    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(json.loads(rec.Result()))
    results.append(json.loads(rec.FinalResult()))
    transcript = " ".join([r.get("text", "") for r in results])
    # Save transcript to dummy file
    with open(dummy_path, "a", encoding="utf-8") as f:
        f.write(transcript + "\n")
    return jsonify({"transcript": transcript})

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)