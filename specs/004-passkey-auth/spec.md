# Feature Specification: Passkey Registration & Authentication

**Feature Branch**: `004-passkey-auth`  
**Created**: 2026-03-27  
**Status**: Draft  
**Input**: User description: "Implement an alternative registration and authentication flow that supports Passkey (https://webauthn.io/). If a user is registering using Passkey, they must also provide their email. Registration will follow the email verification flow and the user will only be able to authenticate using if their email has been verified. It must be possible for a user to add their passkey after they have already registered and verified their email."

## Clarifications

### Session 2026-03-27

- Q: Should passkey authentication require the user to enter their email first, or use discoverable credentials (resident keys) for username-less login? → A: Discoverable credentials (resident keys) — passkey identifies the user automatically, no email entry needed.
- Q: Should there be a maximum number of passkey credentials per user? → A: Yes, limit to 5 passkeys per user.
- Q: How long should a WebAuthn challenge remain valid before expiring? → A: 5 minutes.
- Q: When sign count indicates credential cloning, should the system also disable the credential? → A: Yes, reject the attempt and disable the credential until the user removes and re-adds it.
- Q: Should account recovery for passkey-only users who lose all devices be in scope? → A: Out of scope — documented as a known limitation; recovery will be a separate feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New User Registers with Passkey (Priority: P1)

A new visitor chooses to register using a passkey instead of a traditional password. They provide their email address and create a passkey credential on their device (e.g., fingerprint, face recognition, hardware security key). After registration, a verification email is sent to the provided address. The user cannot authenticate until they verify their email.

**Why this priority**: This is the core happy path for the feature. Without passkey-based registration, the feature delivers no value. It also integrates with the existing email verification flow, making it the foundational journey.

**Independent Test**: Can be fully tested by initiating passkey registration with an email, completing the passkey ceremony on the device, confirming the account is created, verifying the email via the existing verification flow, and then authenticating with the passkey.

**Acceptance Scenarios**:

1. **Given** a visitor on the registration page, **When** they choose passkey registration and provide a valid email address, **Then** the system initiates the passkey creation ceremony by returning registration options to the client.
2. **Given** the system has returned registration options, **When** the visitor completes the passkey creation ceremony on their device, **Then** the system creates a user account linked to the provided email and stores the passkey credential.
3. **Given** a user account has been created via passkey registration, **When** account creation completes, **Then** a verification email is sent to the provided email address following the existing email verification flow.
4. **Given** a user registered via passkey whose email is not yet verified, **When** they attempt to authenticate with their passkey, **Then** the system denies authentication and indicates that email verification is required.
5. **Given** a user registered via passkey, **When** they verify their email using the verification link, **Then** their email is marked as verified and they can now authenticate using their passkey.

---

### User Story 2 - Verified User Authenticates with Passkey (Priority: P1)

A user who has registered via passkey and completed email verification returns to the application and authenticates using their passkey. The passkey is a discoverable credential (resident key), so the user does not need to enter their email — the credential identifies them automatically. The system validates the passkey credential and grants access.

**Why this priority**: Authentication is equally critical to registration — without it, the passkey registration has no practical use. Users must be able to prove their identity using the credential they created.

**Independent Test**: Can be fully tested by having a registered and email-verified user initiate passkey authentication without entering an email, completing the assertion ceremony on their device, and confirming the system grants access and returns valid session tokens.

**Acceptance Scenarios**:

1. **Given** a registered and email-verified user, **When** they initiate passkey authentication, **Then** the system returns authentication challenge options with an empty `allowCredentials` list (enabling the authenticator to present discoverable credentials).
2. **Given** the system has returned authentication challenge options, **When** the user selects and completes the passkey assertion ceremony on their device, **Then** the system identifies the user from the credential, validates the signature, and grants access by returning authentication tokens.
3. **Given** a user with a valid passkey, **When** the assertion response contains an invalid or tampered credential, **Then** the system rejects the authentication attempt with an appropriate error.

---

### User Story 3 - Existing User Adds a Passkey to Their Account (Priority: P2)

A user who previously registered with email and password (and has already verified their email) wants to add a passkey as an alternative authentication method. They navigate to their account settings, initiate the passkey setup, and complete the credential creation ceremony on their device.

