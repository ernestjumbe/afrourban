"""Services for organization write operations."""

from __future__ import annotations

import os
import uuid
from typing import TYPE_CHECKING, Any, cast

import structlog
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db import IntegrityError, transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from organizations.models import Organization
from organizations.permissions import IsOrganizationOwnerOrAdmin, is_organization_owner

if TYPE_CHECKING:
    from users.models import CustomUser

logger = structlog.get_logger(__name__)

_UNSET = object()
ALLOWED_IMAGE_CONTENT_TYPES = ("image/jpeg", "image/png", "image/webp")
MAX_IMAGE_FILE_SIZE = 5 * 1024 * 1024
DUPLICATE_NAME_ERROR = "You already have an organization with this name."
PHYSICAL_ADDRESS_REQUIRED_ERROR = (
    "Physical address is required for organizations with a physical presence."
)


def normalize_organization_name(*, name: str) -> str:
    """Normalize organization name input before validation or persistence."""

    return name.strip()


def normalize_physical_address(*, physical_address: str | None) -> str | None:
    """Normalize organization physical address input."""

    if physical_address is None:
        return None

    normalized_address = physical_address.strip()
    return normalized_address or None


def organization_name_is_taken(
    *,
    owner_id: int,
    name: str,
    exclude_organization_id: int | None = None,
) -> bool:
    """Check if the owner already has an organization with this name."""

    normalized_name = normalize_organization_name(name=name)
    queryset = Organization.objects.filter(
        owner_id=owner_id,
        name__iexact=normalized_name,
    )
    if exclude_organization_id is not None:
        queryset = queryset.exclude(pk=exclude_organization_id)

    is_taken = queryset.exists()
    log_organization_outcome(
        outcome="name_taken" if is_taken else "name_available",
        owner_id=owner_id,
        organization_name=normalized_name,
        organization_id=exclude_organization_id,
    )
    return is_taken


def validate_presence_mode(
    *,
    is_online_only: bool,
    physical_address: str | None,
) -> str | None:
    """Validate the online-only/physical-address relationship."""

    normalized_address = normalize_physical_address(physical_address=physical_address)
    if is_online_only:
        return None

    if normalized_address is None:
        raise ValidationError(
            {
                "physical_address": [PHYSICAL_ADDRESS_REQUIRED_ERROR]
            }
        )

    return normalized_address


def validate_organization_image(*, uploaded_file: UploadedFile) -> UploadedFile:
    """Validate image type and size for organization branding assets."""

    if uploaded_file.size > MAX_IMAGE_FILE_SIZE:
        raise ValidationError({"file": ["File size exceeds 5MB limit."]})

    content_type = getattr(uploaded_file, "content_type", None)
    if content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise ValidationError(
            {"file": ["Unsupported file format. Use JPEG, PNG, or WebP."]}
        )

    return uploaded_file


def organization_create(
    *,
    owner: "CustomUser",
    name: str,
    description: str,
    organization_type: str,
    is_online_only: bool,
    physical_address: str | None,
) -> Organization:
    """Create an organization for the given owner."""

    normalized_name = normalize_organization_name(name=name)

    try:
        normalized_address = validate_presence_mode(
            is_online_only=is_online_only,
            physical_address=physical_address,
        )
    except ValidationError:
        log_organization_outcome(
            outcome="create_validation_failed",
            owner_id=owner.pk,
            organization_name=normalized_name,
            reason="presence_mode_invalid",
        )
        raise

    if organization_name_is_taken(owner_id=owner.pk, name=normalized_name):
        log_organization_outcome(
            outcome="create_validation_failed",
            owner_id=owner.pk,
            organization_name=normalized_name,
            reason="duplicate_name",
        )
        raise ValidationError({"name": [DUPLICATE_NAME_ERROR]})

    organization = Organization(
        owner=owner,
        name=normalized_name,
        description=description,
        organization_type=organization_type,
        is_online_only=is_online_only,
        physical_address=normalized_address,
    )

    try:
        organization.full_clean()
    except DjangoValidationError as exc:
        errors = _coerce_django_validation_error(exc)
        log_organization_outcome(
            outcome="create_validation_failed",
            owner_id=owner.pk,
            organization_name=normalized_name,
            reason="model_validation_failed",
            details=errors,
        )
        raise ValidationError(errors) from exc

    try:
        with transaction.atomic():
            organization.save()
    except IntegrityError as exc:
        log_organization_outcome(
            outcome="create_validation_failed",
            owner_id=owner.pk,
            organization_name=normalized_name,
            reason="integrity_error",
        )
        raise ValidationError({"name": [DUPLICATE_NAME_ERROR]}) from exc

    log_organization_outcome(
        outcome="create_success",
        owner_id=owner.pk,
        organization_name=organization.name,
        organization_id=organization.pk,
    )
    return organization


