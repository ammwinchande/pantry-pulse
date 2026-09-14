from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models import DonationAlert, DispatchProposal

class DonationUseCase(ABC):
    @abstractmethod
    def ingest_donation_alert(self, donation: DonationAlert) -> DispatchProposal:
        """
        Ingests an incoming food rescue alert, kicks off Strands Agent analysis,
        and produces a pending human decision proposal.
        """
        pass

    @abstractmethod
    def list_donations(self) -> List[DonationAlert]:
        """Fetch all donation alerts."""
        pass

    @abstractmethod
    def get_donation(self, donation_id: str) -> Optional[DonationAlert]:
        """Fetch donation by id."""
        pass

    @abstractmethod
    def simulate_random_alert(self) -> DispatchProposal:
        """Helper for demo / judges: injects a realistic emergency surplus alert."""
        pass
