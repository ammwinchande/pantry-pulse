from abc import ABC, abstractmethod


class EmailPort(ABC):
    """
    Outbound SPI for transactional email delivery.

    Used for: registration activation, password reset, and
    password change notifications.
    """

    @abstractmethod
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str = "",
    ) -> bool:
        """Send a transactional email. Returns True on successful hand-off."""
        pass
