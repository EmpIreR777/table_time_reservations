from app.dao.base import BaseDAO
from app.db.models.models import Doctor


class DoctorDAO(BaseDAO[Doctor]):
    model = Doctor
