import logging
import time
import threading

from sqlalchemy.orm import Session

from core import  settings
import crud
import crud.db
import models
from services.notifier import Notifier

config = settings.get()

notify_handler = Notifier(config.FIREBASE_SERVICE_KEY)

def _notify(db_session: Session, user: models.User):
    random_card = crud.card.get_random_by_priority(db_session, user.id)
    if not random_card:
        logging.warning("no cards selected from user '%s', maybe he does not has cards?", user.name)
        return
    title = f"Hello {user.name}, do you still remember of this concept?"
    body = random_card.question
    for notify_token in user.notification_tokens:
        notify_handler.send_notification(notify_token.token, title, body)
    logging.info("notifications sended to user '%s'", user.name)

def process_notifications(db_session: Session):
    users = crud.user.get_multi(db_session)
    for user in users:
        _notify(db_session, user)

def create_worker() -> threading.Thread:

    def thread_code():
        while True:
            time.sleep(config.CARD_NOTIFICATION_INTERVAL.total_seconds())
            with crud.db.SessionLocal() as db_session:
                process_notifications(db_session)
    logging.info("worker started with polling time of %s", config.CARD_NOTIFICATION_INTERVAL.total_seconds())
    notification_worker = threading.Thread(target=thread_code, daemon=True)
    notification_worker.start()
    return notification_worker

