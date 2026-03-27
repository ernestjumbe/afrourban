"""Tests for email verification: US1, US2, and US3."""

from datetime import timedelta

import pytest
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from users.models import EmailVerificationToken
from users.tests.factories import EmailVerificationTokenFactory, UserFactory


@pytest.mark.django_db
class TestRegisterSendsVerificationEmail:
    """Registration should dispatch a verification email."""

    def test_register_sends_verification_email(self, mailoutbox):
        client = APIClient()
        response = client.post(
            "/api/auth/register/",
            {
                "email": "new@example.com",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            },
            format="json",
        )

        assert response.status_code == 201
        assert len(mailoutbox) == 1

        mail = mailoutbox[0]
        assert "new@example.com" in mail.to
        assert "Verify your email" in mail.subject


@pytest.mark.django_db
class TestVerifyValidToken:
    """POST /api/auth/email-verification/verify/ with a valid token."""

    def test_verify_valid_token_returns_200(self):
        user = UserFactory(is_email_verified=False)
        token_obj = EmailVerificationTokenFactory(user=user)

        client = APIClient()
        response = client.post(
            "/api/auth/email-verification/verify/",
            {"token": token_obj.token},
            format="json",
        )

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_verify_marks_email_verified(self):
        user = UserFactory(is_email_verified=False)
        token_obj = EmailVerificationTokenFactory(user=user)

        client = APIClient()
        client.post(
            "/api/auth/email-verification/verify/",
            {"token": token_obj.token},
            format="json",
        )

        user.refresh_from_db()
        assert user.is_email_verified is True

    def test_verify_deletes_token(self):
        user = UserFactory(is_email_verified=False)
        token_obj = EmailVerificationTokenFactory(user=user)

        client = APIClient()
        client.post(
            "/api/auth/email-verification/verify/",
            {"token": token_obj.token},
            format="json",
        )

        assert not EmailVerificationToken.objects.filter(pk=token_obj.pk).exists()


@pytest.mark.django_db
class TestVerifiedUserCanLogin:
    """After verification the user should be able to obtain JWT tokens."""

    def test_verified_user_can_login(self):
        user = UserFactory(is_email_verified=True)
        user.set_password("TestPass123!")
        user.save()

        client = APIClient()
        response = client.post(
            "/api/auth/token/",
            {"email": user.email, "password": "TestPass123!"},
            format="json",
        )

        assert response.status_code == 200
        data = response.json()
        assert "access" in data
        assert "refresh" in data


@pytest.mark.django_db
class TestRegisterSupersedesUnverified:
    """Re-registering with an unverified email replaces the old account."""

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_register_supersedes_existing_unverified_account(self):
        # Create an unverified user
        old_user = UserFactory(is_email_verified=False)
        old_email = old_user.email
        EmailVerificationTokenFactory(user=old_user)

        client = APIClient()
        response = client.post(
            "/api/auth/register/",
            {
                "email": old_email,
                "password": "NewStrongPass123!",
                "password_confirm": "NewStrongPass123!",
            },
            format="json",
        )

        assert response.status_code == 201

        # Old user should be gone; new user with same email exists
        from django.contrib.auth import get_user_model

        User = get_user_model()
        users = User.objects.filter(email__iexact=old_email)
        assert users.count() == 1
        new_user = users.first()
        assert new_user.pk != old_user.pk
        assert new_user.is_email_verified is False

        # A fresh token should exist for the new user
        assert EmailVerificationToken.objects.filter(user=new_user).exists()


# =============================================================================
# US2: Unverified User Is Blocked from Login
# =============================================================================


@pytest.mark.django_db
class TestUnverifiedUserLoginBlocked:
    """Users with is_email_verified=False cannot obtain JWT tokens."""

    def test_unverified_user_login_blocked_returns_401(self):
        user = UserFactory(is_email_verified=False)
        user.set_password("TestPass123!")
        user.save()

        client = APIClient()
        response = client.post(
            "/api/auth/token/",
            {"email": user.email, "password": "TestPass123!"},
            format="json",
        )

        assert response.status_code == 401

    def test_unverified_user_error_code_is_email_not_verified(self):
        user = UserFactory(is_email_verified=False)
        user.set_password("TestPass123!")
        user.save()

        client = APIClient()
        response = client.post(
            "/api/auth/token/",
            {"email": user.email, "password": "TestPass123!"},
            format="json",
        )

        data = response.json()
        assert data["code"] == "email_not_verified"
        assert data["detail"] == "Email address has not been verified."

    def test_verified_user_login_succeeds(self):
        user = UserFactory(is_email_verified=True)
        user.set_password("TestPass123!")
        user.save()

        client = APIClient()
        response = client.post(
            "/api/auth/token/",
            {"email": user.email, "password": "TestPass123!"},
            format="json",
        )

        assert response.status_code == 200
        data = response.json()
        assert "access" in data
        assert "refresh" in data

    def test_expired_token_user_login_still_blocked(self):
        """A user whose token expired (but was never verified) is still blocked."""
        user = UserFactory(is_email_verified=False)
        user.set_password("TestPass123!")
        user.save()
        EmailVerificationTokenFactory(
            user=user,
            expires_at=timezone.now() - timedelta(days=1),
        )

        client = APIClient()
        response = client.post(
            "/api/auth/token/",
            {"email": user.email, "password": "TestPass123!"},
            format="json",
        )

        assert response.status_code == 401
        assert response.json()["code"] == "email_not_verified"


