"""Health API views."""

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from health.serializers import HealthStatusSerializer
from health.services import (
    HealthCheckResult,
    evaluate_application_health,
    log_health_check_evaluated,
)


class HealthView(APIView):
    """Public API view for application-process health."""

    permission_classes = [AllowAny]
    authentication_classes: list = []
    throttle_classes: list = []
    serializer_class = HealthStatusSerializer

    @extend_schema(
        summary="Application health check",
        description=(
            "Anonymous health endpoint for monitoring systems and frontend startup "
            "checks. Reports only application-process availability and excludes "
            "external dependency verification."
        ),
        responses={
            200: HealthStatusSerializer,
            503: HealthStatusSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """Return a machine-readable application health result."""

        try:
            result = evaluate_application_health()
        except Exception:
            result = HealthCheckResult.unhealthy(phase="failing")

        log_health_check_evaluated(
            result=result,
            method=request.method,
            path=request.path,
            request_user_id=getattr(request.user, "pk", None),
        )
        serializer = HealthStatusSerializer({"status": result.status})
        return Response(serializer.data, status=result.http_status)
