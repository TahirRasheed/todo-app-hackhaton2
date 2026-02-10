# Implementation Tasks: Frontend Application — Todo Web Interface

**Feature**: 003-frontend-ui
**Date**: 2026-02-10
**Status**: Ready for Implementation
**Branch**: `003-frontend-ui`

---

## Overview

This document defines all implementation tasks for the Frontend Application feature. Tasks are organized by **user story** to enable independent, parallel development with clear, testable increments.

**Total Tasks**: 38
**Estimated Effort**: 18-25 hours (frontend 12-16h + testing 4-6h + refinement 2-3h)
**MVP Scope**: User Stories 1-4 (signup, signin, dashboard, create task) = ~12-14 hours

---

## Task Dependency Graph

```
Phase 1: Setup & Infrastructure
  └─ (no dependencies)

Phase 2: Foundational (Blocking)
  ├─ Project initialization (structure, dependencies)
  ├─ Authentication context & hooks
  ├─ API client wrapper with JWT attachment
  └─ Type definitions

Phase 3: User Story 1 (Signup - P1)
  ├─ depends on: Phase 2 (auth context, API client)
  └─ enables: US2, US3, US4 (blocks all others)

Phase 4: User Story 2 (Signin - P1)
  ├─ depends on: Phase 2 + US1
  └─ enables: US3, US4

Phase 5: User Story 3 (Dashboard - P1)
  ├─ depends on: Phase 2 + US2
  └─ enables: US4, US5, US6, US7

Phase 6: User Story 4 (Create Task - P1)
  ├─ depends on: Phase 2 + US3
  └─ enables: US5, US6

Phase 7: User Story 5 (Edit Task - P2)
  ├─ depends on: US4
  └─ independent (can parallel US6)

Phase 8: User Story 6 (Toggle Completion - P2)
  ├─ depends on: US3
  └─ independent (can parallel US5, US7)

Phase 9: User Story 7 (Delete Task - P2)
  ├─ depends on: US3
  └─ independent (can parallel US5, US6)

Phase 10: User Story 8 (Logout - P1)
  ├─ depends on: Phase 2
  └─ independent (can parallel US5, US6, US7)

Phase 11: User Story 9 (Error Handling - P1)
  ├─ depends on: US1, US2, US3, US4
  └─ cross-cutting (all error scenarios)

Phase 12: User Story 10 (Responsive Design - P1)
  ├─ depends on: All stories (final polish)
  └─ final validation

Phase 13: Polish & Testing
  ├─ Integration testing
  ├─ E2E testing
  └─ Performance validation
```

---

## Parallel Execution Opportunities

### During Setup (Phase 1-2)
All tasks are independent, can execute in parallel:
- [ ] Project structure initialization
- [ ] Install dependencies and configure tools
- [ ] Set up TypeScript, TailwindCSS, environment
- [ ] Create type definitions

### During Signup (Phase 3)
These can execute in parallel (different files):
- [ ] [P] Create SignupForm component
- [ ] [P] Implement signup validation utilities
- [ ] [P] Add signup page routing

### During Dashboard (Phase 5)
These can execute in parallel:
- [ ] [P] Create TaskList component
- [ ] [P] Create TaskCard component (dependencies: TaskList later)
- [ ] [P] Implement pagination logic
- [ ] [P] Add dashboard page and layout

### During Task Operations (Phases 6-9)
Edit, Complete, Delete can execute in parallel after Create:
- [ ] [P] Create TaskForm component (edit mode)
- [ ] [P] Implement task edit functionality
- [ ] [P] Implement task deletion with confirmation
- [ ] [P] Implement task completion toggle

---

## Phase 1: Project Setup & Infrastructure

### Goal
Initialize Next.js 16 project structure, install dependencies, configure tools, and establish foundational architecture.

### Independent Test Criteria
✓ Project compiles without errors
✓ Dev server runs on http://localhost:3000
✓ Environment variables configured
✓ TypeScript and ESLint pass without warnings
✓ TailwindCSS styles load in browser

