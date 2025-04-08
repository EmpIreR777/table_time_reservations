import pytz
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.specializations_dao import SpecializationDAO
from app.db.session_maker_fast_api import db_session

MOSCOW_TZ = pytz.timezone('Europe/Moscow')


router = APIRouter(tags=['Specializations'])


@router.get('/specialists')
async def get_specialists(session: AsyncSession = Depends(db_session.get_session)):
    return await SpecializationDAO.find_all(session=session)
