import json, time
from datetime import datetime, timezone
from app.tasks.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.job import Job, Execution, JobStatus

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def execute_payload(self, job_id: int, payload: dict):
    db = SessionLocal(); job = db.get(Job, job_id)
    execution = Execution(job_id=job_id, status=JobStatus.running, attempt=self.request.retries + 1, started_at=datetime.now(timezone.utc))
    db.add(execution); job.status = JobStatus.running; db.commit()
    try:
        time.sleep(float(payload.get("sleep_seconds", 0)))
        result = {"message": payload.get("message", "job completed"), "payload": payload}
        execution.status = JobStatus.success; execution.output = json.dumps(result); job.status = JobStatus.success
        execution.finished_at = datetime.now(timezone.utc); db.commit(); return result
    except Exception as exc:
        execution.status = JobStatus.failed; execution.error = str(exc); job.status = JobStatus.failed; db.commit(); raise
    finally: db.close()
