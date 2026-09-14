from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models import DispatchProposal, Dispatch, DispatchStatus

class DispatchRepositoryPort(ABC):
    @abstractmethod
    def save_proposal(self, proposal: DispatchProposal) -> DispatchProposal:
        """Save a newly generated dispatch proposal."""
        pass

    @abstractmethod
    def get_proposal_by_id(self, proposal_id: str) -> Optional[DispatchProposal]:
        """Fetch proposal by ID."""
        pass

    @abstractmethod
    def list_pending_proposals(self) -> List[DispatchProposal]:
        """List proposals waiting for human decision."""
        pass

    @abstractmethod
    def save_dispatch(self, dispatch: Dispatch) -> Dispatch:
        """Save confirmed dispatch."""
        pass

    @abstractmethod
    def list_dispatches(self) -> List[Dispatch]:
        """List all confirmed dispatches."""
        pass

    @abstractmethod
    def get_dispatch_by_id(self, dispatch_id: str) -> Optional[Dispatch]:
        """Fetch confirmed dispatch by ID."""
        pass

    @abstractmethod
    def update_dispatch_status(self, dispatch_id: str, status: DispatchStatus) -> Optional[Dispatch]:
        """Update dispatch state (e.g. PICKED_UP, DELIVERED)."""
        pass
