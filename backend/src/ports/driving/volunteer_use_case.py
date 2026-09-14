from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models import Volunteer, VolunteerStatus

class VolunteerUseCase(ABC):
    @abstractmethod
    def list_volunteers(self) -> List[Volunteer]:
        """List all volunteers and their status."""
        pass

    @abstractmethod
    def get_volunteer(self, volunteer_id: str) -> Optional[Volunteer]:
        """Get volunteer details."""
        pass

    @abstractmethod
    def toggle_availability(self, volunteer_id: str, is_available: bool) -> Volunteer:
        """Allow driver to toggle on/off duty."""
        pass

    @abstractmethod
    def register_volunteer(self, volunteer: Volunteer) -> Volunteer:
        """Add new volunteer to fleet."""
        pass