---

## Phase 1 Tasks

- [ ] T001 Initialize Next.js 16 project with App Router in `frontend/` directory
- [ ] T002 [P] Install dependencies: React, TypeScript, TailwindCSS, React Hook Form
- [ ] T003 [P] Configure TypeScript: `frontend/tsconfig.json` strict mode enabled
- [ ] T004 [P] Configure TailwindCSS: `frontend/tailwind.config.js` with responsive breakpoints (sm=640, md=768, lg=1024, xl=1280)
- [ ] T005 [P] Configure Next.js: `frontend/next.config.js` with API proxy and security headers
- [ ] T006 Create environment variables: `frontend/.env.local` with NEXT_PUBLIC_API_URL=http://localhost:8000
- [ ] T007 Set up project structure: directories for pages, components, lib, hooks, types, styles
- [ ] T008 [P] Create ESLint and Prettier configuration files
- [ ] T009 Verify dev server starts: `npm run dev` runs without errors

---

## Phase 2: Foundational (Blocking Prerequisites)

### Goal
Implement JWT token management, authentication context, API client wrapper, and type definitions that block all user story work.

### Independent Test Criteria
✓ useAuth() hook returns auth state
✓ apiCall() wrapper attaches JWT token to requests
✓ Token persists in httpOnly cookie
✓ 401 response redirects to signin
✓ All TypeScript types compile without errors

---

## Phase 2 Tasks

### Authentication Context & Hooks

- [ ] T010 Create TypeScript types: `frontend/src/types/auth.ts` with User, AuthContext, AuthResponse interfaces
- [ ] T011 [P] Create TypeScript types: `frontend/src/types/task.ts` with Task, TaskListResponse, TaskCreateInput, TaskUpdateInput interfaces
- [ ] T012 [P] Create TypeScript types: `frontend/src/types/api.ts` with ApiResponse, ErrorResponse interfaces
- [ ] T013 Create auth context: `frontend/src/hooks/useAuth.ts` custom hook for auth state management
- [ ] T014 Create AuthProvider component: `frontend/src/components/auth/AuthProvider.tsx` wraps app with context
- [ ] T015 [P] Create auth utilities: `frontend/src/lib/auth.ts` helper functions (isAuthenticated, getToken, clearToken, setToken)

### API Client & Middleware

- [ ] T016 Create API wrapper: `frontend/src/lib/api.ts` with apiCall() function that:
  - Reads JWT from cookie
  - Attaches Authorization: Bearer <token> header
  - Handles 401 → redirect to signin
  - Handles 403 → show error "No permission"
  - Implements error handling for network failures
- [ ] T017 [P] Create type-safe API helpers: `frontend/src/lib/api.ts` extends with:
  - signup(email, password, name)
  - signin(email, password)
  - signout()
  - getTasks(userId, skip, limit)
  - createTask(userId, title, description)
  - updateTask(userId, taskId, updates)
  - deleteTask(userId, taskId)

### Form & Validation Utilities

- [ ] T018 Create form validation utilities: `frontend/src/lib/validation.ts` with:
  - validateEmail(email)
  - validatePassword(password)
  - validateTaskTitle(title)
  - Error messages for each field

- [ ] T019 [P] Create storage utilities: `frontend/src/lib/storage.ts` with:
  - Cookie read/write operations
  - HttpOnly cookie handling reference

---

## Phase 3: User Story 1 - User Signs Up (P1)

### Goal
Implement signup form, validation, and successful account creation with JWT token capture.

### Independent Test Criteria
✓ User navigates to /signup
✓ Form accepts email, password, name inputs
✓ Client-side validation prevents invalid submission
✓ Valid signup POST to backend succeeds
✓ User receives JWT token and redirected to dashboard
✓ Token persisted in httpOnly cookie

---

## Phase 3 Tasks

