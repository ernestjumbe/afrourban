"""Health serializers."""

from rest_framework import serializers


class HealthStatusSerializer(serializers.Serializer):
    """Serializer for the health endpoint response contract."""

    status = serializers.ChoiceField(
        choices=("healthy", "unhealthy"),
        read_only=True,
    )
