"""Test factories for users app."""

import secrets
from datetime import timedelta

import factory
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating CustomUser instances in tests."""

    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "TestPass123!")
    is_active = True
    is_staff = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override create to use the manager's create_user method."""
        password = kwargs.pop("password", None)
        obj = super()._create(model_class, *args, **kwargs)
        if password:
            obj.set_password(password)
            obj.save()
        return obj


class EmailVerificationTokenFactory(factory.django.DjangoModelFactory):
    """Factory for creating EmailVerificationToken instances in tests."""

    class Meta:
        model = "users.EmailVerificationToken"

    user = factory.SubFactory(UserFactory)
    token = factory.LazyFunction(lambda: secrets.token_urlsafe(32))
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
