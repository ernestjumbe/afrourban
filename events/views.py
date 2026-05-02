"""API views for events."""

from __future__ import annotations

import structlog
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from events.models import Event
from events.selectors import event_get_by_id
from events.serializers import (
    EventCoverOutputSerializer,
    EventCoverUploadSerializer,
    EventCreateInputSerializer,
    EventDetailSerializer,
    EventUpdateInputSerializer,
)
from events.services import (
    event_cover_delete,
    event_cover_upload,
    event_create,
    event_update,
)

logger = structlog.get_logger(__name__)


def log_event_api_outcome(
    *,
    request: Request,
    outcome: str,
    event_title: str | None,
    event_id: int | None = None,
    organization_id: int | None = None,
    reason: str | None = None,
) -> None:
    """Log API-layer event mutation outcomes."""

    logger.info(
        "event_api_outcome",
        outcome=outcome,
        request_user_id=getattr(request.user, "pk", None),
        event_title=event_title,
        event_id=event_id,
        organization_id=organization_id,
        reason=reason,
        method=request.method,
        path=request.path,
    )


def log_event_cover_api_outcome(
    *,
    request: Request,
    outcome: str,
    event_id: int | None,
    reason: str | None = None,
) -> None:
    """Log API-layer event cover-image mutation outcomes."""

    logger.info(
        "event_cover_api_outcome",
        outcome=outcome,
        request_user_id=getattr(request.user, "pk", None),
        event_id=event_id,
        reason=reason,
        method=request.method,
        path=request.path,
    )


class EventCollectionView(APIView):
    """Authenticated event collection view."""

    permission_classes = [IsAuthenticated]
    serializer_class = EventCreateInputSerializer

    @extend_schema(
        request=EventCreateInputSerializer,
        responses={status.HTTP_201_CREATED: EventDetailSerializer},
    )
    def post(self, request: Request) -> Response:
        """Create a new personal or organization-owned event."""

        input_serializer = EventCreateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        event_title = input_serializer.validated_data["title"]
        organization_id = input_serializer.validated_data.get("organization_id")

        try:
            event = event_create(
                owner=request.user,
                organization_id=organization_id,
                title=event_title,
                description=input_serializer.validated_data["description"],
                category=input_serializer.validated_data.get("category"),
                start_at=input_serializer.validated_data["start_at"],
                end_at=input_serializer.validated_data["end_at"],
                location=input_serializer.validated_data["location"],
                tickets_url=input_serializer.validated_data.get("tickets_url"),
            )
        except PermissionDenied:
            log_event_api_outcome(
                request=request,
                outcome="create_permission_denied",
                event_title=event_title,
                organization_id=organization_id,
                reason="not_owner",
            )
            raise
        except ValidationError:
            log_event_api_outcome(
                request=request,
                outcome="create_validation_failed",
                event_title=event_title,
                organization_id=organization_id,
                reason="validation_error",
            )
            raise

        log_event_api_outcome(
            request=request,
            outcome="create_success",
            event_title=event.title,
            event_id=event.pk,
            organization_id=event.organization_id,
        )
        output_serializer = EventDetailSerializer(
            event,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class EventDetailView(APIView):
    """Authenticated event detail read and mutation view."""

    permission_classes = [IsAuthenticated]
    serializer_class = EventUpdateInputSerializer

    @extend_schema(
        responses={status.HTTP_200_OK: EventDetailSerializer},
    )
    def get(self, request: Request, event_id: int) -> Response:
        """Return one event for any authenticated viewer."""

        event = get_event_or_404(event_id=event_id)
        serializer = EventDetailSerializer(
            event,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=EventUpdateInputSerializer,
        responses={status.HTTP_200_OK: EventDetailSerializer},
    )
    def patch(self, request: Request, event_id: int) -> Response:
        """Update event metadata for the authorized actor."""

        input_serializer = EventUpdateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        event = get_event_or_404(event_id=event_id)

        try:
            updated_event = event_update(
                event=event,
                actor=request.user,
                **input_serializer.validated_data,
            )
        except PermissionDenied:
            log_event_api_outcome(
                request=request,
                outcome="update_permission_denied",
                event_title=event.title,
                event_id=event.pk,
                organization_id=event.organization_id,
                reason="not_owner",
            )
            raise
        except ValidationError:
            log_event_api_outcome(
                request=request,
                outcome="update_validation_failed",
                event_title=event.title,
                event_id=event.pk,
                organization_id=event.organization_id,
                reason="validation_error",
            )
            raise

        log_event_api_outcome(
            request=request,
            outcome="update_success",
            event_title=updated_event.title,
            event_id=updated_event.pk,
            organization_id=updated_event.organization_id,
        )
        output_serializer = EventDetailSerializer(
            updated_event,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class EventCoverView(APIView):
    """Authenticated event cover-image mutation view."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    serializer_class = EventCoverUploadSerializer

    @extend_schema(
        request=EventCoverUploadSerializer,
        responses={status.HTTP_200_OK: EventCoverOutputSerializer},
    )
    def post(self, request: Request, event_id: int) -> Response:
        """Upload or replace an event cover image."""

        input_serializer = EventCoverUploadSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        event = get_event_or_404(event_id=event_id)

        try:
            asset_url = event_cover_upload(
                event=event,
                actor=request.user,
                uploaded_file=input_serializer.validated_data["cover_image"],
            )
        except PermissionDenied:
            log_event_cover_api_outcome(
                request=request,
                outcome="cover_permission_denied",
                event_id=event.pk,
                reason="not_owner",
            )
            raise
        except ValidationError:
            log_event_cover_api_outcome(
                request=request,
                outcome="cover_validation_failed",
                event_id=event.pk,
                reason="validation_error",
            )
            raise

        log_event_cover_api_outcome(
            request=request,
            outcome="cover_upload_success",
            event_id=event.pk,
        )
        output = EventCoverOutputSerializer(
            {
                "asset_url": request.build_absolute_uri(asset_url),
                "message": "Cover image updated successfully.",
            }
        )
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, event_id: int) -> Response:
        """Delete an event cover image."""

        event = get_event_or_404(event_id=event_id)

        try:
            event_cover_delete(
                event=event,
                actor=request.user,
            )
        except PermissionDenied:
            log_event_cover_api_outcome(
                request=request,
                outcome="cover_permission_denied",
                event_id=event.pk,
                reason="not_owner",
            )
            raise

        log_event_cover_api_outcome(
            request=request,
            outcome="cover_delete_success",
            event_id=event.pk,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


def get_event_or_404(*, event_id: int) -> Event:
    """Load one event or raise a 404 error."""

    try:
        return event_get_by_id(event_id=event_id)
    except Event.DoesNotExist as exc:
        raise NotFound("Event not found.") from exc
