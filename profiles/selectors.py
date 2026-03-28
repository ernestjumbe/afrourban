"""Profile selectors for read operations.

Following HackSoftware Django Styleguide - selectors
are used for all read operations (queries).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from profiles.models import Profile

if TYPE_CHECKING:
    from users.models import CustomUser

def profile_get_by_user(*, user: CustomUser) -> Profile:
    """Get profile for the given user.

    Args:
        user: The user whose profile to retrieve.

    Returns:
        The user's profile.

    Raises:
        Profile.DoesNotExist: If no profile exists for the user.
    """
    return Profile.objects.select_related("user").get(user=user)


def profile_get_by_user_id(*, user_id: int) -> Profile:
    """Get profile by user ID.

    Args:
        user_id: The ID of the user whose profile to retrieve.

    Returns:
        The user's profile.

    Raises:
        Profile.DoesNotExist: If no profile exists for the user ID.
    """
    return Profile.objects.select_related("user").get(user_id=user_id)
