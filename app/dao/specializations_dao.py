from app.dao.base import BaseDAO
from app.db.models.models import Specialization


class SpecializationDAO(BaseDAO[Specialization]):
    model = Specialization
