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

class DispatchNotFoundError(DomainException):
    def __init__(self, dispatch_id: str):
        super().__init__(f"Dispatch '{dispatch_id}' not found.")
class IncompatibleVolunteerError(DomainException):
    def __init__(self, reason: str):
        super().__init__(f"Volunteer incompatible: {reason}")

class InvalidStateTransitionError(DomainException):
    def __init__(self, entity: str, current_state: str, attempted_state: str):
        super().__init__(f"Cannot transition {entity} from {current_state} to {attempted_state}.")


# --- Authentication & Authorization ---
class AuthenticationError(DomainException):
    """Invalid credentials, expired/invalid token, or inactive account."""
    pass


class UserNotFoundError(DomainException):
    def __init__(self, identifier: str):
        super().__init__(f"User with id or email '{identifier}' not found.")


class EmailAlreadyRegisteredError(DomainException):
    def __init__(self, email: str):
        super().__init__(f"An account with email '{email}' already exists.")


class InvalidTokenError(DomainException):
    def __init__(self, reason: str):
        super().__init__(f"Invalid token: {reason}")


class InsufficientPermissionsError(DomainException):
    def __init__(self, required_role: str, actual_role: str):
        super().__init__(f"Requires role '{required_role}', but user has '{actual_role}'.")
