from abc import ABC, abstractmethod
from typing import Dict, Any, List
from src.domain.models import Dispatch, Volunteer, DonationAlert

class NotificationPort(ABC):
    @abstractmethod
    def notify_volunteer_dispatch(self, volunteer: Volunteer, dispatch: Dispatch, donation: DonationAlert) -> bool:
        """Send urgent dispatch SMS/message to assigned volunteer."""
        pass

    @abstractmethod
    def notify_donor_eta(self, donation: DonationAlert, dispatch: Dispatch, volunteer: Volunteer, eta_minutes: int) -> bool:
        """Send arrival reassurance message to food donor."""
        pass

    @abstractmethod
    def notify_coordinator_urgent_decision(self, donation: DonationAlert) -> bool:
        """Trigger high-priority audio/visual alert on coordinator mission control."""
        pass

    @abstractmethod
    def get_sent_messages(self) -> List[Dict[str, Any]]:
        """Return audit history of dispatched notifications."""
        pass