def organization_update(
    *,
    organization: Organization,
    actor: "CustomUser",
    name: str | object = _UNSET,
    description: str | object = _UNSET,
    organization_type: str | object = _UNSET,
    is_online_only: bool | object = _UNSET,
    physical_address: str | None | object = _UNSET,
) -> Organization:
    """Update an organization while enforcing owner-only write rules."""

    _ensure_organization_write_access(
        actor=actor,
        organization=organization,
        operation="update",
    )

    normalized_name = organization.name
    if name is not _UNSET:
        normalized_name = normalize_organization_name(name=str(name))
        if organization_name_is_taken(
            owner_id=organization.owner_id,
            name=normalized_name,
            exclude_organization_id=organization.pk,
        ):
            log_organization_outcome(
                outcome="update_validation_failed",
                owner_id=organization.owner_id,
                actor_user_id=getattr(actor, "pk", None),
                organization_name=normalized_name,
                organization_id=organization.pk,
                reason="duplicate_name",
            )
            raise ValidationError({"name": [DUPLICATE_NAME_ERROR]})

    resulting_is_online_only = organization.is_online_only
    if is_online_only is not _UNSET:
        resulting_is_online_only = bool(is_online_only)

    address_candidate: str | None
    if physical_address is _UNSET:
        address_candidate = organization.physical_address
    else:
        address_candidate = cast("str | None", physical_address)

    try:
        normalized_address = validate_presence_mode(
            is_online_only=resulting_is_online_only,
            physical_address=address_candidate,
        )
    except ValidationError:
        log_organization_outcome(
            outcome="update_validation_failed",
            owner_id=organization.owner_id,
            actor_user_id=getattr(actor, "pk", None),
            organization_name=normalized_name,
            organization_id=organization.pk,
            reason="presence_mode_invalid",
        )
        raise

    fields_to_update: list[str] = []

    if name is not _UNSET and organization.name != normalized_name:
        organization.name = normalized_name
        fields_to_update.append("name")

    if description is not _UNSET and organization.description != description:
        organization.description = str(description)
        fields_to_update.append("description")

    if (
        organization_type is not _UNSET
        and organization.organization_type != organization_type
    ):
        organization.organization_type = str(organization_type)
        fields_to_update.append("organization_type")

    if organization.is_online_only != resulting_is_online_only:
        organization.is_online_only = resulting_is_online_only
        fields_to_update.append("is_online_only")

    if organization.physical_address != normalized_address:
        organization.physical_address = normalized_address
        fields_to_update.append("physical_address")

    try:
        organization.full_clean()
    except DjangoValidationError as exc:
        errors = _coerce_django_validation_error(exc)
        log_organization_outcome(
            outcome="update_validation_failed",
            owner_id=organization.owner_id,
            actor_user_id=getattr(actor, "pk", None),
            organization_name=organization.name,
            organization_id=organization.pk,
            reason="model_validation_failed",
            details=errors,
        )
        raise ValidationError(errors) from exc

    if fields_to_update:
        fields_to_update.append("updated_at")
        organization.save(update_fields=fields_to_update)

    log_organization_outcome(
        outcome="update_success",
        owner_id=organization.owner_id,
        actor_user_id=getattr(actor, "pk", None),
        organization_name=organization.name,
        organization_id=organization.pk,
    )
    return organization


def organization_branding_upload(
    *,
    organization: Organization,
    actor: "CustomUser",
    asset_kind: str,
    uploaded_file: UploadedFile,
) -> str:
    """Upload or replace one organization branding asset."""

    _ensure_organization_write_access(
        actor=actor,
        organization=organization,
        operation="branding_upload",
        asset_kind=asset_kind,
    )

    try:
        validated_file = validate_organization_image(uploaded_file=uploaded_file)
    except ValidationError:
        log_organization_branding_outcome(
            outcome="upload_validation_failed",
            owner_id=organization.owner_id,
            actor_user_id=getattr(actor, "pk", None),
            organization_id=organization.pk,
            asset_kind=asset_kind,
            reason="invalid_file",
        )
        raise

    existing_file = getattr(organization, asset_kind)
    if existing_file:
        existing_file.delete(save=False)

    generated_name = _generate_organization_asset_filename(
        original_name=validated_file.name,
        organization_id=organization.pk,
        asset_kind=asset_kind,
    )
    getattr(organization, asset_kind).save(generated_name, validated_file, save=False)
    organization.save(update_fields=[asset_kind, "updated_at"])

    log_organization_branding_outcome(
        outcome="upload_success",
        owner_id=organization.owner_id,
        actor_user_id=getattr(actor, "pk", None),
        organization_id=organization.pk,
        asset_kind=asset_kind,
    )
    return getattr(organization, asset_kind).url


