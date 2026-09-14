from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models import DonationAlert, DonationStatus

class DonationRepositoryPort(ABC):
    @abstractmethod
    def list_all(self) -> List[DonationAlert]:
        """List all donation alerts."""
        pass

    @abstractmethod
    def get_by_id(self, donation_id: str) -> Optional[DonationAlert]:
        """Fetch donation by ID."""
        pass

    @abstractmethod
    def save(self, donation: DonationAlert) -> DonationAlert:
        """Create or update donation."""
        pass

    @abstractmethod
    def update_status(self, donation_id: str, status: DonationStatus) -> Optional[DonationAlert]:
        """Update donation status."""
        pass
