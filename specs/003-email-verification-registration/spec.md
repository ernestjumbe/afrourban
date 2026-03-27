# Feature Specification: Email Verification for User Registration

**Feature Branch**: `003-email-verification-registration`  
**Created**: 2026-03-27  
**Status**: Draft  
**Input**: User description: "Add an email verification step to the user registration flow."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New User Verifies Email After Registration (Priority: P1)

After completing registration, a newly registered user receives a verification email containing a unique link. The user clicks the link and is taken to the verification page where their email is confirmed as verified.

**Why this priority**: This is the core happy path. Without it, the feature does not function at all. Completing email verification is the primary value delivered and is a prerequisite for all other stories.

**Independent Test**: Can be fully tested by registering a new user, inspecting the sent email, submitting the token to the verification endpoint, and confirming the user's verified status is updated.

**Acceptance Scenarios**:

1. **Given** a user has successfully registered, **When** the registration completes, **Then** a verification email is sent to the address provided during registration.
2. **Given** a verification email has been sent, **When** the user clicks the verification link, **Then** the link directs them to `{base_url}/registration/email-verification?token={token}` with the token as a query parameter.
3. **Given** the user visits the verification URL with a valid, non-expired token, **When** the backend verification endpoint receives the token, **Then** the user's email is marked as verified and a success response is returned.
4. **Given** a user's email is verified, **When** they attempt to log in, **Then** they are permitted to authenticate successfully.

---

### User Story 2 - Unverified User Is Blocked from Login (Priority: P1)

A user who has registered but not yet completed email verification attempts to log in. The system rejects the login attempt with a clear message indicating that email verification is required.

**Why this priority**: This enforces the verification requirement and is equally critical to P1 — without enforcement, the verification step has no functional effect on security or data quality.

**Independent Test**: Can be fully tested by registering a user without completing verification, then attempting to log in and confirming the system returns a login-denied response.

**Acceptance Scenarios**:

1. **Given** a registered user has not verified their email, **When** they attempt to log in with valid credentials, **Then** the system denies the login and returns a response indicating email verification is required.
2. **Given** a registered user's verification token has expired (older than 7 days) without the user verifying, **When** they attempt to log in, **Then** the system still blocks login and indicates verification is required.

---

### User Story 3 - Expired or Invalid Token Is Rejected (Priority: P2)

A user who receives a verification email but does not click the link within 7 days attempts to use the expired link. The system rejects the token and informs the user that the link is no longer valid.

**Why this priority**: Token expiry is a security requirement. An expired token must not be accepted. This can be demonstrated independently of the resend flow.

**Independent Test**: Can be fully tested by creating a token with a past expiry timestamp and submitting it to the verification endpoint, confirming the system returns an error.

**Acceptance Scenarios**:

1. **Given** a verification token was issued more than 7 days ago, **When** the token is submitted to the verification endpoint, **Then** the system returns an error indicating the token has expired.
2. **Given** an invalid or tampered token is submitted, **When** the verification endpoint receives it, **Then** the system returns an error indicating the token is invalid.
3. **Given** a token that has already been used to verify an email is submitted again, **When** the verification endpoint receives it, **Then** the system returns an error indicating the token is no longer valid.

---

### User Story 4 - User Requests a New Verification Email (Priority: P2)

A user who has not yet verified their email and whose token may have expired (or who did not receive the original email) requests a fresh verification email.

**Why this priority**: Without a resend mechanism, users with expired or missing emails are permanently blocked from completing registration. This protects registration completion rates.

**Independent Test**: Can be fully tested by requesting a new verification email for an unverified user and confirming a new email is dispatched with a fresh, valid token.

**Acceptance Scenarios**:

1. **Given** an unverified user submits their email address to the resend endpoint, **When** the request is received, **Then** a new verification email is sent to that address with a fresh 7-day token.
2. **Given** a new verification email is sent, **When** the user clicks the new link, **Then** the verification succeeds normally.
3. **Given** a user whose email is already verified submits their email to the resend endpoint, **When** the request is received, **Then** the system returns the same generic success response as for a valid resend (no distinct error exposed to prevent enumeration).
4. **Given** a non-existent email address is submitted to the resend endpoint, **When** the request is received, **Then** the system returns the same generic success response without indicating whether the address exists.

---

### Edge Cases