- [ ] T020 [US1] Create signup page: `frontend/src/pages/signup/page.tsx` with:
  - Title "Create Account"
  - Form with email, password, name, confirm-password fields
  - Link to signin page
  - Loading indicator during submission

- [ ] T021 [P] [US1] Create SignupForm component: `frontend/src/components/auth/SignupForm.tsx` with:
  - React Hook Form integration
  - Email validation (format check)
  - Password validation (8+ chars, uppercase, lowercase, number)
  - Name validation (non-empty)
  - Submit handler calls api.signup()
  - Error display for each field
  - Success redirect to /dashboard

- [ ] T022 [P] [US1] Create error handling for signup:
  - 409 Conflict (email exists) → show "Email already registered"
  - 400 Bad Request → show field-level errors
  - Network error → show "Unable to connect"
  - Success → set auth state, redirect

- [ ] T023 [US1] Add signup route to root layout: `frontend/src/pages/layout.tsx` includes SignupForm page
- [ ] T024 [US1] Add signup styling: `frontend/src/components/auth/SignupForm.tsx` responsive layout (mobile-first)

---

## Phase 4: User Story 2 - User Signs In (P1)

### Goal
Implement signin form, credential validation, and secure session establishment.

### Independent Test Criteria
✓ User navigates to /signin
✓ Form accepts email and password
✓ Valid credentials POST to backend succeeds
✓ User receives JWT token and redirected to dashboard
✓ Token persisted in httpOnly cookie
✓ Invalid credentials show generic error message

---

## Phase 4 Tasks

- [ ] T025 [US2] Create signin page: `frontend/src/pages/signin/page.tsx` with:
  - Title "Sign In"
  - Form with email and password fields
  - Link to signup page
  - Loading indicator during submission

- [ ] T026 [P] [US2] Create SigninForm component: `frontend/src/components/auth/SigninForm.tsx` with:
  - React Hook Form integration
  - Email and password validation
  - Submit handler calls api.signin()
  - Error display (generic "Invalid email or password" message)
  - Success redirect to /dashboard

- [ ] T027 [P] [US2] Create error handling for signin:
  - 401 Unauthorized → show "Invalid email or password" (generic)
  - Network error → show "Unable to connect"
  - Success → set auth state, redirect

- [ ] T028 [US2] Add signin route and default routing: `frontend/src/pages/page.tsx` (root) redirects:
  - If authenticated → /dashboard
  - If not authenticated → /signin

- [ ] T029 [US2] Add signin styling: responsive layout matching signup

---

## Phase 5: User Story 3 - View Dashboard with Tasks (P1)

### Goal
Implement protected dashboard page that displays authenticated user's personalized task list.

### Independent Test Criteria
✓ Unauthenticated users redirected to /signin
✓ Authenticated users see dashboard
✓ Task list fetches from backend with JWT token
✓ Loading indicator shown while fetching
✓ Empty state displayed when no tasks
✓ Pagination controls for large lists
✓ Responsive layout on mobile, tablet, desktop

---

## Phase 5 Tasks

### Dashboard Layout & Protection

- [ ] T030 [US3] Create protected dashboard page: `frontend/src/pages/dashboard/page.tsx` with:
  - Check authentication (redirect to /signin if not auth)
  - Display user greeting "Welcome, {name}!"
  - TaskList component (to be implemented)
  - Create Task button
  - Sign Out button in header
  - Responsive grid layout

- [ ] T031 [P] [US3] Create root layout with auth check: `frontend/src/pages/layout.tsx` with:
  - AuthProvider wrapper
  - Header component with navigation
  - Route protection middleware (redirect on 401)
  - Global error boundary

- [ ] T032 [P] [US3] Create Header component: `frontend/src/components/common/Header.tsx` with:
  - App logo/title
  - User name display
  - Sign Out button
  - Responsive menu for mobile

### Task List Components