**Why this priority**: Supporting passkey addition for existing accounts ensures the feature is not limited to new registrations. This bridges the gap between the existing user base and the new authentication method, driving adoption.

**Independent Test**: Can be fully tested by logging in with an existing email/password account, initiating passkey addition, completing the ceremony, and then authenticating with the newly added passkey.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a verified email, **When** they request to add a passkey, **Then** the system initiates the passkey creation ceremony by returning registration options tied to their existing account.
2. **Given** the system has returned passkey registration options, **When** the user completes the passkey creation ceremony on their device, **Then** the passkey credential is stored and linked to their account.
3. **Given** an authenticated user has added a passkey, **When** they log out and attempt to log back in using the passkey, **Then** the system authenticates them successfully.
4. **Given** an authenticated user whose email is not verified, **When** they attempt to add a passkey, **Then** the system rejects the request and indicates that email verification is required first.

---

### User Story 4 - User Manages Multiple Passkeys (Priority: P3)

A user who has one or more passkeys registered wants to view their registered passkeys and remove one they no longer use (e.g., an old device). They can see a list of their passkeys and remove individual credentials.

**Why this priority**: Passkey management is important for long-term usability and security hygiene but is not required for the core registration and authentication flows to function.

**Independent Test**: Can be fully tested by adding multiple passkeys to an account, listing them, removing one, and confirming the removed passkey no longer works for authentication while others still do.

**Acceptance Scenarios**:

1. **Given** an authenticated user with one or more passkeys, **When** they request to view their passkeys, **Then** the system returns a list of their registered passkeys with identifying information (e.g., device name, creation date).
2. **Given** an authenticated user viewing their passkeys, **When** they remove a specific passkey, **Then** the credential is deleted and can no longer be used for authentication.
3. **Given** an authenticated user with only one passkey and no password, **When** they attempt to remove their last passkey, **Then** the system prevents the removal and informs the user they must retain at least one authentication method.
4. **Given** an authenticated user who already has 5 registered passkeys, **When** they attempt to add another passkey, **Then** the system rejects the request and informs the user they have reached the maximum number of passkeys.

---

### Edge Cases

