"""API views for organizations."""

from __future__ import annotations

import structlog
from drf_spectacular.utils import extend_schema
from django.http import QueryDict
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from organizations.models import Organization
from organizations.serializers import (
    OrganizationBrandingOutputSerializer,
    OrganizationCoverUploadSerializer,
    OrganizationCreateInputSerializer,
    OrganizationDetailSerializer,
    OrganizationListQuerySerializer,
    OrganizationListResponseSerializer,
    OrganizationLogoUploadSerializer,
    OrganizationSummarySerializer,
    OrganizationUpdateInputSerializer,
)
from organizations.selectors import organization_get_by_id, organization_list
from organizations.services import (
    organization_branding_delete,
    organization_branding_upload,
    organization_create,
    organization_update,
)

logger = structlog.get_logger(__name__)


def log_organization_api_outcome(
    *,
    request: Request,
    outcome: str,
    organization_name: str | None,
    organization_id: int | None = None,
    reason: str | None = None,
) -> None:
    """Log API-layer organization mutation outcomes."""

    logger.info(
        "organization_api_outcome",
        outcome=outcome,
        request_user_id=getattr(request.user, "pk", None),
        organization_name=organization_name,
        organization_id=organization_id,
        reason=reason,
        method=request.method,
        path=request.path,
    )


def log_organization_branding_api_outcome(
    *,
    request: Request,
    outcome: str,
    organization_id: int | None,
    asset_kind: str,
    reason: str | None = None,
) -> None:
    """Log API-layer organization branding outcomes."""

    logger.info(
        "organization_branding_api_outcome",
        outcome=outcome,
        request_user_id=getattr(request.user, "pk", None),
        organization_id=organization_id,
        asset_kind=asset_kind,
        reason=reason,
        method=request.method,
        path=request.path,
    )


