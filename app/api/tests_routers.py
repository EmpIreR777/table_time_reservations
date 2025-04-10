from fastapi import APIRouter
from datetime import datetime
from app.core.config import scheduler

router = APIRouter()


@router.get("/force-run-job/{job_id}")
async def force_run_job(job_id: str):
    job = scheduler.get_job(job_id)
    if not job:
        return {"status": "error", "message": "Job not found"}

    job_args = job.args
    user_id, text = job_args if len(job_args) == 2 else (None, None)

    # Запускаем задачу сейчас
    job.modify(next_run_time=datetime.now())

    return {
        "status": "success",
        "job_id": job_id,
        "new_run_time": "now",
        "message_text": text,
        "user_id": user_id,
    }
