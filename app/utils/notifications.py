from typing import Literal

def notify(channel: Literal["email", "sms"], destination: str, subject: str, body: str) -> None:
    print(f"[NOTIFY::{channel}] -> {destination} | {subject}: {body}")
