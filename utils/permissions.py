from rest_framework import permissions


class IsBusinessOwnerOrAdmin(permissions.BasePermission):
    """
    Only business users can create offers.
    Only the owner of the offer or an admin can edit/delete it.
    """

    def has_permission(self, request, view):
        """ Global permission check (applies to list & create). """
        if request.method == 'POST':
            user_profile = getattr(request.user, 'profile', None)
            return (
                request.user.is_authenticated and
                user_profile and
                user_profile.user_type == 'business'
            )

        if view.action == 'retrieve':
            return request.user.is_authenticated

        return True

    def has_object_permission(self, request, view, obj):
        """ Object-level permission check (applies to update/delete). """
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, 'business_user'):
            return obj.business_user == request.user or request.user.is_staff

        return obj.user == request.user or request.user.is_staff


class IsCustomerOrAdmin(permissions.BasePermission):
    """
    Only customers can access this resource.
    Admin users (is_staff) also have full access.
    """

    def has_permission(self, request, view):
        """ Global permission check (applies to list & create). """
        user_profile = getattr(request.user, 'profile', None)
        return (
            request.user.is_authenticated and
            user_profile and
            (user_profile.user_type == 'customer' or request.user.is_staff)
        )

    def has_object_permission(self, request, view, obj):
        """ Object-level permission check (applies to update/delete). """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff


class IsReviewerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow only the review creator or an admin to update/delete.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.reviewer == request.user or request.user.is_staff


class IsAdminOnly(permissions.BasePermission):
    """
    Allows access only to admin users (staff).
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class IsBusinessOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        user_profile = getattr(user, 'profile', None)

        return (
            user.is_authenticated and
            (user.is_staff or user_profile.user_type == 'business'
             )
        )
