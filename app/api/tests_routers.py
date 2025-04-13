from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.api.utils import sms_service
from app.core.config import scheduler
from app.schemas.users_schemas import SMSRequest

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


@router.post("/send-sms/")
async def send_sms(request: SMSRequest):
    """
    Отправка SMS через сервис SMS.ru
    
    Параметры:
    - phone: номер телефона в формате 79991112233
    - message: текст сообщения (до 800 символов)
    """
    try:
        result = await sms_service.send_sms(request.phone, request.message)
        return {
            "status": "success",
            "data": result,
            "message": "SMS отправлено успешно"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e))