- [ ] T033 [US3] Create TaskList component: `frontend/src/components/tasks/TaskList.tsx` with:
  - Fetch tasks on mount: getTasks(userId, 0, 20)
  - Display loading spinner while fetching
  - Show empty state if no tasks
  - Render TaskCard for each task
  - Pagination controls (Previous/Next, page indicator)
  - Handles 401 (redirect) and 403 (show error)

- [ ] T034 [P] [US3] Create TaskCard component: `frontend/src/components/tasks/TaskCard.tsx` with:
  - Display task title, description, completion status
  - Edit button
  - Delete button
  - Completion checkbox
  - Responsive card layout (works on mobile)

- [ ] T035 [P] [US3] Create pagination logic: `frontend/src/hooks/useTask.ts` custom hook with:
  - currentPage state
  - Total task count tracking
  - Previous/Next page handlers
  - Refetch on page change

- [ ] T036 [US3] Add responsive styling to dashboard: TailwindCSS responsive classes:
  - Mobile: single column, stacked layout
  - Tablet: two-column grid (768px+)
  - Desktop: three-column or card view (1024px+)

---

## Phase 6: User Story 4 - Create Task (P1)

### Goal
Implement task creation form and API integration with optimistic UI updates.

### Independent Test Criteria
✓ Create Task button opens modal/form
✓ Form accepts title and optional description
✓ Client-side validation prevents empty title
✓ Valid submission POSTs to backend with JWT
✓ Task appears in list immediately (optimistic)
✓ Error shows if API fails, optimistic update reverted
✓ Form closes on success

---

## Phase 6 Tasks

- [ ] T037 [US4] Create CreateTaskModal: `frontend/src/components/tasks/CreateTaskModal.tsx` with:
  - Title "Create New Task"
  - Input fields: title (required), description (optional)
  - Create and Cancel buttons
  - Modal overlay and close button

- [ ] T038 [P] [US4] Create TaskForm component: `frontend/src/components/tasks/TaskForm.tsx` with:
  - React Hook Form integration
  - Title validation (required, non-empty, max 255 chars)
  - Description validation (optional, max 1000 chars)
  - Submit handler:
    - Call createTask(userId, title, description)
    - Show loading indicator
    - On success: close modal, add task to list, show "Task created" message
    - On error: show "Failed to create task" error

- [ ] T039 [P] [US4] Add optimistic update logic to TaskList:
  - Add task to list immediately when form submits
  - Show pending state (dimmed or loading indicator)
  - If API fails: remove from list and show error
  - If API succeeds: update task with real data from response

- [ ] T040 [US4] Add Create Task button to dashboard:
  - Button in header or above task list
  - Click opens CreateTaskModal
  - Modal closes on cancel or success

- [ ] T041 [US4] Add styling to task form: responsive design for modal on mobile

---

## Phase 7: User Story 5 - Edit Task (P2)

### Goal
Implement task editing with form pre-population and API integration.

### Independent Test Criteria
✓ Edit button opens form with current task values
✓ User can modify title, description, completion
✓ Valid submission PUTs to backend with JWT
✓ Task updates in list immediately
✓ Error handling reverts changes if API fails

---

## Phase 7 Tasks

- [ ] T042 [US5] Create EditTaskModal: `frontend/src/components/tasks/EditTaskModal.tsx` with:
  - Title "Edit Task"
  - Pre-populated form with current task values
  - Update and Cancel buttons

- [ ] T043 [P] [US5] Extend TaskForm for edit mode:
  - Accept task as prop (for edit mode)
  - Pre-populate fields when editing
  - Submit handler calls updateTask() with task ID
  - Show success message on update
  - Show error if 403 Forbidden or 404 Not Found

- [ ] T044 [P] [US5] Add edit button handler to TaskCard:
  - Click edit → open EditTaskModal with task data
  - Modal closes on save or cancel
  - Updated task replaces old task in list

- [ ] T045 [US5] Add optimistic update logic for edit:
  - Update task in list immediately
  - Revert on error with error message

---

## Phase 8: User Story 6 - Toggle Task Completion (P2)