def organization_branding_delete(
    *,
    organization: Organization,
    actor: "CustomUser",
    asset_kind: str,
) -> None:
    """Delete one organization branding asset as a safe no-op when missing."""

    _ensure_organization_write_access(
        actor=actor,
        organization=organization,
        operation="branding_delete",
        asset_kind=asset_kind,
    )

    existing_file = getattr(organization, asset_kind)
    if not existing_file:
        log_organization_branding_outcome(
            outcome="delete_noop",
            owner_id=organization.owner_id,
            actor_user_id=getattr(actor, "pk", None),
            organization_id=organization.pk,
            asset_kind=asset_kind,
        )
        return

    existing_file.delete(save=False)
    setattr(organization, asset_kind, None)
    organization.save(update_fields=[asset_kind, "updated_at"])

    log_organization_branding_outcome(
        outcome="delete_success",
        owner_id=organization.owner_id,
        actor_user_id=getattr(actor, "pk", None),
        organization_id=organization.pk,
        asset_kind=asset_kind,
    )


def log_organization_outcome(
    *,
    outcome: str,
    owner_id: int | None,
    actor_user_id: int | None = None,
    organization_name: str | None,
    organization_id: int | None = None,
    reason: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """Log structured organization lifecycle outcomes."""

    logger.info(
        "organization_operation_outcome",
        outcome=outcome,
        owner_id=owner_id,
        actor_user_id=actor_user_id,
        organization_name=organization_name,
        organization_id=organization_id,
        reason=reason,
        details=details or {},
    )


def log_organization_branding_outcome(
    *,
    outcome: str,
    owner_id: int | None,
    actor_user_id: int | None = None,
    organization_id: int | None,
    asset_kind: str,
    reason: str | None = None,
) -> None:
    """Log structured organization branding outcomes."""

    logger.info(
        "organization_branding_outcome",
        outcome=outcome,
        owner_id=owner_id,
        actor_user_id=actor_user_id,
        organization_id=organization_id,
        asset_kind=asset_kind,
        reason=reason,
    )


def _coerce_django_validation_error(
    exc: DjangoValidationError,
) -> dict[str, list[str]]:
    """Convert Django validation errors into DRF-friendly payloads."""

    if hasattr(exc, "message_dict"):
        return {
            field: [str(message) for message in messages]
            for field, messages in exc.message_dict.items()
        }

    return {"non_field_errors": [str(message) for message in exc.messages]}


def _ensure_organization_write_access(
    *,
    actor: "CustomUser",
    organization: Organization,
    operation: str,
    asset_kind: str | None = None,
) -> None:
    """Raise when the actor is not allowed to mutate the organization."""

    if bool(getattr(actor, "is_staff", False) or getattr(actor, "is_superuser", False)):
        return

    if is_organization_owner(user=actor, organization=organization):
        return

    if asset_kind is None:
        log_organization_outcome(
            outcome=f"{operation}_permission_denied",
            owner_id=organization.owner_id,
            actor_user_id=getattr(actor, "pk", None),
            organization_name=organization.name,
            organization_id=organization.pk,
            reason="not_owner",
        )
    else:
        log_organization_branding_outcome(
            outcome=f"{operation}_permission_denied",
            owner_id=organization.owner_id,
            actor_user_id=getattr(actor, "pk", None),
            organization_id=organization.pk,
            asset_kind=asset_kind,
            reason="not_owner",
        )

    raise PermissionDenied(IsOrganizationOwnerOrAdmin.message)


def _generate_organization_asset_filename(
    *,
    original_name: str,
    organization_id: int,
    asset_kind: str,
) -> str:
    """Generate a predictable-unique filename for branding uploads."""

    ext = os.path.splitext(original_name)[1].lower()
    unique_id = uuid.uuid4().hex[:8]
    return f"{organization_id}_{asset_kind}_{unique_id}{ext}"
