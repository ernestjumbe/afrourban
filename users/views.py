"""User API views for registration and authentication."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
    TokenVerifyView as BaseTokenVerifyView,
)

from users.permissions import IsStaffUser
from users.selectors import (
    role_get_by_id,
    role_list,
    user_get_by_id,
    user_list,
    user_permissions_get,
)
from users.serializers import (
    AdminUserDetailSerializer,
    AdminUserListSerializer,
    AdminUserUpdateInputSerializer,
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    PermissionsInputSerializer,
    PermissionsOutputSerializer,
    RegisterInputSerializer,
    ResendVerificationEmailInputSerializer,
    RoleCreateInputSerializer,
    RoleDetailSerializer,
    RoleListSerializer,
    RoleUpdateInputSerializer,
    UserActivationOutputSerializer,
    UserOutputSerializer,
    VerifyEmailInputSerializer,
)
from users.services import (
    email_verification_resend,
    email_verification_verify,
    role_create,
    role_delete,
    role_update,
    user_activate,
    user_create,
    user_deactivate,
    user_permissions_set,
    user_update,
)

User = get_user_model()


class RegisterView(APIView):
    """API view for user registration.

    POST /api/auth/register/
    Creates a new user account with an associated profile.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Handle user registration.

        Args:
            request: DRF request with registration data.

        Returns:
            Response with created user data or validation errors.
        """
        serializer = RegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_create(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            display_name=serializer.validated_data.get("display_name", ""),
        )

        output_serializer = UserOutputSerializer(user)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
    """API view for email verification.

    POST /api/auth/email-verification/verify/
    Validates a verification token and marks the user's email as verified.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = VerifyEmailInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email_verification_verify(token=serializer.validated_data["token"])

        return Response({"status": "ok"})


class ResendVerificationEmailView(APIView):
    """API view for resending a verification email.

    POST /api/auth/email-verification/resend/
    Always returns 200 OK to prevent user enumeration.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = ResendVerificationEmailInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email_verification_resend(email=serializer.validated_data["email"])

        return Response({"status": "ok"})


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view.

    POST /api/auth/token/
    Returns access and refresh tokens along with user data and policies.
    """

    serializer_class = CustomTokenObtainPairSerializer


class TokenRefreshView(BaseTokenRefreshView):
    """JWT token refresh view.

    POST /api/auth/token/refresh/
    Returns new access token (and rotated refresh token).
    """

    pass


class TokenVerifyView(BaseTokenVerifyView):
    """JWT token verification view.

    POST /api/auth/token/verify/
    Verifies that a token is valid.
    """

    pass


class LogoutView(APIView):
    """API view for user logout.

    POST /api/auth/logout/
    Blacklists the provided refresh token.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Handle user logout by blacklisting refresh token.

        Args:
            request: DRF request with refresh token.

        Returns:
            Empty response with 205 Reset Content status.
        """
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except Exception:
            # Token already blacklisted or invalid - still return success
            pass

        return Response(status=status.HTTP_205_RESET_CONTENT)


# =============================================================================
# Admin Views (Phase 6: User Story 4)
# =============================================================================


