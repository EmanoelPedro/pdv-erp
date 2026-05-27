class AppError(Exception):
    """Base exception for domain and application errors."""


class AppConflictError(AppError):
    """Raised when the current state conflicts with the requested action."""


class AppNotFoundError(AppError):
    """Raised when a requested entity cannot be found."""


class AppPermissionError(AppError):
    """Raised when the current user cannot perform an action."""


class AppAuthenticationError(AppError):
    """Raised when authentication is required or invalid."""


class AppValidationError(AppError):
    """Raised when a business payload is invalid."""


class CashRegisterError(AppError):
    """Base exception for cash register business errors."""


class CashRegisterAlreadyOpenError(CashRegisterError, AppConflictError):
    """Raised when attempting to open a second active session."""


class CashRegisterAlreadyClosedError(CashRegisterError, AppConflictError):
    """Raised when attempting to close an already closed session."""


class CashRegisterNotFoundError(CashRegisterError, AppNotFoundError):
    """Raised when a cash register session cannot be found."""


class CashRegisterNotOpenError(CashRegisterError, AppConflictError):
    """Raised when a sale requires an open cash register session."""


class OwnerPermissionRequiredError(CashRegisterError, AppPermissionError):
    """Raised when a sensitive action requires owner approval."""


class AuthenticationRequiredError(AppAuthenticationError):
    """Raised when an authenticated user is required."""


class InvalidCredentialsError(AppAuthenticationError):
    """Raised when local credentials do not match."""


class UserRegistrationNotAllowedError(AppPermissionError):
    """Raised when the current actor cannot create a user."""


class DuplicateUsernameError(AppConflictError):
    """Raised when trying to create a user with a duplicate username."""


class UserNotFoundError(AppNotFoundError):
    """Raised when a user cannot be found."""


class CategoryNotFoundError(AppNotFoundError):
    """Raised when a category cannot be found."""


class DuplicateCategoryNameError(AppConflictError):
    """Raised when trying to create a category with a duplicate name."""


class ProductNotFoundError(AppNotFoundError):
    """Raised when one or more products cannot be found."""


class ProductInactiveError(AppConflictError):
    """Raised when a sale references an inactive product."""


class InvalidProductImageError(AppValidationError):
    """Raised when an uploaded product image is invalid."""


class InvalidPaymentError(AppValidationError):
    """Raised when a payment breakdown is invalid."""


class ExpenseNotFoundError(AppNotFoundError):
    """Raised when an expense cannot be found."""


class ExpenseImmutableError(AppConflictError):
    """Raised when an expense belongs to a closed cash session."""


class InvalidExpenseAmountError(AppValidationError):
    """Raised when an expense amount is not positive."""


class InvalidOwnerPinError(AppPermissionError):
    """Raised when an owner-only protected action receives an invalid PIN."""