### Goal
Implement completion toggle with checkbox and real-time UI update.

### Independent Test Criteria
✓ Checkbox toggles completion status
✓ UI updates immediately (strikethrough or visual change)
✓ API request sent with new completion state
✓ Changes persist after page refresh

---

## Phase 8 Tasks

- [ ] T046 [US6] Add completion checkbox to TaskCard: `frontend/src/components/tasks/TaskCard.tsx`:
  - Checkbox element
  - onChange handler calls updateTask(taskId, { completed: !current })
  - Visual indicator of completion (strikethrough, opacity)

- [ ] T047 [P] [US6] Implement optimistic completion toggle:
  - Update UI immediately on checkbox change
  - Send updateTask API request
  - Revert if API fails with error toast

- [ ] T048 [P] [US6] Add completion styling: TailwindCSS classes for strikethrough, opacity when completed

---

## Phase 9: User Story 7 - Delete Task (P2)

### Goal
Implement task deletion with confirmation dialog and safe removal.

### Independent Test Criteria
✓ Delete button opens confirmation dialog
✓ Canceling dialog keeps task in list
✓ Confirming deletion POSTs DELETE to backend
✓ Task removed from list immediately
✓ Error shows if deletion fails

---

## Phase 9 Tasks

- [ ] T049 [US7] Add delete button to TaskCard: `frontend/src/components/tasks/TaskCard.tsx`
  - Delete icon/button
  - Click opens ConfirmDialog

- [ ] T050 [P] [US7] Create ConfirmDialog component: `frontend/src/components/ui/ConfirmDialog.tsx` with:
  - Message: "Are you sure? This cannot be undone"
  - Confirm and Cancel buttons
  - Modal overlay

- [ ] T051 [P] [US7] Implement delete handler in TaskCard:
  - Show ConfirmDialog on delete click
  - Call deleteTask(userId, taskId) on confirm
  - Remove task from list immediately (optimistic)
  - If error: add task back to list with error toast

---

## Phase 10: User Story 8 - Logout (P1)

### Goal
Implement logout that clears token and redirects to signin page.

### Independent Test Criteria
✓ Sign Out button visible in header
✓ Click Sign Out clears token
✓ User redirected to /signin
✓ Subsequent requests rejected with 401

---

## Phase 10 Tasks

- [ ] T052 [US8] Create LogoutButton component: `frontend/src/components/auth/LogoutButton.tsx` with:
  - Button in header
  - Click handler calls signout()
  - Clears auth state
  - Redirects to /signin

- [ ] T053 [P] [US8] Implement signout in useAuth hook:
  - Clear token from cookie
  - Clear user from context
  - Redirect to /signin page

---

## Phase 11: User Story 9 - Error Handling (P1)

### Goal
Implement graceful error handling across all operations.

### Independent Test Criteria
✓ 401 Unauthorized redirects to signin
✓ 403 Forbidden shows "No permission" error
✓ 404 Not Found shows "Not found" error
✓ Network errors show retry option
✓ Validation errors show field-level messages
✓ Generic error messages prevent user enumeration

---

## Phase 11 Tasks

- [ ] T054 [US9] Create ErrorAlert component: `frontend/src/components/ui/ErrorAlert.tsx` with:
  - Error message display
  - Dismiss button
  - Optional retry action
  - Responsive styling

- [ ] T055 [P] [US9] Implement error handling in API wrapper:
  - Catch and standardize error responses
  - Map HTTP status to user messages:
    - 400 → "Invalid input"
    - 401 → "Your session expired, please sign in again"
    - 403 → "You don't have permission"
    - 404 → "Not found"
    - 500 → "Server error, please try again"
  - Network errors: "Unable to connect, please check your internet"

- [ ] T056 [P] [US9] Add error state to dashboard components:
  - Show error alert for task list failures
  - Show error alert for create/edit/delete failures
  - Automatic dismissal or manual close