- What happens when a user registers with an email address already associated with an unverified account? → The new registration supersedes the previous unverified account: the existing unverified user record and its active token are replaced, and a fresh verification email is dispatched.
- What happens if the verification email cannot be delivered (e.g., invalid email domain)?
- What happens if a user clicks the verification link more than once after it has already been consumed? → The consumed token no longer exists in the database; the endpoint returns an invalid-token error.
- What happens to expired token records in the database? → Expired tokens are deleted from the database at the point they are first rejected by the verification endpoint.
- How does the system behave if the configured base URL setting is absent or misconfigured?
- What happens when a user requests a resend while a valid token is still active?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST automatically send a verification email to the user's registered email address immediately upon successful registration.
- **FR-002**: The verification email MUST be rendered using both a plain text template and an HTML template, with all necessary values including the verification link and base URL passed to each template.
- **FR-003**: Email templates MUST reside within the `templates` directory of the app responsible for user registration.
- **FR-004**: The verification link included in the email MUST direct users to `{base_url}/registration/email-verification?token={token}`, placing the token as a query parameter.
- **FR-005**: The base URL used to construct the verification link MUST be sourced from a configurable app-level setting that can be overridden in the active project settings module.
- **FR-006**: The system MUST expose a REST API endpoint that accepts a verification token and validates it by database lookup against stored token records.
- **FR-007**: Upon successful token validation, the system MUST mark the corresponding user's email address as verified.
- **FR-008**: Verification tokens MUST expire after 7 days from their time of issuance. This expiry duration MUST be configurable via an app-level setting overridable from the project settings module.
- **FR-009**: The system MUST reject login attempts from users whose email address has not been verified, returning a response that clearly distinguishes this failure from incorrect-credential errors.
- **FR-010**: The system MUST reject verification tokens that are expired, already consumed, or otherwise invalid, returning a descriptive error response in each case. Expired token records MUST be deleted from the database at the point of rejection.
- **FR-011**: The system MUST provide an unauthenticated REST API endpoint allowing a user to request a new verification email by supplying their registered email address. If the address belongs to an unverified user, a fresh token MUST be generated and a new email sent. The endpoint MUST return the same response regardless of whether the email address exists or is already verified, to prevent user enumeration.
- **FR-012**: If a registration attempt is made with an email address that belongs to an existing unverified account, the system MUST supersede the previous unverified account (replacing its token) and dispatch a new verification email. Registration attempts against an already-verified email address MUST be rejected as a duplicate.
- **FR-013**: All settings governing registration and verification behaviour (base URL, token expiry duration, sender email address, and any other configurable values) MUST be defined with sensible defaults in the users app and MUST be individually overridable from the active project settings module.

### Key Entities

- **EmailVerificationToken**: Represents a unique, time-limited opaque token stored as a database record, issued to a user upon registration and on resend requests. Associated with exactly one user, carries an expiry timestamp, and tracks whether it has been consumed. Validated exclusively by database lookup; revoked by marking consumed or deleting the record. Requesting a resend supersedes any existing active token.
- **User**: Carries an email-verified status flag. A user without a verified status set cannot complete the authentication flow.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can complete the full email verification journey — from registration through clicking the verification link and receiving a success response — without encountering errors.
- **SC-002**: 100% of login attempts by users with unverified email addresses are rejected with a distinct, informative response that differs from standard incorrect-credential errors.
- **SC-003**: Verification tokens older than the configured expiry window (default 7 days) are rejected 100% of the time by the verification endpoint.
- **SC-004**: All registration-related configuration values can be overridden at the project settings level without modifying the users app source code.
- **SC-005**: Verification emails are rendered with correct personalised values — including the recipient's details, correct verification link, and correct base URL — in both the plain text and HTML variants.
- **SC-006**: A user whose token has expired can request a new verification email, receive it, click the link, and complete verification successfully.

## Assumptions

- The app responsible for user registration is the `users` app already present in the project.
- A resend verification email endpoint is in scope for this feature to ensure users with expired tokens are not permanently blocked.
- The verification token is single-use; once consumed to verify an email, it cannot be used again.
- The frontend page at `{base_url}/registration/email-verification` is out of scope for this feature and will be implemented separately. The backend provides only the API endpoint that the frontend page will call.
- Email delivery success or failure is not within the scope of this feature; failed delivery is treated as an infrastructure and configuration concern.
- A user can have at most one active (non-expired, non-consumed) verification token at any time. Requesting a resend invalidates any previously issued active token.
- Standard authentication error responses are already established; this feature adds a distinct unverified-email error code alongside them.

## Clarifications

### Session 2026-03-27

- Q: How should the verification token be stored and validated? → A: Opaque random token stored in the database — retrieved and validated by DB lookup; revoked by deletion or marking consumed.
- Q: How should the resend verification email endpoint authenticate the requester? → A: Unauthenticated — caller supplies their email address; system silently sends if the address belongs to an unverified user (same response returned regardless to prevent enumeration).
- Q: What should happen when a user registers with an email address that already belongs to an unverified account? → A: Allow re-registration — supersede the previous unverified account and resend a verification email to that address.
- Q: Where should the verification token be placed in the link sent to the user? → A: Query parameter — `{base_url}/registration/email-verification?token={token}`.
- Q: When the verification endpoint rejects an expired token, should the record be deleted immediately or retained? → A: Delete on rejection — expired token records are removed from the database at the point of rejection.
