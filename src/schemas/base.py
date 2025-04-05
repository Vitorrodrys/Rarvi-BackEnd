from pydantic import BaseModel



class BaseSchema(BaseModel):
    pass

class BaseCreateSchema(BaseModel):
    pass

class BaseUpdateSchema(BaseModel):
    id: int
