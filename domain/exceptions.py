"""Domain-level exceptions."""


class CareerPlusError(Exception):
    """Base class for all CareerPlus errors."""


class CompanyNotFoundError(CareerPlusError):
    pass


class ProjectNotFoundError(CareerPlusError):
    pass


class CVNotFoundError(CareerPlusError):
    pass


class InvalidFilterError(CareerPlusError):
    pass


class EmailDeliveryError(CareerPlusError):
    pass


class RetrievalError(CareerPlusError):
    pass