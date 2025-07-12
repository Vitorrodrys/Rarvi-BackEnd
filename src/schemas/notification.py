from pydantic import BaseModel

class NotificationTokenCommitSchema(BaseModel):
    token: str
    user_id: int
