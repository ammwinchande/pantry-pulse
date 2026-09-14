from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models import DispatchProposal, Dispatch, DispatchStatus

class DispatchUseCase(ABC):
    @abstractmethod
    def list_pending_decisions(self) -> List[DispatchProposal]:
        """Fetch proposals awaiting human decision."""
        pass

    @abstractmethod
    def approve_proposal(self, proposal_id: str, approved_by: str = "Coordinator Sarah L.") -> Dispatch:
        """Coordinator 1-click approval: executes dispatch of primary candidate."""
        pass

    @abstractmethod
    def override_with_alternative(self, proposal_id: str, approved_by: str = "Coordinator Sarah L.") -> Dispatch:
        """Coordinator switches to alternative candidate."""
        pass

    @abstractmethod
    def custom_override(self, proposal_id: str, volunteer_id: str, notes: str, approved_by: str = "Coordinator Sarah L.") -> Dispatch:
        """Coordinator picks a specific volunteer from fleet."""
        pass

    @abstractmethod
    def reject_proposal(self, proposal_id: str, reason: str) -> None:
        """Rejects proposal if no dispatch can take place."""
        pass

    @abstractmethod
    def confirm_pickup(self, dispatch_id: str, verification_code: str) -> Dispatch:
        """Driver confirms food custody at donor location using 4-digit code."""
        pass

    @abstractmethod
    def confirm_delivery(self, dispatch_id: str, final_weight_lbs: Optional[int] = None) -> Dispatch:
        """Pantry intake worker confirms food arrival at pantry loading dock."""
        pass

    @abstractmethod
    def list_dispatches(self) -> List[Dispatch]:
        """List confirmed dispatches."""
        pass
