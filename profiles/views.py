"""Profile API views.

Provides endpoints for profile management including:
- GET/PATCH /me/ - View and update own profile
- POST/DELETE /me/avatar/ - Upload and delete avatar
- GET /{user_id}/ - View public profile
"""

from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles.models import Profile
from profiles.selectors import profile_get_by_user, profile_get_by_user_id
from profiles.serializers import (
    AvatarOutputSerializer,
    AvatarUploadSerializer,
    ProfileInputSerializer,
    ProfileOutputSerializer,
    ProfilePublicOutputSerializer,
)
from profiles.services import avatar_delete, avatar_upload, profile_update


class ProfileMeView(APIView):
    """View for authenticated user's own profile.

    GET: Retrieve current user's profile.
    PATCH: Update current user's profile fields.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Get the authenticated user's profile.

        Args:
            request: HTTP request.

        Returns:
            Profile data with all fields.
        """
        profile = profile_get_by_user(user=request.user)
        serializer = ProfileOutputSerializer(profile, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request) -> Response:
        """Update the authenticated user's profile.

        Args:
            request: HTTP request with update data.

        Returns:
            Updated profile data.
        """
        input_serializer = ProfileInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        profile = profile_get_by_user(user=request.user)
        updated_profile = profile_update(
            profile=profile,
            **input_serializer.validated_data,
        )

        output_serializer = ProfileOutputSerializer(
            updated_profile, context={"request": request}
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class ProfileAvatarView(APIView):
    """View for avatar upload and deletion.

    POST: Upload a new avatar image.
    DELETE: Remove current avatar.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request: Request) -> Response:
        """Upload a new avatar image.

        Args:
            request: HTTP request with avatar file.

        Returns:
            Avatar URL and success message.
        """
        serializer = AvatarUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = profile_get_by_user(user=request.user)
        avatar_url = avatar_upload(
            profile=profile,
            avatar_file=serializer.validated_data["avatar"],
        )

        # Build full URL
        full_url = request.build_absolute_uri(avatar_url)
        output = AvatarOutputSerializer(
            {"avatar": full_url, "message": "Profile picture updated successfully."}
        )
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request: Request) -> Response:
        """Delete the current avatar.

        Args:
            request: HTTP request.

        Returns:
            Empty response with 204 status.
        """
        profile = profile_get_by_user(user=request.user)
        avatar_delete(profile=profile)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfilePublicView(APIView):
    """View for public profile (other users).

    GET: Retrieve limited public profile data.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, user_id: int) -> Response:
        """Get a user's public profile.

        Args:
            request: HTTP request.
            user_id: The user ID to look up.

        Returns:
            Public profile data (limited fields).
        """
        try:
            profile = profile_get_by_user_id(user_id=user_id)
        except Profile.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound("User profile not found.")

        serializer = ProfilePublicOutputSerializer(
            profile, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
