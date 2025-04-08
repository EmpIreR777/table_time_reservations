from app.dao.base_dao import BaseDAO
from app.db.models.models import Table


class TableDAO(BaseDAO[Table]):
    model = Table
