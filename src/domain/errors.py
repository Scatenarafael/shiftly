class DomainError(Exception):
    """Base error for domain/business rules."""


class NotFoundError(DomainError):
    pass


class AlreadyExistsError(DomainError):
    pass


class PermissionDeniedError(DomainError):
    pass


class ValidationError(DomainError):
    pass


class AuthError(DomainError):
    pass


class InvalidCredentials(AuthError):
    pass


class RefreshNotFound(AuthError):
    pass


class RefreshReuseDetected(AuthError):
    pass


class RefreshExpired(AuthError):
    pass


class RefreshInvalid(AuthError):
    pass