- [ ] T057 [US9] Test error scenarios:
  - Token expiration during action
  - Cross-user access attempt
  - Network timeout
  - Server 500 error

---

## Phase 12: User Story 10 - Responsive Design (P1)

### Goal
Validate and polish responsive design across all devices.

### Independent Test Criteria
✓ No horizontal scrolling on mobile (375px)
✓ All touch targets ≥ 48x48px
✓ Text readable at all breakpoints
✓ Navigation works on mobile/tablet/desktop
✓ Forms stack vertically on mobile
✓ Task cards adapt to screen width

---

## Phase 12 Tasks

- [ ] T058 [US10] Review TailwindCSS responsive classes:
  - Verify sm: (640px), md: (768px), lg: (1024px) breakpoints
  - Check button sizes (h-12 w-12 = 48px minimum)
  - Check input sizes (h-10+ minimum)
  - Check text sizes (base, lg, xl appropriate per screen)

- [ ] T059 [P] [US10] Test on mobile (375px width):
  - Dashboard layout single column, no horizontal scroll
  - Task cards full width with padding
  - Forms stack vertically
  - Buttons touch-friendly (48px+)
  - Navigation accessible

- [ ] T060 [P] [US10] Test on tablet (768px width):
  - Two-column layout for task grid
  - Forms side-by-side if appropriate
  - Improved spacing and readability

- [ ] T061 [P] [US10] Test on desktop (1920px width):
  - Three-column grid or card view
  - Full feature set visible
  - Optimal use of space

- [ ] T062 [US10] Fix responsive issues found during testing:
  - Adjust breakpoints if needed
  - Refine padding/margins per device
  - Improve mobile UX

---

## Phase 13: Integration Testing & Polish

### Goal
Comprehensive testing of complete user workflows and final polish.

### Independent Test Criteria
✓ Complete signup → signin → create → edit → delete → logout workflow
✓ Cross-browser compatibility (Chrome, Firefox, Safari)
✓ Performance: signup < 3min, signin < 2min, dashboard < 2sec
✓ Security: No tokens in logs, XSS protection, CORS working
✓ Accessibility: Keyboard navigation, proper ARIA labels

---

## Phase 13 Tasks

### Integration Testing

- [ ] T063 Test complete workflow:
  - New user signup
  - User signin
  - View empty dashboard
  - Create first task
  - View task in list
  - Edit task
  - Complete task
  - Create second task
  - Edit second task
  - Delete task
  - Logout
  - Verify cannot access dashboard without login

- [ ] T064 [P] Test error scenarios:
  - Signup with duplicate email → shows error
  - Signin with wrong password → shows error
  - Create task without title → shows error
  - Delete task on network failure → retry works
  - Token expiration during action → redirects to signin

- [ ] T065 [P] Test authentication persistence:
  - Login → close browser → reopen → still logged in
  - Verify token in cookie (DevTools)
  - Logout → refresh page → on signin page
  - No JWT in URL or local storage

### Performance & Security

- [ ] T066 [US10] Measure performance:
  - Signup form submission < 3 seconds
  - Signin form submission < 2 seconds
  - Dashboard load with 20 tasks < 2 seconds
  - Task create/update/delete < 1 second each

- [ ] T067 [P] Security verification:
  - JWT token only in Authorization header (not localStorage, not URLs)
  - Cookie marked httpOnly (DevTools → Application → Cookies)
  - Error messages don't leak user info (generic "Invalid email or password")
  - CORS headers allow frontend origin

### Cross-Browser Testing

- [ ] T068 [US10] Test on Chrome (latest):
  - All features work
  - Forms submit correctly
  - Responsive design loads

- [ ] T069 [P] Test on Firefox (latest):
  - All features work
  - No console errors

- [ ] T070 [P] Test on Safari (latest):
  - All features work
  - Cookie handling correct

### Accessibility

- [ ] T071 [US10] Keyboard navigation:
  - Tab through form fields
  - Enter submits form
  - Escape closes modal
  - Focus visible on all interactive elements

