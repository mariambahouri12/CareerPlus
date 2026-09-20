from __future__ import annotations

from abc import ABC, abstractmethod


class EmailSenderPort(ABC):
    @abstractmethod
    def send(self, recipient: str, subject: str, body: str) -> dict:
        """
        Send an email. Must return {"status": "success", "message_id": ...}
        or raise if sending failed.
        """