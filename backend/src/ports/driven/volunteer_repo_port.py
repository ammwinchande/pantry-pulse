from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models import Volunteer, VolunteerStatus

class VolunteerRepositoryPort(ABC):
    @abstractmethod
    def list_all(self) -> List[Volunteer]:
        """Return all registered volunteers."""
        pass

    @abstractmethod
    def get_by_id(self, volunteer_id: str) -> Optional[Volunteer]:
        """Fetch a volunteer by ID."""
        pass

    @abstractmethod
    def list_available(self) -> List[Volunteer]:
        """Return volunteers with AVAILABLE status."""
        pass

    @abstractmethod
    def save(self, volunteer: Volunteer) -> Volunteer:
        """Create or update a volunteer."""
        pass

    @abstractmethod
    def update_status(self, volunteer_id: str, status: VolunteerStatus) -> Optional[Volunteer]:
        """Update volunteer status."""
        pass