class OrganizationCollectionView(APIView):
    """Authenticated organization collection view."""

    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationCreateInputSerializer

    @extend_schema(
        parameters=[OrganizationListQuerySerializer],
        responses={status.HTTP_200_OK: OrganizationListResponseSerializer},
    )
    def get(self, request: Request) -> Response:
        """List organizations with filtering, ordering, and pagination."""

        query_serializer = OrganizationListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        page = query_serializer.validated_data["page"]
        page_size = query_serializer.validated_data["page_size"]
        queryset = organization_list(
            owner=request.user,
            owner_scope=query_serializer.validated_data["owner_scope"],
            organization_type=query_serializer.validated_data.get("organization_type"),
            is_online_only=query_serializer.validated_data.get("is_online_only"),
            search=query_serializer.validated_data.get("search"),
            ordering=query_serializer.validated_data["ordering"],
        )

        count = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        organizations = queryset[start:end]

        serializer = OrganizationSummarySerializer(
            organizations,
            many=True,
            context={"request": request},
        )
        return Response(
            {
                "count": count,
                "next": _build_pagination_url(
                    request=request,
                    page=page + 1,
                    page_size=page_size,
                )
                if end < count
                else None,
                "previous": _build_pagination_url(
                    request=request,
                    page=page - 1,
                    page_size=page_size,
                )
                if page > 1
                else None,
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=OrganizationCreateInputSerializer,
        responses={status.HTTP_201_CREATED: OrganizationDetailSerializer},
    )
    def post(self, request: Request) -> Response:
        """Create a new organization owned by the authenticated user."""

        input_serializer = OrganizationCreateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        organization_name = input_serializer.validated_data["name"]

        try:
            organization = organization_create(
                owner=request.user,
                name=organization_name,
                description=input_serializer.validated_data["description"],
                organization_type=input_serializer.validated_data[
                    "organization_type"
                ],
                is_online_only=input_serializer.validated_data["is_online_only"],
                physical_address=input_serializer.validated_data.get(
                    "physical_address"
                ),
            )
        except ValidationError:
            log_organization_api_outcome(
                request=request,
                outcome="create_validation_failed",
                organization_name=organization_name,
                reason="validation_error",
            )
            raise

        log_organization_api_outcome(
            request=request,
            outcome="create_success",
            organization_name=organization.name,
            organization_id=organization.pk,
        )
        output_serializer = OrganizationDetailSerializer(
            organization,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class OrganizationDetailView(APIView):
    """Authenticated organization detail read and mutation view."""

    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationUpdateInputSerializer

    @extend_schema(
        responses={status.HTTP_200_OK: OrganizationDetailSerializer},
    )
    def get(self, request: Request, organization_id: int) -> Response:
        """Return one organization for any authenticated viewer."""

        organization = get_organization_or_404(organization_id=organization_id)
        serializer = OrganizationDetailSerializer(
            organization,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=OrganizationUpdateInputSerializer,
        responses={status.HTTP_200_OK: OrganizationDetailSerializer},
    )
    def patch(self, request: Request, organization_id: int) -> Response:
        """Update organization metadata for the owner."""

        input_serializer = OrganizationUpdateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        organization = get_organization_or_404(organization_id=organization_id)

        try:
            updated_organization = organization_update(
                organization=organization,
                actor=request.user,
                **input_serializer.validated_data,
            )
        except PermissionDenied:
            log_organization_api_outcome(
                request=request,
                outcome="update_permission_denied",
                organization_name=organization.name,
                organization_id=organization.pk,
                reason="not_owner",
            )
            raise
        except ValidationError:
            log_organization_api_outcome(
                request=request,
                outcome="update_validation_failed",
                organization_name=organization.name,
                organization_id=organization.pk,
                reason="validation_error",
            )
            raise

        log_organization_api_outcome(
            request=request,
            outcome="update_success",
            organization_name=updated_organization.name,
            organization_id=updated_organization.pk,
        )
        output_serializer = OrganizationDetailSerializer(
            updated_organization,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class OrganizationLogoView(APIView):
    """Authenticated organization logo mutation view."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    serializer_class = OrganizationLogoUploadSerializer

    @extend_schema(
        request=OrganizationLogoUploadSerializer,
        responses={status.HTTP_200_OK: OrganizationBrandingOutputSerializer},
    )
    def post(self, request: Request, organization_id: int) -> Response:
        """Upload or replace an organization logo."""

        input_serializer = OrganizationLogoUploadSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        organization = get_organization_or_404(organization_id=organization_id)

        try:
            asset_url = organization_branding_upload(
                organization=organization,
                actor=request.user,
                asset_kind="logo",
                uploaded_file=input_serializer.validated_data["logo"],
            )
        except PermissionDenied:
            log_organization_branding_api_outcome(
                request=request,
                outcome="logo_permission_denied",
                organization_id=organization.pk,
                asset_kind="logo",
                reason="not_owner",
            )
            raise
        except ValidationError:
            log_organization_branding_api_outcome(
                request=request,
                outcome="logo_validation_failed",
                organization_id=organization.pk,
                asset_kind="logo",
                reason="validation_error",
            )
            raise

        log_organization_branding_api_outcome(
            request=request,
            outcome="logo_upload_success",
            organization_id=organization.pk,
            asset_kind="logo",
        )
        output = OrganizationBrandingOutputSerializer(
            {
                "asset_url": request.build_absolute_uri(asset_url),
                "message": "Logo updated successfully.",
            }
        )
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, organization_id: int) -> Response:
        """Delete the organization logo."""

        organization = get_organization_or_404(organization_id=organization_id)

        try:
            organization_branding_delete(
                organization=organization,
                actor=request.user,
                asset_kind="logo",
            )
        except PermissionDenied:
            log_organization_branding_api_outcome(
                request=request,
                outcome="logo_permission_denied",
                organization_id=organization.pk,
                asset_kind="logo",
                reason="not_owner",
            )
            raise

        log_organization_branding_api_outcome(
            request=request,
            outcome="logo_delete_success",
            organization_id=organization.pk,
            asset_kind="logo",
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrganizationCoverView(APIView):
    """Authenticated organization cover-image mutation view."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    serializer_class = OrganizationCoverUploadSerializer

    @extend_schema(
        request=OrganizationCoverUploadSerializer,
        responses={status.HTTP_200_OK: OrganizationBrandingOutputSerializer},
    )
    def post(self, request: Request, organization_id: int) -> Response:
        """Upload or replace an organization cover image."""

        input_serializer = OrganizationCoverUploadSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        organization = get_organization_or_404(organization_id=organization_id)

        try:
            asset_url = organization_branding_upload(
                organization=organization,
                actor=request.user,
                asset_kind="cover_image",
                uploaded_file=input_serializer.validated_data["cover_image"],
            )
        except PermissionDenied:
            log_organization_branding_api_outcome(
                request=request,
                outcome="cover_permission_denied",
                organization_id=organization.pk,
                asset_kind="cover_image",
                reason="not_owner",
            )
            raise
        except ValidationError:
            log_organization_branding_api_outcome(
                request=request,
                outcome="cover_validation_failed",
                organization_id=organization.pk,
                asset_kind="cover_image",
                reason="validation_error",
            )
            raise

        log_organization_branding_api_outcome(
            request=request,
            outcome="cover_upload_success",
            organization_id=organization.pk,
            asset_kind="cover_image",
        )
        output = OrganizationBrandingOutputSerializer(
            {
                "asset_url": request.build_absolute_uri(asset_url),
                "message": "Cover image updated successfully.",
            }
        )
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, organization_id: int) -> Response:
        """Delete the organization cover image."""

        organization = get_organization_or_404(organization_id=organization_id)

        try:
            organization_branding_delete(
                organization=organization,
                actor=request.user,
                asset_kind="cover_image",
            )
        except PermissionDenied:
            log_organization_branding_api_outcome(
                request=request,
                outcome="cover_permission_denied",
                organization_id=organization.pk,
                asset_kind="cover_image",
                reason="not_owner",
            )
            raise

        log_organization_branding_api_outcome(
            request=request,
            outcome="cover_delete_success",
            organization_id=organization.pk,
            asset_kind="cover_image",
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


def get_organization_or_404(*, organization_id: int) -> Organization:
    """Load one organization or raise a 404 error."""

    try:
        return organization_get_by_id(organization_id=organization_id)
    except Organization.DoesNotExist as exc:
        raise NotFound("Organization not found.") from exc


def _build_pagination_url(
    *,
    request: Request,
    page: int,
    page_size: int,
) -> str:
    """Build a pagination URL while preserving active collection filters."""

    query_params: QueryDict = request.query_params.copy()
    query_params["page"] = str(page)
    query_params["page_size"] = str(page_size)
    return f"{request.build_absolute_uri(request.path)}?{query_params.urlencode()}"
