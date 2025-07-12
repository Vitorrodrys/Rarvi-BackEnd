from pathlib import Path

from firebase_admin import credentials, initialize_app, messaging

class Notifier:

    def __init__(
        self,
        firebase_key: Path
    ):
        cred = credentials.Certificate(firebase_key)
        initialize_app(cred)

    def send_notification(self, token: str, title:str, body: str):
        message = messaging.Message(
            notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                token=token,
        )
        messaging.send(message)


