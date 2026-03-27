# Tasks: Custom User & Profile Management

**Input**: Design documents from `/specs/001-user-profile-apps/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Not explicitly requested in the feature specification. Test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md structure:
- `users/` - Custom user app
- `profiles/` - Profile app
- `afrourban/` - Project settings and core

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [x] T001 Add dependencies to pyproject.toml: djangorestframework, djangorestframework-simplejwt, Pillow
- [x] T002 [P] Add dev dependencies to pyproject.toml: factory-boy, pytest-django
- [x] T003 Create users Django app via `poetry run python manage.py startapp users`
- [x] T004 Create profiles Django app via `poetry run python manage.py startapp profiles`
- [x] T005 [P] Configure INSTALLED_APPS in afrourban/settings/base.py (add rest_framework, rest_framework_simplejwt, rest_framework_simplejwt.token_blacklist, users, profiles)
- [x] T006 [P] Configure REST_FRAMEWORK settings in afrourban/settings/base.py (JWT auth, default permissions)
- [x] T007 [P] Configure SIMPLE_JWT settings in afrourban/settings/base.py (30min access, 1 day refresh, rotation, blacklist)
- [x] T008 [P] Configure AUTH_PASSWORD_VALIDATORS in afrourban/settings/base.py (8+ chars, common, numeric, similarity)
- [x] T009 Set AUTH_USER_MODEL = 'users.CustomUser' in afrourban/settings/base.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 Create CustomUserManager in users/managers.py (create_user, create_superuser methods)
- [x] T011 Create CustomUser model in users/models.py (email-based auth, AbstractBaseUser, PermissionsMixin)
- [x] T012 Create RFC 9457 Problem Details exception handler in afrourban/exceptions.py
- [x] T013 Register users app in users/apps.py with proper config
- [x] T014 Register profiles app in profiles/apps.py with proper config
- [x] T015 Create and apply initial migrations: `poetry run python manage.py makemigrations users profiles`
- [x] T016 Apply migrations: `poetry run python manage.py migrate`
- [x] T017 Add users and profiles URL includes to afrourban/urls.py (/api/auth/, /api/profiles/, /api/admin/users/)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - New User Registration (Priority: P1) 🎯 MVP

**Goal**: Allow visitors to create accounts with email/password and auto-create profiles

**Independent Test**: Create a new account with valid information, verify user and profile are created, verify user can authenticate

### Implementation for User Story 1

- [x] T018 [P] [US1] Create user input serializer (RegisterInputSerializer) in users/serializers.py (email, password, password_confirm, display_name)
- [x] T019 [P] [US1] Create user output serializer (UserOutputSerializer) in users/serializers.py
- [x] T020 [US1] Create user_create service in users/services.py (validate, create user, create profile, return user)
- [x] T021 [US1] Create UserFactory in users/tests/factories.py
- [x] T022 [US1] Create RegisterView (POST /api/auth/register/) in users/views.py
- [x] T023 [US1] Add registration URL route in users/urls.py
- [x] T024 [US1] Create Profile model in profiles/models.py (OneToOne to CustomUser, display_name, bio, avatar, phone_number, date_of_birth, preferences JSONField)
- [x] T025 [US1] Create ProfileFactory in profiles/tests/factories.py
- [x] T026 [US1] Create initial migration for Profile model

**Checkpoint**: User Story 1 complete - visitors can register and profiles are auto-created

---

## Phase 4: User Story 2 - User Authentication (Priority: P1)

**Goal**: Enable registered users to login/logout with JWT tokens containing policy claims

**Independent Test**: Login with valid credentials, receive JWT tokens, verify token contains user info and policies, logout and verify token is blacklisted

### Implementation for User Story 2

- [x] T027 [P] [US2] Create JWT claims builder in users/claims.py (get_user_policies, build_token_claims)
- [x] T028 [US2] Create CustomTokenObtainPairSerializer in users/serializers.py (add user, policies to response, embed claims in token)
- [x] T029 [US2] Create user_by_email selector in users/selectors.py
- [x] T030 [US2] Create user_with_permissions selector in users/selectors.py
- [x] T031 [US2] Create TokenObtainPairView override in users/views.py (POST /api/auth/token/)
- [x] T032 [US2] Create TokenRefreshView route in users/views.py (POST /api/auth/token/refresh/)
- [x] T033 [US2] Create TokenVerifyView route in users/views.py (POST /api/auth/token/verify/)
- [x] T034 [US2] Create LogoutView in users/views.py (POST /api/auth/logout/ - blacklist refresh token)
- [x] T035 [US2] Add authentication URL routes in users/urls.py (token, token/refresh, token/verify, logout)

**Checkpoint**: User Story 2 complete - users can login, receive JWTs with policies, refresh tokens, and logout

---

## Phase 5: User Story 3 - Profile Management (Priority: P2)

**Goal**: Allow authenticated users to view and update their profile, including avatar upload

**Independent Test**: Login, view profile, update profile fields, upload avatar, verify changes persist

### Implementation for User Story 3

- [x] T036 [P] [US3] Create ProfileInputSerializer in profiles/serializers.py (display_name, bio, phone_number, date_of_birth, preferences)
- [x] T037 [P] [US3] Create ProfileOutputSerializer in profiles/serializers.py
- [x] T038 [P] [US3] Create AvatarUploadSerializer in profiles/serializers.py (file validation: JPEG/PNG/WebP, max 5MB)
- [x] T039 [US3] Create profile_get_by_user selector in profiles/selectors.py
- [x] T040 [US3] Create profile_update service in profiles/services.py
- [x] T041 [US3] Create avatar_upload service in profiles/services.py (validate, save, return URL)
- [x] T042 [US3] Create avatar_delete service in profiles/services.py
- [x] T043 [US3] Create ProfileMeView in profiles/views.py (GET/PATCH /api/profiles/me/)
- [x] T044 [US3] Create ProfileAvatarView in profiles/views.py (POST/DELETE /api/profiles/me/avatar/)
- [x] T045 [US3] Create ProfilePublicView in profiles/views.py (GET /api/profiles/{user_id}/)
- [x] T046 [US3] Add profile URL routes in profiles/urls.py (me, me/avatar, {user_id})

**Checkpoint**: User Story 3 complete - users can manage their profiles and avatars

---

## Phase 6: User Story 4 - Permission-Based Access Control (Priority: P2)

**Goal**: Allow administrators to manage user permissions and enforce permission checks on protected actions

**Independent Test**: Create users with different permissions, verify authorized actions succeed, verify unauthorized actions return 403

### Implementation for User Story 4

- [x] T047 [P] [US4] Create HasPermission DRF permission class in users/permissions.py (check token claims)
- [x] T048 [P] [US4] Create IsStaffUser DRF permission class in users/permissions.py
- [x] T049 [P] [US4] Create IsOwnerOrAdmin DRF permission class in users/permissions.py
- [x] T050 [US4] Create user_list selector in users/selectors.py (with pagination, filtering, search)
- [x] T051 [US4] Create user_get_by_id selector in users/selectors.py
- [x] T052 [US4] Create user_activate service in users/services.py
- [x] T053 [US4] Create user_deactivate service in users/services.py
- [x] T054 [US4] Create user_permissions_get selector in users/selectors.py
- [x] T055 [US4] Create user_permissions_set service in users/services.py
- [x] T056 [P] [US4] Create AdminUserListSerializer in users/serializers.py
- [x] T057 [P] [US4] Create AdminUserDetailSerializer in users/serializers.py
- [x] T058 [US4] Create AdminUserListView in users/views.py (GET /api/admin/users/)
- [x] T059 [US4] Create AdminUserDetailView in users/views.py (GET/PATCH /api/admin/users/{user_id}/)
- [x] T060 [US4] Create AdminUserActivateView in users/views.py (POST /api/admin/users/{user_id}/activate/)
- [x] T061 [US4] Create AdminUserDeactivateView in users/views.py (POST /api/admin/users/{user_id}/deactivate/)
- [x] T062 [US4] Create AdminUserPermissionsView in users/views.py (GET/PUT /api/admin/users/{user_id}/permissions/)
- [x] T063 [US4] Add admin user URL routes in users/urls.py

**Checkpoint**: User Story 4 complete - administrators can manage users and permissions are enforced

---

## Phase 7: User Story 5 - Role and Policy Management (Priority: P3)

**Goal**: Allow administrators to define roles (groups) that bundle permissions and policies with conditions

**Independent Test**: Create role with permissions, assign to user, verify user inherits role permissions, create policy with conditions, verify policy restrictions apply

### Implementation for User Story 5

- [X] T064 [P] [US5] Create Policy model in profiles/models.py (name, description, conditions JSONField, is_active)
- [X] T065 [P] [US5] Create GroupPolicy through model in profiles/models.py (links Group to Policy)
- [X] T066 [US5] Create migration for Policy and GroupPolicy models
- [X] T067 [P] [US5] Create RoleSerializer in users/serializers.py (for Django Group)
- [X] T068 [P] [US5] Create PolicySerializer in profiles/serializers.py
- [X] T069 [US5] Create role_list selector in users/selectors.py
- [X] T070 [US5] Create role_get_by_id selector in users/selectors.py
- [X] T071 [US5] Create role_create service in users/services.py (create Group with permissions)
- [X] T072 [US5] Create role_update service in users/services.py
- [X] T073 [US5] Create role_delete service in users/services.py
- [X] T074 [US5] Create policy_evaluate service in profiles/services.py (check conditions: time_window, ip_whitelist, etc.)
- [X] T075 [US5] Update users/claims.py to include active policies in JWT tokens
- [X] T076 [US5] Create AdminRoleListView in users/views.py (GET/POST /api/admin/users/roles/)
- [X] T077 [US5] Create AdminRoleDetailView in users/views.py (GET/PATCH/DELETE /api/admin/users/roles/{role_id}/)
- [X] T078 [US5] Add role management URL routes in users/urls.py

**Checkpoint**: User Story 5 complete - administrators can manage roles, policies, and users inherit role permissions

---

## Phase 8: User Story 6 - Password Management (Priority: P3)

**Goal**: Allow users to reset forgotten passwords and change passwords when authenticated

**Independent Test**: Request password reset, receive mock email with reset link, reset password with valid token, login with new password, change password when authenticated

### Implementation for User Story 6

- [X] T079 [P] [US6] Create PasswordResetRequestSerializer in users/serializers.py (email)
- [X] T080 [P] [US6] Create PasswordResetConfirmSerializer in users/serializers.py (token, uid, new_password, new_password_confirm)
- [X] T081 [P] [US6] Create PasswordChangeSerializer in users/serializers.py (current_password, new_password, new_password_confirm)
- [X] T082 [US6] Create password_reset_request service in users/services.py (generate token, queue email)
- [X] T083 [US6] Create password_reset_confirm service in users/services.py (validate token, set new password)
- [X] T084 [US6] Create password_change service in users/services.py (verify current, set new)
- [X] T085 [US6] Create PasswordResetRequestView in users/views.py (POST /api/auth/password/reset/)
- [X] T086 [US6] Create PasswordResetConfirmView in users/views.py (POST /api/auth/password/reset/confirm/)
- [X] T087 [US6] Create PasswordChangeView in users/views.py (POST /api/auth/password/change/)
- [X] T088 [US6] Add password management URL routes in users/urls.py

**Checkpoint**: User Story 6 complete - users can reset and change passwords

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T089 [P] Register CustomUser admin in users/admin.py
- [X] T090 [P] Register Profile admin in profiles/admin.py
- [X] T091 [P] Register Policy admin in profiles/admin.py
- [X] T092 Add structlog JSON logging configuration in afrourban/settings/base.py
- [X] T093 Add audit logging for auth events (login, logout, password changes) in users/services.py
- [X] T094 Run quickstart.md validation (verify all curl commands work)
- [ ] T095 Create test superuser via `poetry run python manage.py createsuperuser`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 and can be implemented in sequence or parallel
  - US3 and US4 are both P2 and can be implemented after US1+US2
  - US5 and US6 are both P3 and can be implemented after US3+US4
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - Creates Profile model needed by US3
- **User Story 2 (P1)**: Can start after Foundational - Can run parallel to US1
- **User Story 3 (P2)**: Depends on US1 (Profile model) - Independent otherwise
- **User Story 4 (P2)**: Can start after Foundational - Depends on US2 for permission classes
- **User Story 5 (P3)**: Depends on US4 (permission infrastructure)
- **User Story 6 (P3)**: Can start after US2 (authentication) - Independent otherwise

### Within Each User Story

- Models/Serializers before services (when applicable)
- Services before views
- Views before URL routes
- Core implementation before integration

### Parallel Opportunities

- Setup tasks T001-T009: T002, T005-T008 can run in parallel
- Foundational: T010 must complete before T011
- US1: T018-T019 can run in parallel, T024-T025 can run in parallel
- US2: T027 can start immediately
- US3: T036-T038 can run in parallel
- US4: T047-T049 can run in parallel, T056-T057 can run in parallel
- US5: T064-T065 can run in parallel, T067-T068 can run in parallel
- US6: T079-T081 can run in parallel
- Polish: T089-T091 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch serializers for User Story 1 together:
Task: "T018 [P] [US1] Create user input serializer in users/serializers.py"
Task: "T019 [P] [US1] Create user output serializer in users/serializers.py"

# After serializers, launch model and factory together:
Task: "T024 [US1] Create Profile model in profiles/models.py"
Task: "T021 [US1] Create UserFactory in users/tests/factories.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Registration)
4. Complete Phase 4: User Story 2 (Authentication)
5. **STOP and VALIDATE**: Test registration + authentication flow
6. Deploy/demo if ready - Users can register and login

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Registration) + US2 (Authentication) → MVP! Users can register and login
3. Add US3 (Profile Management) → Users can manage profiles
4. Add US4 (Permissions) → Admin can manage user access
5. Add US5 (Roles/Policies) → Scalable permission management
6. Add US6 (Password Management) → Full password recovery flow
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers after Foundational phase:

- Developer A: User Story 1 + User Story 3 (user-facing registration/profile)
- Developer B: User Story 2 + User Story 4 (auth + admin)
- Developer C: User Story 5 + User Story 6 (once dependencies ready)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- HackSoftware Django Styleguide: services for writes, selectors for reads
- Profile auto-creation happens in user_create service (US1), not via signals
- JWT token includes policies embedded as private claims (research.md decision)
- RFC 9457 Problem Details format for all API errors (constitution compliance)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
