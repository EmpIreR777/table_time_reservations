from app.dao.base_dao import BaseDAO
from app.db.models.models import TimeSlot


class TimeSlotDAO(BaseDAO[TimeSlot]):
    model = TimeSlot