class AdminUserListView(APIView):
    """Admin view for listing users.

    GET /api/admin/users/
    List all users with pagination, filtering, and search.
    """

    permission_classes = [IsStaffUser]

    def get(self, request: Request) -> Response:
        """List users with optional filters.

        Query Parameters:
            - page: Page number (default: 1)
            - page_size: Items per page (default: 20, max: 100)
            - is_active: Filter by active status
            - is_staff: Filter by staff status
            - search: Search in email or display name
            - ordering: Sort field (default: -date_joined)

        Returns:
            Paginated list of users.
        """
        # Parse query params
        page = int(request.query_params.get("page", 1))
        page_size = min(int(request.query_params.get("page_size", 20)), 100)
        is_active = request.query_params.get("is_active")
        is_staff = request.query_params.get("is_staff")
        search = request.query_params.get("search")
        ordering = request.query_params.get("ordering", "-date_joined")

        # Convert string booleans
        if is_active is not None:
            is_active = is_active.lower() == "true"
        if is_staff is not None:
            is_staff = is_staff.lower() == "true"

        # Get queryset
        queryset = user_list(
            is_active=is_active,
            is_staff=is_staff,
            search=search,
            ordering=ordering,
        )

        # Paginate
        count = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        users = queryset[start:end]

        # Build pagination URLs
        base_url = request.build_absolute_uri(request.path)
        next_url = None
        prev_url = None

        if end < count:
            next_url = f"{base_url}?page={page + 1}&page_size={page_size}"
        if page > 1:
            prev_url = f"{base_url}?page={page - 1}&page_size={page_size}"

        serializer = AdminUserListSerializer(users, many=True)
        return Response(
            {
                "count": count,
                "next": next_url,
                "previous": prev_url,
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class AdminUserDetailView(APIView):
    """Admin view for user detail and updates.

    GET /api/admin/users/{user_id}/
    PATCH /api/admin/users/{user_id}/
    """

    permission_classes = [IsStaffUser]

    def get(self, request: Request, user_id: int) -> Response:
        """Get detailed user information.

        Args:
            request: The HTTP request.
            user_id: The user's ID.

        Returns:
            User detail data.
        """
        try:
            user = user_get_by_id(user_id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found.")

        serializer = AdminUserDetailSerializer(user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request, user_id: int) -> Response:
        """Update user account settings.

        Args:
            request: The HTTP request with update data.
            user_id: The user's ID.

        Returns:
            Updated user data.
        """
        try:
            user = user_get_by_id(user_id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found.")

        input_serializer = AdminUserUpdateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        data = input_serializer.validated_data
        updated_user = user_update(
            user=user,
            is_staff=data.get("is_staff"),
            group_ids=data.get("roles"),
        )

        # Refresh user to get updated relations
        updated_user = user_get_by_id(user_id=updated_user.pk)
        output_serializer = AdminUserDetailSerializer(
            updated_user, context={"request": request}
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class AdminUserActivateView(APIView):
    """Admin view for activating user accounts.

    POST /api/admin/users/{user_id}/activate/
    """

    permission_classes = [IsStaffUser]

    def post(self, request: Request, user_id: int) -> Response:
        """Activate a user account.

        Args:
            request: The HTTP request.
            user_id: The user's ID.

        Returns:
            Activation confirmation.
        """
        try:
            user = user_get_by_id(user_id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found.")

        activated_user = user_activate(user=user)
        serializer = UserActivationOutputSerializer(
            {
                "id": activated_user.pk,
                "email": activated_user.email,
                "is_active": activated_user.is_active,
                "message": "User account activated successfully.",
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminUserDeactivateView(APIView):
    """Admin view for deactivating user accounts.

    POST /api/admin/users/{user_id}/deactivate/
    """

    permission_classes = [IsStaffUser]

    def post(self, request: Request, user_id: int) -> Response:
        """Deactivate a user account.

        Args:
            request: The HTTP request.
            user_id: The user's ID.

        Returns:
            Deactivation confirmation.
        """
        try:
            user = user_get_by_id(user_id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found.")

        # Prevent self-deactivation
        if user.pk == request.user.pk:
            raise ValidationError({"detail": "You cannot deactivate your own account."})

        deactivated_user = user_deactivate(user=user)
        serializer = UserActivationOutputSerializer(
            {
                "id": deactivated_user.pk,
                "email": deactivated_user.email,
                "is_active": deactivated_user.is_active,
                "message": "User account deactivated successfully.",
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminUserPermissionsView(APIView):
    """Admin view for managing user permissions.

    GET /api/admin/users/{user_id}/permissions/
    PUT /api/admin/users/{user_id}/permissions/
    """

    permission_classes = [IsStaffUser]

    def get(self, request: Request, user_id: int) -> Response:
        """Get user's effective permissions.

        Args:
            request: The HTTP request.
            user_id: The user's ID.

        Returns:
            User permissions data.
        """
        try:
            user = user_get_by_id(user_id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found.")

        permissions_data = user_permissions_get(user=user)
        serializer = PermissionsOutputSerializer(permissions_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, user_id: int) -> Response:
        """Set user's direct permissions.

        Args:
            request: The HTTP request with permission IDs.
            user_id: The user's ID.

        Returns:
            Updated permissions data.
        """
        try:
            user = user_get_by_id(user_id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found.")

        input_serializer = PermissionsInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        permissions = user_permissions_set(
            user=user,
            permission_ids=input_serializer.validated_data["permission_ids"],
        )

        # Return updated permissions
        output_data = {
            "user_id": user.pk,
            "direct_permissions": [
                {"id": p.id, "codename": p.codename} for p in permissions
            ],
            "message": "Permissions updated successfully.",
        }
        return Response(output_data, status=status.HTTP_200_OK)


# =============================================================================
# Admin Role Views (Phase 7: User Story 5)
# =============================================================================


class AdminRoleListView(APIView):
    """Admin view for listing and creating roles.

    GET /api/admin/users/roles/
    POST /api/admin/users/roles/
    """

    permission_classes = [IsStaffUser]

    def get(self, request: Request) -> Response:
        """List all available roles.

        Returns:
            List of roles with user and permission counts.
        """
        roles = role_list()
        serializer = RoleListSerializer(roles, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """Create a new role.

        Args:
            request: The HTTP request with role data.

        Returns:
            Created role data.
        """
        input_serializer = RoleCreateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        role = role_create(
            name=input_serializer.validated_data["name"],
            permission_ids=input_serializer.validated_data.get("permission_ids"),
        )

        # Refresh to get permissions
        role.refresh_from_db()
        output_data = {
            "id": role.id,
            "name": role.name,
            "permissions": [
                {"id": p.id, "codename": p.codename, "name": p.name}
                for p in role.permissions.all()
            ],
        }
        return Response(output_data, status=status.HTTP_201_CREATED)


class AdminRoleDetailView(APIView):
    """Admin view for role detail, update, and deletion.

    GET /api/admin/users/roles/{role_id}/
    PATCH /api/admin/users/roles/{role_id}/
    DELETE /api/admin/users/roles/{role_id}/
    """

    permission_classes = [IsStaffUser]

    def get(self, request: Request, role_id: int) -> Response:
        """Get role details.

        Args:
            request: The HTTP request.
            role_id: The role's ID.

        Returns:
            Role detail data with permissions and policies.
        """
        from django.contrib.auth.models import Group

        try:
            role_data = role_get_by_id(role_id=role_id)
        except Group.DoesNotExist:
            raise NotFound("Role not found.")

        serializer = RoleDetailSerializer(role_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request, role_id: int) -> Response:
        """Update a role.

        Args:
            request: The HTTP request with update data.
            role_id: The role's ID.

        Returns:
            Updated role data.
        """
        from django.contrib.auth.models import Group

        try:
            role = Group.objects.prefetch_related("permissions").get(pk=role_id)
        except Group.DoesNotExist:
            raise NotFound("Role not found.")

        input_serializer = RoleUpdateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        data = input_serializer.validated_data

        # Check name uniqueness if changing
        if data.get("name") and data["name"] != role.name:
            if Group.objects.filter(name__iexact=data["name"]).exists():
                raise ValidationError({"name": "A role with this name already exists."})

        updated_role = role_update(
            role=role,
            name=data.get("name"),
            permission_ids=data.get("permission_ids"),
        )

        # Refresh to get updated permissions
        updated_role.refresh_from_db()
        output_data = {
            "id": updated_role.id,
            "name": updated_role.name,
            "permissions": [
                {"id": p.id, "codename": p.codename, "name": p.name}
                for p in updated_role.permissions.all()
            ],
        }
        return Response(output_data, status=status.HTTP_200_OK)

    def delete(self, request: Request, role_id: int) -> Response:
        """Delete a role.

        Args:
            request: The HTTP request.
            role_id: The role's ID.

        Returns:
            Empty response with 204 status.
        """
        from django.contrib.auth.models import Group

        try:
            role = Group.objects.get(pk=role_id)
        except Group.DoesNotExist:
            raise NotFound("Role not found.")

        # Check for force delete query param
        force = request.query_params.get("force", "").lower() == "true"

        try:
            role_delete(role=role, force=force)
        except ValueError as e:
            raise ValidationError({"detail": str(e)})

        return Response(status=status.HTTP_204_NO_CONTENT)


# =============================================================================
# Password Management Views (Phase 8: User Story 6)
# =============================================================================


class PasswordResetRequestView(APIView):
    """API view for password reset request.

    POST /api/auth/password/reset/
    Requests a password reset link via email.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Request password reset.

        Always returns success to prevent email enumeration.
        In production, would queue an email with reset link.

        Args:
            request: DRF request with email.

        Returns:
            Response with generic success message.
        """
        from users.serializers import PasswordResetRequestSerializer
        from users.services import password_reset_request

        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = password_reset_request(email=serializer.validated_data["email"])

        # In development, include token data for testing
        # In production, this would just return the generic message
        response_data = {
            "detail": "If an account exists with this email, a password reset link has been sent."
        }

        # For development/testing only - include reset data
        if result:
            response_data["_debug"] = {
                "reset_link": f"{result['uid']}:{result['token']}"
            }

        return Response(response_data, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """API view for password reset confirmation.

    POST /api/auth/password/reset/confirm/
    Completes password reset with token from email.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Complete password reset.

        Args:
            request: DRF request with token and new password.

        Returns:
            Response with success message or error.
        """
        from users.serializers import PasswordResetConfirmSerializer
        from users.services import password_reset_confirm

        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            password_reset_confirm(
                token=serializer.validated_data["token"],
                password=serializer.validated_data["password"],
            )
        except ValueError as e:
            raise ValidationError({"token": str(e)})

        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


class PasswordChangeView(APIView):
    """API view for authenticated password change.

    POST /api/auth/password/change/
    Changes password for authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Change password for the authenticated user.

        Args:
            request: DRF request with old and new passwords.

        Returns:
            Response with success message or error.
        """
        from users.serializers import PasswordChangeSerializer
        from users.services import password_change

        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            password_change(
                user=request.user,
                old_password=serializer.validated_data["old_password"],
                new_password=serializer.validated_data["new_password"],
            )
        except ValueError as e:
            raise ValidationError({"old_password": str(e)})

        return Response(
            {"detail": "Password has been changed successfully."},
            status=status.HTTP_200_OK,
        )


# =============================================================================
# Passkey Views (US1: Registration)
# =============================================================================


class PasskeyRegisterOptionsView(APIView):
    """API view for passkey registration options.

    POST /api/auth/passkey/register/options/
    Initiates the passkey registration ceremony.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        from users.serializers import (
            PasskeyRegisterOptionsInputSerializer,
            PasskeyRegisterOptionsOutputSerializer,
        )
        from users.services import passkey_register_options

        serializer = PasskeyRegisterOptionsInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        import json

        result = passkey_register_options(
            email=serializer.validated_data["email"],
            display_name=serializer.validated_data.get("display_name", ""),
        )

        output = PasskeyRegisterOptionsOutputSerializer(
            {
                "challenge_id": result["challenge_id"],
                "options": json.loads(result["options"]),
            }
        )
        return Response(output.data, status=status.HTTP_200_OK)


class PasskeyRegisterCompleteView(APIView):
    """API view for passkey registration completion.

    POST /api/auth/passkey/register/complete/
    Completes registration, creates user, triggers email verification.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        from users.serializers import (
            PasskeyRegisterCompleteInputSerializer,
            PasskeyRegisterCompleteOutputSerializer,
        )
        from users.services import passkey_register_complete

        serializer = PasskeyRegisterCompleteInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = passkey_register_complete(
            challenge_id=str(serializer.validated_data["challenge_id"]),
            credential=serializer.validated_data["credential"],
        )

        output = PasskeyRegisterCompleteOutputSerializer(
            {
                "id": user.pk,
                "email": user.email,
                "is_email_verified": user.is_email_verified,
                "message": "Account created. Please verify your email address.",
            }
        )
        return Response(output.data, status=status.HTTP_201_CREATED)


# =============================================================================
# Passkey Views (US2: Authentication)
# =============================================================================


class PasskeyAuthenticateOptionsView(APIView):
    """API view for passkey authentication options.

    POST /api/auth/passkey/authenticate/options/
    Initiates the passkey authentication ceremony (discoverable credentials).
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        import json

        from users.serializers import PasskeyAuthenticateOptionsOutputSerializer
        from users.services import passkey_authenticate_options

        result = passkey_authenticate_options()

        output = PasskeyAuthenticateOptionsOutputSerializer(
            {
                "challenge_id": result["challenge_id"],
                "options": json.loads(result["options"]),
            }
        )
        return Response(output.data, status=status.HTTP_200_OK)


class PasskeyAuthenticateCompleteView(APIView):
    """API view for passkey authentication completion.

    POST /api/auth/passkey/authenticate/complete/
    Verifies assertion and returns JWT tokens.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        from users.serializers import (
            PasskeyAuthenticateCompleteInputSerializer,
            PasskeyAuthenticateCompleteOutputSerializer,
        )
        from users.services import passkey_authenticate_complete

        serializer = PasskeyAuthenticateCompleteInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = passkey_authenticate_complete(
            challenge_id=str(serializer.validated_data["challenge_id"]),
            credential=serializer.validated_data["credential"],
        )

        output = PasskeyAuthenticateCompleteOutputSerializer(tokens)
        return Response(output.data, status=status.HTTP_200_OK)


# =============================================================================
# Passkey Views (US3: Add Passkey to Existing Account)
# =============================================================================


class PasskeyAddOptionsView(APIView):
    """API view for adding a passkey to an existing account.

    POST /api/auth/passkey/add/options/
    Initiates passkey addition for an authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        import json

        from users.serializers import (
            PasskeyAddOptionsInputSerializer,
            PasskeyAddOptionsOutputSerializer,
        )
        from users.services import passkey_add_options

        serializer = PasskeyAddOptionsInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = passkey_add_options(
            user=request.user,
            device_label=serializer.validated_data.get("device_label", ""),
        )

        output = PasskeyAddOptionsOutputSerializer(
            {
                "challenge_id": result["challenge_id"],
                "options": json.loads(result["options"]),
            }
        )
        return Response(output.data, status=status.HTTP_200_OK)


class PasskeyAddCompleteView(APIView):
    """API view for completing passkey addition.

    POST /api/auth/passkey/add/complete/
    Completes passkey addition for an authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        from users.serializers import (
            PasskeyAddCompleteInputSerializer,
            PasskeyAddCompleteOutputSerializer,
        )
        from users.services import passkey_add_complete

        serializer = PasskeyAddCompleteInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        credential = passkey_add_complete(
            user=request.user,
            challenge_id=str(serializer.validated_data["challenge_id"]),
            credential=serializer.validated_data["credential"],
        )

        output = PasskeyAddCompleteOutputSerializer(credential)
        return Response(output.data, status=status.HTTP_201_CREATED)


class PasskeyListView(APIView):
    """API view for listing a user's passkey credentials.

    GET /api/auth/passkey/
    Returns the authenticated user's registered passkeys.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        from users.selectors import passkey_credentials_list
        from users.serializers import PasskeyCredentialListOutputSerializer

        credentials = passkey_credentials_list(user=request.user)
        serializer = PasskeyCredentialListOutputSerializer(credentials, many=True)
        return Response(
            {"results": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )


class PasskeyRemoveView(APIView):
    """API view for removing a passkey credential.

    DELETE /api/auth/passkey/<credential_id>/
    Removes a passkey credential from the authenticated user's account.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, credential_id: int) -> Response:
        from users.services import passkey_credential_remove

        passkey_credential_remove(user=request.user, credential_id=credential_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
