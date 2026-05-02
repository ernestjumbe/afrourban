# Organization Profiles Specification

## 1. Overview
This specification details the creation of a new, standalone Django app called `organizations` (or `businesses`). The app will manage organizational entities such as restaurants, barbershops, bars, night clubs, event organizers, and dance crews. By separating this from the existing individual `Profile` model, the system maintains a clean data architecture that strictly differentiates human users from business entities.

## 2. Core Requirements
An Organization must:
- Be owned by a registered application user.
- Include a descriptive text (description/bio).
- Support optional branding (profile image/logo and cover image).
- Have a defined categorization/type to identify the nature of the organization.
- Support both physical locations and online-only presences.

## 3. Data Model Definition

### 3.1 Organization Type Choices
Instead of hardcoding every possible future type into the database schema via migrations, the types should be implemented using Django's `models.TextChoices` for maintainability and performance.

**Proposed Types:**
- Restaurant
- Barber
- Hair Salon
- Bar
- Night Club
- Event Organizer
- Dance Crew
- Online Community
- Retail Store
- *Other*

### 3.2 `Organization` Model
The core model will store the business details and relationship to the owner.

**Fields:**
- **`owner`**: `ForeignKey(settings.AUTH_USER_MODEL)` 
  - *Description*: The registered user who creates and manages the organization.
  - *Relationship*: One-to-Many (a user can own multiple organizations).
- **`name`**: `CharField(max_length=255)`
  - *Description*: The public name of the organization.
- **`description`**: `TextField()`
  - *Description*: Required detailed description or bio of the organization.
- **`organization_type`**: `CharField(choices=OrganizationType.choices)`
  - *Description*: The primary category of the organization (e.g., "Restaurant").
- **`is_online_only`**: `BooleanField(default=False)`
  - *Description*: Flag indicating if the organization operates entirely online without a physical storefront.
- **`physical_address`**: `TextField(blank=True, null=True)`
  - *Description*: The physical location of the organization. Required conditionally at the application level if `is_online_only` is False.
- **`logo`**: `ImageField(upload_to='organizations/logos/', blank=True, null=True)`
  - *Description*: Optional profile image or logo.
- **`cover_image`**: `ImageField(upload_to='organizations/covers/', blank=True, null=True)`
  - *Description*: Optional banner or cover image for the organization's page.
- **`created_at`** / **`updated_at`**: `DateTimeField(auto_now_add=True)` / `DateTimeField(auto_now=True)`
  - *Description*: Standard audit timestamps.

## 4. API Endpoints (Django REST Framework)

### 4.1 REST Resources
- **`GET /api/v1/organizations/`**: List all organizations (with optional filtering by type, online/offline status, or owner).
- **`POST /api/v1/organizations/`**: Create a new organization. Requires authentication. The `owner` is automatically set to `request.user`.
- **`GET /api/v1/organizations/{id}/`**: Retrieve details of a specific organization.
- **`PATCH/PUT /api/v1/organizations/{id}/`**: Update organization details. Restricted to the `owner` of the organization.
- **`DELETE /api/v1/organizations/{id}/`**: Delete an organization. Restricted to the `owner`.

### 4.2 Permissions & Security
- **IsAuthenticated**: Required for creating an organization.
- **IsOwnerOrReadOnly**: Custom permission class ensuring that while anyone (or any authenticated user, depending on privacy settings) can view the organization profile, only the registered user designated as the `owner` can mutate or delete the record.

## 5. Validation Rules
- **Address Enforcement**: If `is_online_only` is set to `False`, the system should validate (e.g., via the DRF Serializer's `validate()` method) that `physical_address` is provided. If `is_online_only` is `True`, `physical_address` can be cleared or ignored.
- **Image Constraints**: `logo` and `cover_image` should enforce standard size and dimension limits tailored to the application's media storage policies (e.g., max 5MB, accepted formats JPEG/PNG/WebP).

## 6. Future Extensibility (Not for immediate implementation)
By modeling this independently, the following features become trivial to add in subsequent iterations:
- **Multiple Administrators:** Creating an intermediary `OrganizationMember` model to allow the owner to invite other users to manage the page.
- **Operating Hours:** Adding an `OperatingHours` model linked via ForeignKey to the Organization.
- **Verification:** An `is_verified` boolean field specifically for businesses to indicate official platform blessing them as official entities, separate from user age verification.