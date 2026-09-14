from abc import ABC, abstractmethod
from typing import List
from src.domain.models import DonationAlert, Volunteer, DispatchProposal, AgentTraceLog

class AgentPort(ABC):
    @abstractmethod
    def evaluate_and_propose(self, donation: DonationAlert, available_volunteers: List[Volunteer]) -> DispatchProposal:
        """
        Runs the autonomous Strands Agent loop with tools to evaluate cargo,
        rank volunteers, and generate the structured DispatchProposal.
        """
        pass

    @abstractmethod
    def get_traces(self) -> List[AgentTraceLog]:
        """Returns the in-memory execution traces and tool calls of the Strands Agent."""
        pass
