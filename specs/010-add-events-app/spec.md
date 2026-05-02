# Feature Specification: Events App

**Feature Branch**: `010-add-events-app`  
**Created**: 2026-04-27  
**Status**: Draft  
**Input**: User description: "Create a Django events app. The app should allow an event to be created by a regular user or an Organisation; events created by organisations can only be created by a user that can manage the Organisation, i.e. the owner. The event must have the following attributes: Title, Description max 1000 characters, Start datetime, End datetime, Event category (default to other), Location including physical address or web address, Cover image (optional), Tickets link (optional). Changes made to the title, start time, end time, and location of the event must be kept for audit purposes. The physical address must have a Country, State, city/town, and postcode/zipcode."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a Personal Event (Priority: P1)

As a registered user, I want to create an event in my own name so that I can publish plans,
gatherings, or announcements without needing an organization profile.

**Why this priority**: The feature has no value until an individual user can create a valid event
record with the required schedule and location details.

**Independent Test**: Can be fully tested by having a registered user submit a valid personal event
with required fields and verifying it is saved under that user with the correct defaults and
optional-field behavior.

**Acceptance Scenarios**:

1. **Given** a registered user is creating an event for themselves, **When** they submit a title,
   description, start date and time, end date and time, and a valid location, **Then** a new
   personal event is created under their account.
2. **Given** a registered user omits the event category while creating a valid event, **When** the
   event is saved, **Then** the event category is set to `Other` automatically.
3. **Given** a registered user provides a web address as the event location, **When** the event is
   saved, **Then** creation succeeds without requiring physical address details.

---

### User Story 2 - Create an Organization Event (Priority: P2)

As an organization owner, I want to create an event on behalf of one of my organizations so that
the event is represented as an organization-led activity rather than a personal one.

**Why this priority**: Organization-led publishing is a core business rule of the feature and must
respect the existing ownership model before broader event management is useful.

**Independent Test**: Can be fully tested by having an organization owner create an event for an
owned organization and verifying the event is linked to that organization, while a non-owner is
blocked from doing the same.

**Acceptance Scenarios**:

1. **Given** a registered user owns an organization, **When** they choose that organization while
   creating a valid event, **Then** the event is created on behalf of that organization.
2. **Given** a registered user does not own a selected organization, **When** they attempt to
   create an event for that organization, **Then** the system prevents creation.
3. **Given** an organization owner creates an event without a cover image or tickets link,
   **When** the event is saved, **Then** creation succeeds and the event remains valid without
   those optional fields.

---

### User Story 3 - Maintain Event Details with Audit History (Priority: P3)

As an authorized event organizer, I want to update event details while preserving a history of key
changes so that event information stays accurate without losing accountability.

**Why this priority**: Event details often change after publication, and the specified audit
requirements are necessary to preserve trust and traceability for the most important public-facing
fields.

**Independent Test**: Can be fully tested by updating an owned event’s title, start time, end
time, or location and verifying the current event reflects the new value while the previous value,
editor, and change time remain preserved.

**Acceptance Scenarios**:

1. **Given** an authorized organizer edits an owned event’s title, start time, end time, or
   location, **When** the update succeeds, **Then** the event shows the latest value and the prior
   value is retained in the audit history.
2. **Given** an authorized organizer changes an event location from a web address to a physical
   address or from a physical address to a web address, **When** the update succeeds, **Then** the
   event keeps the new location format and the previous location state remains captured for audit
   purposes.
3. **Given** a user without write permission attempts to update an event, **When** they submit a
   change, **Then** the system prevents the update and no event data is modified.

### Edge Cases

- What happens when the end date and time is the same as or earlier than the start date and time?
- How does the system handle a description that exceeds the 1000-character limit?
- What happens when a physical-location event is submitted without one of the required address
  components: country, state, city/town, or postcode/zipcode?
- How does the system handle an event location being changed from a web address to a physical
  address, or the reverse, after the event has already been created?
- What happens when an organization owner loses ownership access after previously creating an
  organization event?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow a registered user to create an event in their own name.
- **FR-002**: System MUST allow an organization owner to create an event on behalf of an
  organization they own.
- **FR-003**: System MUST prevent users from creating an organization event for any organization
  they do not currently own.
- **FR-004**: System MUST associate each event with exactly one organizer context: either a single
  registered user or a single organization.
- **FR-005**: System MUST allow only the personal event creator to update a personal event.
- **FR-006**: System MUST allow only the current owner of an organization to update an
  organization-owned event.
- **FR-007**: System MUST require each event to include a title.
- **FR-008**: System MUST require each event to include a description no longer than 1000
  characters.
