# Feature Specification: Username Registration and Email Privacy

**Feature Branch**: `[006-add-username-privacy]`  
**Created**: 2026-03-28  
**Status**: Draft  
**Input**: User description: "Add username to the custom user. Authentication must be performed using email and password. A username must be provided during registration. Use the email as the username for existing users. Make sure no email addresses are included in any API response bodies for objects that are not owned by the user."

## Clarifications

### Session 2026-03-28

- Q: Should privileged roles have exceptions for viewing non-owned email addresses? → A: Admin/staff may receive non-owned emails; non-privileged users may not.
- Q: What username uniqueness policy should apply? → A: Usernames are globally unique and case-insensitive.
- Q: How should existing users who already have usernames be handled during rollout? → A: Backfill only users with missing/blank usernames; keep existing usernames unchanged.
- Q: What username format rules should apply? → A: Letters, numbers, underscore, and dot; length 3-30; must not start with dot; must include at least one letter.
- Q: What username change policy should apply after registration? → A: Users can change their own username with full validation and uniqueness checks; enforce a configurable username change cooldown in days (default 7), applied only after successful username changes and not after initial username creation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register with Username, Login with Email (Priority: P1)

As a new user, I provide a username during registration, but I authenticate using email and password so login behavior remains consistent.

**Why this priority**: Registration and authentication are core account-access flows. If this story fails, users cannot reliably create or access accounts.

**Independent Test**: Can be fully tested by registering a new account with `username`, `email`, and `password`, then confirming login works with email/password and does not require username.

**Acceptance Scenarios**:

1. **Given** a visitor submits valid registration data including a username, **When** the account is created, **Then** the user record includes the submitted username and registration succeeds.
2. **Given** a visitor submits registration data without a username, **When** validation runs, **Then** registration is rejected with a clear validation error on `username`.
3. **Given** a visitor submits a username that starts with `.` or has no letters, **When** validation runs, **Then** registration is rejected with a clear validation error on `username`.
4. **Given** a registered user has valid credentials, **When** they authenticate with email and password, **Then** authentication succeeds without requiring username input.

---

### User Story 2 - Preserve Existing Accounts During Username Rollout (Priority: P2)

As a product owner, I need existing accounts to receive usernames automatically so old users remain valid under the new account rules.

**Why this priority**: This prevents account inconsistency and avoids manual remediation during rollout.

**Independent Test**: Can be fully tested by running the rollout process on pre-existing users and confirming each existing user has a non-empty username derived from their email.

**Acceptance Scenarios**:

1. **Given** a user account exists before rollout and has no username, **When** the rollout migration completes, **Then** the user’s username is set to that user’s email value.
2. **Given** multiple existing accounts, **When** rollout migration completes, **Then** each account has a populated username and no account is deactivated or removed.

---

### User Story 3 - Protect Other Users’ Email Addresses in API Responses (Priority: P3)

As a non-privileged authenticated user, I can see only safe identity data for other users, and I never receive another user’s email address in API response bodies.

**Why this priority**: This reduces exposure of sensitive contact information and aligns API output with privacy expectations.

**Independent Test**: Can be fully tested by comparing API responses for owned vs non-owned user objects and verifying email appears only on owned objects.

**Acceptance Scenarios**:

1. **Given** a response contains a user object owned by the requesting user, **When** the response is returned, **Then** email may be present for that owned object.
2. **Given** a non-privileged requester and a response containing one or more non-owned user objects, **When** the response is returned, **Then** email is omitted from every non-owned object.
3. **Given** an admin or staff requester and a response containing non-owned user objects, **When** the response is returned from authorized admin/staff operations, **Then** email may be included according to role privileges.

---

### User Story 4 - Change Username with Cooldown (Priority: P4)

As an authenticated user, I can change my own username later, but after a successful change I must wait for a cooldown period before changing it again.

**Why this priority**: This protects account identity stability while still allowing legitimate username updates.

**Independent Test**: Can be fully tested by submitting username-change requests before and after cooldown boundaries, including initial first change and duplicate/invalid username attempts.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a valid unique target username, **When** they request their first username change after account creation, **Then** the change succeeds and is not blocked by cooldown.
2. **Given** an authenticated user changed username recently, **When** they request another username change before the cooldown period ends, **Then** the request is rejected due to active cooldown.
3. **Given** an authenticated user changed username and the cooldown period has elapsed, **When** they request another valid username change, **Then** the change succeeds.
4. **Given** an authenticated user requests a username change to an invalid or case-insensitive duplicate username, **When** validation runs, **Then** the request is rejected.

### Edge Cases

