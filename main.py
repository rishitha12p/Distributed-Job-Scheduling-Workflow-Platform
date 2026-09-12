import json
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import Base, engine, get_db
from app.models.job import Job, User, JobStatus
from app.schemas.job import JobCreate, JobRead, UserCreate, Token
from app.core.security import hash_password, verify_password, create_token
from app.api.deps import current_user
from app.tasks.tasks import execute_payload

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Distributed Job Scheduling & Workflow Platform", version="1.0.0")

@app.get("/health")
def health(): return {"status": "ok", "service": "job-platform"}

@app.post("/auth/register", response_model=Token)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first(): raise HTTPException(409, "Username already exists")
    user = User(username=data.username, password_hash=hash_password(data.password)); db.add(user); db.commit()
    return Token(access_token=create_token(user.username))

@app.post("/auth/token", response_model=Token)
def token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.password_hash): raise HTTPException(401, "Invalid credentials")
    return Token(access_token=create_token(user.username))

@app.post("/jobs", response_model=JobRead)
def create_job(data: JobCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    job = Job(**data.model_dump(exclude={"payload"}), payload=json.dumps(data.payload), owner_id=user.id)
    db.add(job); db.commit(); db.refresh(job)
    if not job.run_at and not job.cron: execute_payload.delay(job.id, data.payload); job.status = JobStatus.queued; db.commit()
    return job

@app.get("/jobs", response_model=list[JobRead])
def list_jobs(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.query(Job).filter(Job.owner_id == user.id).order_by(Job.priority.asc(), Job.created_at.desc()).all()

@app.get("/jobs/{job_id}", response_model=JobRead)
def get_job(job_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.owner_id == user.id).first()
    if not job: raise HTTPException(404, "Job not found")
    return job

@app.post("/jobs/{job_id}/cancel", response_model=JobRead)
def cancel_job(job_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.owner_id == user.id).first()
    if not job: raise HTTPException(404, "Job not found")
    job.status = JobStatus.cancelled; db.commit(); db.refresh(job); return job
