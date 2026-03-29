"""Test factories for profiles app."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import factory

from profiles.models import Profile
from users.tests.factories import UserFactory

if TYPE_CHECKING:
    from users.models import CustomUser


class ProfileFactory(factory.django.DjangoModelFactory):
    """Factory for creating Profile instances in tests."""

    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    display_name = factory.Faker("name")
    bio = factory.Faker("text", max_nb_chars=200)
    phone_number = ""
    date_of_birth = None
    preferences = factory.LazyFunction(dict)


def profile_visibility_case(*, owned: bool = False) -> dict[str, object]:
    """Build viewer/profile tuples for ownership visibility tests."""

    owner = cast("CustomUser", UserFactory())
    viewer = owner if owned else cast("CustomUser", UserFactory())
    profile = ProfileFactory(user=owner)
    return {
        "viewer": viewer,
        "profile": profile,
        "is_owned": viewer.pk == owner.pk,
    }
