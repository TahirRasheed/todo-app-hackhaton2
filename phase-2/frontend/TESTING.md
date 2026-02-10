# Frontend Testing Guide

## Manual Testing Checklist

### Authentication Flow
- [ ] **Signup**: Create new account with valid credentials
  - Name, email, password (8+ chars, uppercase, lowercase, number)
  - Verify token stored in cookies
  - Verify user data in localStorage
  - Redirects to /dashboard
  
- [ ] **Signin**: Login with existing account
  - Enter email and password
  - Token attached to subsequent requests
  - Redirects to /dashboard
  - Invalid credentials show generic error message
  
- [ ] **Logout**: Sign out from dashboard
  - Click "Sign Out" button
  - Token cleared from cookies
  - User data cleared from localStorage
  - Redirects to /signin

### Task Operations
- [ ] **Create Task**: Add new task
  - Click "+ Create Task" button
  - Modal appears with title/description fields
  - Submit with title only
  - Submit with title and description
  - Task appears in list immediately (optimistic)
  - Error handling if API fails (rollback)
  
- [ ] **Edit Task**: Modify existing task
  - Click "Edit" button on task card
  - Modal shows pre-populated values
  - Modify title or description
  - Submit changes
  - Task updates in list immediately
  - Error handling for failed updates
  
- [ ] **Complete Task**: Toggle task status
  - Click checkbox to mark complete
  - Visual feedback (strikethrough)
  - API request sent
  - Changes persist on refresh
  
- [ ] **Delete Task**: Remove task
  - Click "Delete" button
  - Confirmation dialog appears with task name
  - Cancel: dialog closes, task remains
  - Confirm: task removed from list (optimistic)
  - Error handling with rollback

### Error Scenarios
- [ ] **Network Error**: Turn off internet, try operation
  - Shows "Unable to connect" error
  - Retry button available
  
- [ ] **401 Unauthorized**: Invalid/expired token
  - Redirects to /signin automatically
  - Session cleared
  
- [ ] **403 Forbidden**: Cross-user access attempt
  - Shows "No permission" error
  - Prevents access to other user's data
  
- [ ] **404 Not Found**: Deleted task operations
  - Shows "Not found" error gracefully
  
- [ ] **500 Server Error**: Backend error
  - Shows "Server error, please try again later"
  - Allows retry

### Responsive Design
- [ ] **Mobile (375px)**
  - No horizontal scrolling
  - Single column task list
  - Touch-friendly buttons (48px minimum)
  - Forms stack vertically
  
- [ ] **Tablet (768px)**
  - Two-column task grid
  - Readable text sizes
  - Navigation accessible
  
- [ ] **Desktop (1024px+)**
  - Three-column task grid
  - Optimal spacing
  - Hover effects work

### Performance
- [ ] **Page Load**: Initial load time < 2s
- [ ] **Task Operations**: Create/edit/delete < 500ms
- [ ] **No Console Errors**: DevTools shows no errors/warnings
- [ ] **Memory**: No memory leaks (DevTools profiler)

## Browser Testing
- [ ] **Chrome/Edge** (Chromium)
- [ ] **Firefox**
- [ ] **Safari**
- [ ] **Mobile Safari** (iOS)
- [ ] **Chrome Mobile** (Android)

## Accessibility Testing
- [ ] **Keyboard Navigation**: Tab through form fields, buttons
- [ ] **Screen Reader**: Test with NVDA/JAWS
- [ ] **Color Contrast**: Text meets WCAG AA standards
- [ ] **Focus Indicators**: Visible focus rings on interactive elements
- [ ] **Aria Labels**: Buttons have proper aria-label attributes

## API Integration Testing
- [ ] **JWT Attachment**: Verify Authorization header on all requests
- [ ] **Cookie Handling**: Token stored and sent correctly
- [ ] **CORS**: No CORS errors with backend
- [ ] **Request/Response Format**: Matches API contract

## Example Integration Test (Playwright)
```typescript
import { test, expect } from '@playwright/test';

test.describe('Todo App - Full User Flow', () => {
  test('should signup, create task, and logout', async ({ page }) => {
    // Navigate to signup
    await page.goto('http://localhost:3001/auth/signup');
    
    // Fill form
    await page.fill('[name="name"]', 'Test User');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'TestPass123');
    
    // Submit
    await page.click('button:has-text("Create Account")');
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('http://localhost:3001/dashboard');
    
    // Create task
    await page.click('button:has-text("Create Task")');
    await page.fill('[placeholder="Enter task title"]', 'Test Task');
    await page.click('button:has-text("Create Task")');
    
    // Verify task appears
    await expect(page.locator('h3:has-text("Test Task")')).toBeVisible();
    
    // Logout
    await page.click('button:has-text("Sign Out")');
    await expect(page).toHaveURL('http://localhost:3001/auth/signin');
  });
});
```

## Performance Benchmarks
- **Signup**: < 1s
- **Signin**: < 1s
- **Task Creation**: < 500ms
- **Task List Load**: < 1s
- **Page Navigation**: < 300ms
- **Responsive Layout**: Reflow < 60ms

## Known Issues & Limitations
- [ ] No offline mode
- [ ] No real-time sync (requires manual refresh)
- [ ] No drag-and-drop reordering
- [ ] No task filtering/search (Phase 13+)
- [ ] No task categories/tags (Phase 13+)

## Future Test Coverage
- [ ] Unit tests for utilities (validation, storage, auth)
- [ ] Component tests (React Testing Library)
- [ ] Integration tests (Playwright/Cypress)
- [ ] E2E tests with real backend
- [ ] Performance tests (Lighthouse)
- [ ] Accessibility tests (axe-core)
