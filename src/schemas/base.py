from pydantic import BaseModel, ConfigDict



class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class BaseCreateSchema(BaseModel):
    pass

class BaseUpdateSchema(BaseModel):
    pass
