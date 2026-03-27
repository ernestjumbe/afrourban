# Feature Specification: Age Verification Field

**Feature Branch**: `002-age-verification-field`  
**Created**: 27 March 2026  
**Status**: Draft  
**Input**: User description: "Include a field for future age verification"
**Depends on**: Feature 001 (Custom User & Profile Management)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Provides Date of Birth (Priority: P1)

As a registered user, I want to provide my date of birth so that the system can verify my age for age-restricted features in the future.

**Why this priority**: Date of birth collection is the foundation for any age verification. Without this data, no verification is possible.

**Independent Test**: Can be fully tested by logging in, navigating to profile, entering a date of birth, and verifying it is saved and displayed correctly.

**Acceptance Scenarios**:

1. **Given** an authenticated user on their profile page, **When** they enter a valid date of birth, **Then** the date is saved and displayed in their profile.
2. **Given** an authenticated user, **When** they enter a date of birth in the future, **Then** they receive a validation error.
3. **Given** an authenticated user, **When** they enter a date of birth more than 120 years ago, **Then** they receive a validation error.
4. **Given** an authenticated user with a saved date of birth, **When** they view their profile, **Then** they see their age calculated from the date of birth.

---

### User Story 2 - Age Verification Status Tracking (Priority: P2)

As a system administrator, I want to track the age verification status of users so that I can enforce age restrictions on certain features when needed.

**Why this priority**: Tracking verification status enables future age-gating without requiring users to re-enter information.

**Independent Test**: Can be fully tested by creating users with different verification statuses and confirming the status is correctly stored and queryable.

**Acceptance Scenarios**:

1. **Given** a new user profile, **When** the profile is created, **Then** the age verification status defaults to "unverified".
2. **Given** a user who has provided date of birth, **When** the system records this, **Then** the verification status changes to "self_declared".
3. **Given** an administrator viewing user details, **When** they check age verification status, **Then** they see the current status and when it was last updated.

---

### User Story 3 - Minimum Age Policy Enforcement (Priority: P3)

As a system administrator, I want to define minimum age requirements for specific features so that age-restricted content or actions are protected.

**Why this priority**: Policy enforcement is the end-goal of age verification, but requires the foundation from P1 and P2 first.

**Independent Test**: Can be fully tested by creating a policy with minimum age requirement and verifying users below that age are denied access.

**Acceptance Scenarios**:

1. **Given** a policy with a minimum age of 18, **When** a 17-year-old user attempts to access a protected feature, **Then** they are denied with an appropriate message.
2. **Given** a policy with a minimum age of 18, **When** a user without date of birth attempts to access a protected feature, **Then** they are prompted to provide their date of birth first.
3. **Given** a policy with a minimum age of 18, **When** a 19-year-old user attempts to access a protected feature, **Then** they are granted access.

---

### Edge Cases

- User updates date of birth after previously passing age verification: Reset verification status to self_declared with updated timestamp; age-based permissions recalculate dynamically on next access check (user may lose access if new age is below threshold).
- User's birthday occurs (age changes): Age-based permissions should reflect current age dynamically.
- User provides date of birth that makes them exactly the minimum age today: Should pass verification (≥ minimum age).
- Date of birth field with invalid format: Validation should reject with clear error message.

## Requirements *(mandatory)*

### Functional Requirements

**Date of Birth Collection**
- **FR-001**: Profile MUST include an optional date_of_birth field (DateField, nullable)
- **FR-002**: System MUST validate date_of_birth is not in the future
- **FR-003**: System MUST validate date_of_birth is not more than 120 years in the past
- **FR-004**: System MUST calculate and expose user's current age based on date_of_birth

**Age Verification Status**
- **FR-005**: Profile MUST include an age_verification_status field with values: unverified, self_declared (active); pending, verified, failed (reserved for future document verification)
- **FR-006**: System MUST default age_verification_status to "unverified" for new profiles
- **FR-007**: System MUST update age_verification_status to "self_declared" when user provides date_of_birth
- **FR-008**: System MUST track the timestamp when age_verification_status was last updated
- **FR-008a**: State transitions pending → verified/failed are reserved for future document verification feature and NOT implemented in this scope
- **FR-008b**: When user updates date_of_birth, system MUST reset age_verification_status to self_declared and update timestamp

**Age Policy Integration**
- **FR-009**: Policy conditions MUST support a minimum_age constraint
- **FR-010**: System MUST deny access to age-restricted features when user's age is below minimum or unknown
- **FR-011**: System MUST include age verification data in JWT private claims when user has provided date_of_birth

**Privacy & Consent**
- **FR-012**: System MUST store date_of_birth securely as sensitive personal data
- **FR-013**: System MUST NOT expose exact date_of_birth in public API responses; only age or age_verified boolean

### Key Entities

- **Profile** (extended): Existing profile entity gains age_verification_status, age_verified_at fields. date_of_birth already exists from feature 001.
- **Policy** (extended): Existing policy conditions gain minimum_age support for age-gated access control.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can enter and save their date of birth in under 30 seconds
- **SC-002**: Age calculation is accurate to the day (handles leap years, timezone correctly)
- **SC-003**: Age verification status transitions correctly in 100% of test cases
- **SC-004**: Age-restricted policies deny underage users with zero false positives
- **SC-005**: Date of birth is not exposed in any public API response (privacy compliance)
- **SC-006**: Age data is available in JWT claims for stateless policy checks

## Assumptions

- Date of birth is self-declared; third-party verification (ID documents, services) is out of scope for this feature
- Feature 001 (Custom User & Profile Management) is implemented and provides the Profile model
- Age is calculated based on UTC date comparison
- "Verified" status (beyond self_declared) will be implemented in a future feature with document upload

## Clarifications

### Session 2026-03-27

- Q: What triggers the pending/verified/failed states in age_verification_status? → A: Reserved for future document verification; implement only unverified/self_declared now
- Q: What happens when user updates date of birth after passing age verification? → A: Reset status to self_declared with new timestamp; permissions recalculate dynamically
