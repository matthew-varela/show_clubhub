from rest_framework.permissions import BasePermission
from .models import UserClubs, ClubRole


class IsClubAdmin(BasePermission):
    """Allow operation only if the current user is an admin of the targeted club.

    Views using this permission must implement a `get_club()` method that returns
    the `Club` instance relevant to the current request or `None`.
    """

    def has_permission(self, request, view):
        club = getattr(view, "get_club", lambda: None)()
        if club is None or not request.user or not request.user.is_authenticated:
            return False
        try:
            membership = UserClubs.objects.get(user=request.user, club=club)
            return membership.role == ClubRole.ADMIN
        except UserClubs.DoesNotExist:
            return False 