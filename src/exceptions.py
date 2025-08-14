from typing import Any


class APIException(Exception):
    """General API Exception, whenever a specific reason can't be determined."""

    extra: dict[str, Any] = {}

    def __init__(self, *args, **kwargs):
        self.extra = kwargs.pop('extra', self.extra)
        super().__init__(*args)


class CLIException(Exception):
    """General CLI Exception, whenever a specific reason can't be determined."""

    extra: dict[str, Any] = {}

    def __init__(self, *args, **kwargs):
        self.extra = kwargs.pop('extra', self.extra)
        super().__init__(*args)

    def get_extra_details(self) -> dict:
        if self.extra:
            return self.extra
        return {}


class ServiceUnavailableException(APIException):
    pass


class ServiceInvalidRequestException(APIException):
    pass


class ServiceInvalidResponseException(APIException):
    pass


class UpdateWorkItemException(APIException):
    pass


class ValidationError(APIException):
    pass


class IssueTransitionException(APIException):
    pass


class ResourceNotFoundException(APIException):
    pass


class AuthorizationException(APIException):
    pass


class PermissionException(APIException):
    pass