# =============================================================================
# US3: Expired or Invalid Token Is Rejected
# =============================================================================


@pytest.mark.django_db
class TestExpiredOrInvalidTokenRejected:
    """Verification endpoint differentiates expired, invalid, and consumed tokens."""

    def test_expired_token_returns_400_token_expired(self):
        token_obj = EmailVerificationTokenFactory(
            expires_at=timezone.now() - timedelta(days=1),
        )

        client = APIClient()
        response = client.post(
            "/api/auth/email-verification/verify/",
            {"token": token_obj.token},
            format="json",
        )

        assert response.status_code == 400
        assert response.json()["code"] == "token_expired"

    def test_expired_token_is_deleted_from_db(self):
        token_obj = EmailVerificationTokenFactory(
            expires_at=timezone.now() - timedelta(days=1),
        )
        token_value = token_obj.token

        client = APIClient()
        client.post(
            "/api/auth/email-verification/verify/",
            {"token": token_value},
            format="json",
        )

        assert not EmailVerificationToken.objects.filter(token=token_value).exists()

    def test_invalid_token_string_returns_400_token_invalid(self):
        client = APIClient()
        response = client.post(
            "/api/auth/email-verification/verify/",
            {"token": "completely-bogus-token-string"},
            format="json",
        )

        assert response.status_code == 400
        assert response.json()["code"] == "token_invalid"

    def test_already_consumed_token_returns_400_token_invalid(self):
        """A token that was already used (and deleted) is treated as invalid."""
        token_obj = EmailVerificationTokenFactory()
        token_value = token_obj.token

        # Consume the token
        client = APIClient()
        client.post(
            "/api/auth/email-verification/verify/",
            {"token": token_value},
            format="json",
        )

        # Try again with the same token
        response = client.post(
            "/api/auth/email-verification/verify/",
            {"token": token_value},
            format="json",
        )

        assert response.status_code == 400
        assert response.json()["code"] == "token_invalid"


# =============================================================================
# US4: User Requests a New Verification Email
# =============================================================================


@pytest.mark.django_db
class TestResendVerificationEmail:
    """Resend endpoint is enumeration-safe and replaces old tokens."""

    def test_resend_for_unverified_user_sends_email(self):
        user = UserFactory(is_email_verified=False)

        client = APIClient()
        response = client.post(
            "/api/auth/email-verification/resend/",
            {"email": user.email},
            format="json",
        )

        assert response.status_code == 200
        from django.core import mail

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [user.email]

    def test_resend_creates_new_token(self):
        user = UserFactory(is_email_verified=False)
        old_token = EmailVerificationTokenFactory(user=user)
        old_token_value = old_token.token

        client = APIClient()
        client.post(
            "/api/auth/email-verification/resend/",
            {"email": user.email},
            format="json",
        )

        assert EmailVerificationToken.objects.filter(user=user).exists()
        new_token = EmailVerificationToken.objects.get(user=user)
        assert new_token.token != old_token_value

    def test_resend_deletes_old_token(self):
        user = UserFactory(is_email_verified=False)
        old_token = EmailVerificationTokenFactory(user=user)
        old_token_value = old_token.token

        client = APIClient()
        client.post(
            "/api/auth/email-verification/resend/",
            {"email": user.email},
            format="json",
        )

        assert not EmailVerificationToken.objects.filter(token=old_token_value).exists()

    def test_resend_for_verified_user_returns_200_no_email_sent(self):
        user = UserFactory(is_email_verified=True)

        client = APIClient()
        response = client.post(
            "/api/auth/email-verification/resend/",
            {"email": user.email},
            format="json",
        )

        assert response.status_code == 200
        from django.core import mail

        assert len(mail.outbox) == 0

    def test_resend_for_unknown_email_returns_200_no_email_sent(self):
        client = APIClient()
        response = client.post(
            "/api/auth/email-verification/resend/",
            {"email": "nobody@example.com"},
            format="json",
        )

        assert response.status_code == 200
        from django.core import mail

        assert len(mail.outbox) == 0
