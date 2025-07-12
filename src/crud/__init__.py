import models
import schemas

from .crud_base import CRUDBase
from .crud_card import CRUDCard
from .crud_disciplines import CRUDDisciplines
from .crud_user import CRUDUser


card = CRUDCard()
discipline = CRUDDisciplines()
user = CRUDUser()
