"""
All exceptions for dashboard, they maybe handled in [common.middleware].
Also collect some exceptions from keystoneclient and novaclient.
"""

from keystoneclient import exceptions as keystoneclient_exceptions
from novaclient import exceptions as novaclient_exceptions


class DashboardException(Exception):
    pass


class NotAuthorized(DashboardException):
    """
    Raised whenever a user attempts to access a resource which they do not
    have role-based access to .
    """
    status_code = 401


class NotFound(DashboardException):
    status_code = 404

    
class ServiceCatalogException(DashboardException):
    """
    Raised when a requested service is not available in the ``ServiceCatalog``
    returned by Keystone.
    """
    def __init__(self, service_name):
        message = 'Invalid service catalog service: %s' % service_name
        super(ServiceCatalogException, self).__init__(message)


UNAUTHORIZED = (keystoneclient_exceptions.Unauthorized,
                keystoneclient_exceptions.Forbidden,
                novaclient_exceptions.Unauthorized,
                novaclient_exceptions.Forbidden,
                NotAuthorized)