- **FR-009**: System MUST require each event to include a start date and time and an end date and
  time.
- **FR-010**: System MUST reject any event whose end date and time is not later than its start
  date and time.
- **FR-011**: System MUST assign each event a category from a predefined event-category list and
  MUST default the category to `Other` when no category is selected.
- **FR-012**: System MUST require each event to have exactly one location representation: either a
  physical address or a web address.
- **FR-013**: System MUST require a physical event location to include country, state, city/town,
  and postcode/zipcode.
- **FR-014**: System MUST allow an event to use a web address as its location without requiring
  physical address details.
- **FR-015**: System MUST allow an event to include an optional cover image.
- **FR-016**: System MUST allow an event to include an optional tickets link.
- **FR-017**: System MUST allow an authorized organizer to update event details after creation.
- **FR-018**: System MUST retain an immutable audit history for every change made to an event’s
  title, start date and time, end date and time, and location.
- **FR-019**: System MUST record, for each audited change, which field changed, the previous value,
  the new value, who made the change, and when the change occurred.
- **FR-020**: System MUST retain audit history when an event’s location changes between a web
  address and a physical address.
- **FR-021**: System MUST retain audited change records for the lifetime of the event record.
- **FR-022**: System MUST retain creation and last-updated timestamps for each event.
- **FR-023**: System MUST allow events to remain valid when the optional cover image and optional
  tickets link are absent.

### API Contract & Versioning *(mandatory when APIs are added or changed)*

- **API-001**: Event creation and event maintenance capabilities MUST be published as part of the
  project’s OpenAPI 3.0+ documentation.
- **API-002**: Any event endpoints introduced by this feature MUST be exposed under the active
  versioned API namespace at `/api/v1/`.
- **API-003**: The documented contract MUST distinguish personal events from organization-owned
  events and MUST define the ownership rules that govern who can create or update each kind.
- **API-004**: The documented contract MUST define required event fields, optional fields, default
  category behavior, and validation rules for schedule ordering and location input.
- **API-005**: The documented contract MUST define error outcomes for unauthorized organization
  selection, unauthorized event updates, invalid schedule data, and invalid physical address input.
- **API-006**: The documented contract MUST state that audited changes to title, start time, end
  time, and location are retained even when that history is not part of the standard public event
  payload.
- **API-007**: No existing API version or endpoint is deprecated by this feature.

### Key Entities *(include if feature involves data)*

- **Event**: A scheduled activity owned either by an individual user or an organization; includes
  title, description, category, schedule, location, optional cover image, optional tickets link,
  and lifecycle timestamps.
- **Event Organizer**: The accountable owner of the event, represented either by the registered
  user who created a personal event or by the organization on whose behalf the event is created.
- **Event Location**: The event venue information, represented either as a physical address with
  country, state, city/town, and postcode/zipcode, or as a web address for online attendance.
- **Event Change Record**: An immutable audit entry that preserves the previous and new values for
  changes to title, schedule, and location, along with who made the change and when it occurred.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of successfully created personal events are linked to the creating user, and
  100% of successfully created organization events are linked to the selected owned organization.
- **SC-002**: 100% of event submissions with an end date and time that is not later than the start
  date and time are rejected with clear feedback before publication.
- **SC-003**: 100% of physical-location event submissions missing country, state, city/town, or
  postcode/zipcode are rejected with clear feedback.
- **SC-004**: 100% of organization-event creation or update attempts by non-owners are blocked.
- **SC-005**: 100% of successful changes to title, start time, end time, or location produce an
  audit record containing the previous value, new value, change actor, and change timestamp.
- **SC-006**: 95% of valid event creation attempts are completed by an organizer in under 3
  minutes.
- **SC-007**: 100% of valid event submissions that omit category are saved with the category set to
  `Other`.
- **SC-008**: 100% of valid event submissions without a cover image or tickets link are accepted
  without requiring those fields.

## Assumptions

- Event creation and event updates in this feature are limited to registered users acting either on
  their own behalf or as the single owner of an organization; delegated managers and shared
  ownership are out of scope.
- Each event has one location mode at a time: one physical address or one web address, not both
  simultaneously.
- Audit retention in this feature is for accountability and traceability; a dedicated end-user
  interface for browsing audit history is out of scope unless defined separately.
- Event deletion, cancellation workflows, recurrence, attendee registration, capacity limits, and
  payment or ticket inventory management are out of scope for this initial release.
- The initial event-category list will be defined during planning and delivery, but it must include
  `Other` and support automatic defaulting when no category is chosen.
