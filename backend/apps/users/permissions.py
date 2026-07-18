# PATH: apps/users/permissions.py

from rest_framework.permissions import BasePermission

# Allows only authenticated admin users to access the endpoint.
class IsAdmin(BasePermission):
    """Allows access only to users with role='admin'"""

    message = 'Only admin users can perform this action.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )

# Allows only authenticated customer users to access the endpoint.
class IsCustomer(BasePermission):
    """Allows access only to users with role='customer'"""

    message = 'Only customer accounts can perform this action.'
    
# Checks whether the logged-in user is authenticated and has the customer role.
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'customer'
        )