- [ ] T072 [P] ARIA labels and semantic HTML:
  - Buttons have accessible labels
  - Form labels associated with inputs
  - Error messages linked to fields

### Final Polish

- [ ] T073 Code cleanup:
  - Remove console.logs
  - Fix TypeScript warnings
  - Format code with Prettier
  - Run ESLint and fix issues

- [ ] T074 Documentation:
  - Update README with setup instructions
  - Document API wrapper usage
  - Add comments to complex logic

- [ ] T075 Build and deploy check:
  - Run `npm run build` successfully
  - Check bundle size reasonable
  - Verify no missing files

---

## Implementation Strategy

### MVP Scope (Phase 1-6)
**Core functionality**: Signup, Signin, Dashboard, Create Task
**Effort**: ~12-14 hours
**Value**: Users can create and view tasks

**Implement in order**:
1. Setup (T001-T009)
2. Foundational (T010-T019)
3. Signup (T020-T024)
4. Signin (T025-T029)
5. Dashboard (T030-T036)
6. Create Task (T037-T041)

Then test end-to-end before adding more features.

### Full Feature (Phase 1-13)
**Complete functionality**: All 10 user stories + testing
**Effort**: ~18-25 hours
**Value**: Production-ready task management application

**After MVP, add**:
7. Edit Task (T042-T045)
8. Toggle Completion (T046-T048)
9. Delete Task (T049-T051)
10. Logout (T052-T053)
11. Error Handling (T054-T057)
12. Responsive Design (T058-T062)
13. Testing & Polish (T063-T075)

### Parallel Opportunities
- Setup (T001-T009): All independent, run in parallel
- Foundational (T010-T019): Tasks 10-12 and 15-17 can parallel
- During each story: Different components can be built in parallel (marked [P])

---

## Testing Validation Checklist

Each story should be tested independently:

### US1 - Signup
- [ ] Valid signup creates account
- [ ] Email validation prevents invalid format
- [ ] Password validation enforces strength
- [ ] Duplicate email shows error
- [ ] Token stored in cookie
- [ ] Redirected to dashboard

### US2 - Signin
- [ ] Valid credentials grant access
- [ ] Invalid credentials show generic error
- [ ] Token stored and persists
- [ ] User stays logged in after refresh

### US3 - Dashboard
- [ ] Protected route (unauthenticated redirected)
- [ ] Task list fetches from backend
- [ ] Loading indicator shown
- [ ] Empty state displayed when no tasks
- [ ] Pagination works for 20+ tasks
- [ ] Responsive on mobile/tablet/desktop

### US4 - Create Task
- [ ] Modal/form opens on button click
- [ ] Title required validation works
- [ ] Valid submission POSTs to backend
- [ ] Task appears in list immediately
- [ ] Error shown if API fails
- [ ] Form closes on success

### US5 - Edit Task
- [ ] Edit button opens pre-populated form
- [ ] Changes saved to backend
- [ ] Task updates in list immediately
- [ ] Error handling for permission/not found

### US6 - Toggle Completion
- [ ] Checkbox changes completion status
- [ ] Visual change reflects status
- [ ] Change persists after refresh

### US7 - Delete Task
- [ ] Delete button shows confirmation
- [ ] Confirmed delete removes task
- [ ] Canceled delete keeps task
- [ ] Error handling if API fails

### US8 - Logout
- [ ] Sign Out button works
- [ ] Redirects to signin page
- [ ] Token cleared from cookie
- [ ] Cannot access dashboard

### US9 - Error Handling
- [ ] All error types handled gracefully
- [ ] Generic error messages (no user enumeration)
- [ ] Retry logic works

### US10 - Responsive Design
- [ ] Mobile: no horizontal scroll, readable
- [ ] Tablet: optimized layout
- [ ] Desktop: full features visible

---

**Status**: Ready for implementation via `/sp.implement`

**Next Command**: `/sp.implement` to execute all tasks in order
