class DomainException(Exception):
    """Base class for domain exceptions."""
    pass

class DonationNotFoundError(DomainException):
    def __init__(self, donation_id: str):
        super().__init__(f"Donation with id '{donation_id}' not found.")

class VolunteerNotFoundError(DomainException):
    def __init__(self, volunteer_id: str):
        super().__init__(f"Volunteer with id '{volunteer_id}' not found.")

class ProposalNotFoundError(DomainException):
    def __init__(self, proposal_id: str):
        super().__init__(f"Dispatch proposal with id '{proposal_id}' not found.")

class IncompatibleVolunteerError(DomainException):
    def __init__(self, reason: str):
        super().__init__(f"Volunteer incompatible: {reason}")

class InvalidStateTransitionError(DomainException):
    def __init__(self, entity: str, current_state: str, attempted_state: str):
        super().__init__(f"Cannot transition {entity} from {current_state} to {attempted_state}.")