- What happens when a user registers with a passkey using an email address already associated with a verified account? → The system rejects the registration and informs the user the email is already in use.
- What happens when a user registers with a passkey using an email address associated with an unverified account? → The system supersedes the previous unverified account (consistent with existing email verification behaviour), replacing the user record and dispatching a fresh verification email.
- What happens if the passkey ceremony times out or is cancelled by the user? → The registration or addition is not completed; no account or credential is created. The user can retry.
- What happens if a user's device no longer supports the stored passkey (e.g., device reset)? → The user must use an alternative authentication method (password if available). If the user registered exclusively via passkey and has no password, they cannot authenticate — account recovery for passkey-only users is explicitly out of scope for this feature and will be addressed in a dedicated recovery feature.
- What happens when the same passkey credential is presented for two different accounts? → The system rejects authentication with an error; each passkey credential must be uniquely associated with one account.
- What happens if the passkey signature counter is lower than the stored counter (indicating potential credential cloning)? → The system rejects the authentication attempt and immediately disables the affected credential. The user must remove the disabled credential and re-add a new passkey to restore access via that device.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a registration flow that allows a new user to create an account by providing an email address and completing a passkey creation ceremony (WebAuthn registration).
- **FR-002**: During passkey registration, the system MUST generate and return WebAuthn registration options (challenge, relying party information, user information) to the client to initiate the credential creation ceremony. The options MUST request a discoverable credential (resident key) so the credential can identify the user at authentication time.
- **FR-003**: Upon successful completion of the passkey creation ceremony, the system MUST create a user account linked to the provided email and store the passkey credential (credential ID, public key, sign count) associated with that account.
- **FR-004**: After passkey-based account creation, the system MUST trigger the existing email verification flow, sending a verification email to the provided address with a valid token.
- **FR-005**: The system MUST deny authentication via passkey for any user whose email address has not been verified, returning a response that clearly indicates email verification is required.
- **FR-006**: The system MUST provide an authentication flow that allows a user with a verified email to authenticate using their passkey by completing a WebAuthn assertion ceremony.
- **FR-007**: During passkey authentication, the system MUST generate and return WebAuthn authentication options (challenge, empty `allowCredentials` list) to the client, enabling discoverable credential selection on the authenticator without requiring the user to provide an email address.
- **FR-008**: Upon successful completion of the passkey assertion ceremony, the system MUST validate the credential signature, verify the sign count, and return authentication tokens (consistent with the existing token-based authentication).
- **FR-009**: The system MUST allow an authenticated user with a verified email to add a passkey credential to their existing account by completing a passkey creation ceremony.
- **FR-010**: The system MUST reject passkey addition requests from users whose email is not verified.
- **FR-011**: The system MUST allow an authenticated user to view a list of their registered passkeys, including identifying metadata (device name or label, creation date).
- **FR-012**: The system MUST allow an authenticated user to remove a specific passkey credential from their account.
- **FR-013**: The system MUST prevent a user from removing their last passkey if they have no other authentication method (e.g., no password set), ensuring at least one authentication method is always available.
- **FR-014**: The system MUST reject passkey registration if the provided email address already belongs to a verified account.
- **FR-015**: If a passkey registration is attempted with an email address belonging to an unverified account, the system MUST supersede the previous unverified account, replacing its credentials and dispatching a new verification email.
- **FR-016**: The system MUST validate the WebAuthn sign count during authentication and reject attempts where the presented sign count is not greater than the stored value, to detect potential credential cloning. Upon detection, the system MUST immediately disable the affected credential, preventing any further authentication attempts with it until the user explicitly removes and re-adds a passkey.
- **FR-017**: A user MUST be able to authenticate using either their password or their passkey, provided their email is verified. Both methods coexist independently.
- **FR-018**: The system MUST enforce a maximum of 5 passkey credentials per user account. Attempts to add a passkey beyond this limit MUST be rejected with an appropriate error.
- **FR-019**: WebAuthn challenges generated for both registration and authentication ceremonies MUST expire after 5 minutes. Responses submitted against an expired challenge MUST be rejected. The challenge expiry duration MUST be configurable via an app-level setting.

### Key Entities

- **Passkey Credential**: Represents a WebAuthn credential registered by a user. Key attributes: credential ID, public key, sign count, device label, creation timestamp, enabled/disabled status. Associated with exactly one user account. A user may have up to 5 passkey credentials. A credential may be disabled (e.g., due to cloning detection) and cannot be used for authentication until removed and re-added.
- **User Account**: Extended from the existing user model to support passkey-based authentication alongside email/password. A user may have zero or more passkey credentials and may authenticate via password, passkey, or both.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete passkey registration (including email verification) within 3 minutes.
- **SC-002**: Users can authenticate with a passkey in under 10 seconds after initiating the flow.
- **SC-003**: Existing users with verified emails can add a passkey to their account in under 1 minute.
- **SC-004**: 95% of passkey authentication attempts by verified users succeed on the first try.
- **SC-005**: No user can authenticate via passkey without a verified email address.
- **SC-006**: Users who have both password and passkey credentials can independently use either method to authenticate.
- **SC-007**: Users can manage (view and remove) their registered passkeys without assistance.

## Assumptions

- The client (browser or native app) supports the Web Authentication API (WebAuthn). The system does not need to provide a fallback for clients that lack WebAuthn support — clients without support will continue to use the existing email/password flow.
- The relying party ID and origin are derived from the application's configured domain, consistent with WebAuthn specifications.
- Passkey credentials use the "platform" or "cross-platform" authenticator attachment; the system does not restrict authenticator type.
- The existing email verification flow (feature 003) is fully implemented and operational before this feature is deployed.
- The existing JWT-based authentication token system is used for passkey authentication responses — the system returns the same token format regardless of whether the user authenticated via password or passkey.
- Device labels for passkeys are optionally provided by the user at creation time; if not provided, a default label is generated from the credential metadata.
- WebAuthn challenges expire after 5 minutes by default; this is configurable.
- Account recovery for passkey-only users who lose access to all their devices is explicitly out of scope for this feature. It will be addressed in a separate, dedicated account recovery feature.