- What happens when a new username value (ignoring letter case) is already used by another account?
- How does the system handle registration when username is blank, whitespace-only, starts with `.`, contains unsupported characters, or contains no letters?
- What happens when a username change request arrives exactly at the cooldown boundary time?
- How does the system apply cooldown if the configured cooldown days value changes while users are already in cooldown?
- How are bulk/list endpoints handled when they return a mix of owned and non-owned user objects?
- What happens if an existing user already has a username before rollout migration runs?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST store a `username` value for every user account.
- **FR-002**: System MUST require `username` during new user registration.
- **FR-003**: System MUST reject registration requests that omit `username`, provide an invalid `username`, or provide a username that matches an existing username case-insensitively.
- **FR-003a**: System MUST enforce username format rules: allowed characters are letters, numbers, underscore (`_`), and dot (`.`); length MUST be 3 to 30 characters; username MUST NOT start with `.`; username MUST include at least one letter.
- **FR-004**: System MUST continue authenticating users with `email` and `password`.
- **FR-005**: System MUST NOT require `username` as an authentication credential.
- **FR-006**: System MUST populate `username` for pre-existing users that have missing or blank usernames by copying each user’s current email value during rollout.
- **FR-007**: System MUST preserve all existing user accounts during username backfill without deleting or deactivating accounts.
- **FR-008**: System MUST include a user’s email address when the serialized user object is owned by the authenticated requester.
- **FR-009**: System MUST exclude email fields from all API response objects representing users not owned by non-privileged requesters.
- **FR-010**: System MUST allow admin/staff requesters to receive non-owned emails in authorized admin/staff API operations.
- **FR-011**: System MUST apply ownership and role-based email visibility rules consistently across list, detail, and nested API response objects.
- **FR-012**: System MUST update API documentation to reflect `username` registration requirements and ownership-based email visibility rules.
- **FR-013**: System MUST enforce global case-insensitive uniqueness for usernames across all user accounts.
- **FR-014**: System MUST allow authenticated users to change their own username after registration.
- **FR-015**: System MUST apply the same username format and case-insensitive uniqueness validation rules to username changes as to registration.
- **FR-016**: System MUST enforce a username change cooldown period between successful username changes.
- **FR-017**: System MUST use a default username change cooldown of 7 days.
- **FR-018**: System MUST allow configuration of the username change cooldown duration in whole days.
- **FR-019**: Username change cooldown MUST start only after a successful username change and MUST NOT apply to initial username creation or migration backfill.

### API Contract & Versioning *(mandatory when APIs are added or changed)*

- **API-001**: Updated API documentation MUST be generated and maintained with `drf-spectacular`, with OpenAPI 3.0+ schema output.
- **API-002**: All changed endpoints MUST remain explicitly versioned under `/api/v1/` unless a new version is introduced.
- **API-003**: Any added or changed routes for this feature MUST be registered in `api_urlpatterns` in main `urls.py` and included under `/api/`.
- **API-004**: Because response payload visibility rules change, the specification MUST document compatibility impact and consumer migration guidance if clients previously expected non-owned emails.
- **API-005**: If any endpoint behavior is deprecated as part of this change, deprecation date, planned removal date, and migration path MUST be documented.

### Key Entities *(include if feature involves data)*

- **User Account**: Core identity record with account credentials and attributes including email, username, active status, and verification state.
- **Owned User View**: API response projection for user objects owned by the authenticated requester; may include private contact fields such as email.
- **Non-Owned User View**: API response projection for user objects not owned by the requester; must exclude email and expose only non-sensitive identity fields.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of successful new registrations include a non-empty username.
- **SC-002**: 100% of login attempts using valid email/password credentials continue to succeed after the change.
- **SC-003**: 100% of pre-existing user accounts have username populated after rollout completion.
- **SC-004**: 0 API response objects for non-owned users contain an email address when requested by non-privileged users in validation test coverage.
- **SC-005**: 100% of admin/staff endpoints that are designated to expose non-owned emails enforce admin/staff authorization in validation coverage.
- **SC-006**: 100% of documented registration and user-visibility examples match actual API behavior.
- **SC-007**: 100% of attempted duplicate usernames (case-insensitive match) are rejected in validation test coverage.
- **SC-008**: 100% of usernames that violate defined format rules are rejected in validation test coverage.
- **SC-009**: 100% of username-change requests made before the cooldown expires are rejected in validation test coverage.
- **SC-010**: 100% of first username-change requests after initial account creation are evaluated without cooldown blocking.
- **SC-011**: 100% of username-change validation behavior matches configured cooldown days in validation test coverage.

## Assumptions

- Existing user emails are already valid and unique, making email-to-username backfill deterministic.
- Existing users with non-empty usernames keep their current username during rollout.
- Ownership for response redaction is determined by comparing the authenticated requester to the user represented by each response object.
- Endpoints that return only the authenticated user’s own account data may continue exposing that user’s email.
- Admin/staff privileges are the only role-based exception allowed for non-owned email visibility.
- Username change cooldown is a global setting measured in whole days from the most recent successful username change.
- Username format will follow current product identity conventions without introducing a separate aliasing system in this feature.
