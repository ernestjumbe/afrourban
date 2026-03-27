"""Test factories for profiles app."""

import factory

from profiles.models import Profile
from users.tests.factories import UserFactory


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
