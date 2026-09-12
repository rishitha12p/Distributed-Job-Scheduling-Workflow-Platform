from apscheduler.schedulers.blocking import BlockingScheduler
from app.db.session import SessionLocal
from app.models.job import Job, JobStatus
from app.tasks.tasks import execute_payload
import json

def dispatch_due_jobs():
    db = SessionLocal()
    try:
        jobs = db.query(Job).filter(Job.status == JobStatus.pending, Job.run_at <= __import__('datetime').datetime.now(__import__('datetime').timezone.utc)).all()
        for job in jobs:
            execute_payload.delay(job.id, json.loads(job.payload)); job.status = JobStatus.queued
        db.commit()
    finally: db.close()

if __name__ == "__main__":
    scheduler = BlockingScheduler(); scheduler.add_job(dispatch_due_jobs, "interval", seconds=10); scheduler.start()
