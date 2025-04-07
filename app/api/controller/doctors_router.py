from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.doctors_dao import DoctorDAO
from app.schemas.specializations_schemas import SpecIDModel
from app.db.session_maker_fast_api import db_session


router = APIRouter(tags=['Doctors'])


@router.get('/doctors/{spec_id}')
async def get_doctors_spec(
    spec_id: int, session: AsyncSession = Depends(db_session.get_session)):
    return await DoctorDAO.find_all(
        session=session, filters=SpecIDModel(specialization_id=spec_id))


@router.get('/doctor/{doctor_id}')
async def get_doctor_by_id(
    doctor_id: int, session: AsyncSession = Depends(db_session.get_session)):
    return await DoctorDAO.find_one_or_none_by_id(session=session, data_id=doctor_id)
