# Medisoft - Historical Fixes

This file documents important fixes that have been applied to the project. Read this before making changes to avoid reintroducing old bugs.

---

## 1. Docker API Proxy Configuration Fix - April 26, 2026

### Problem Description

The frontend was unable to communicate with the backend API in Docker environment. Requests were failing because:

1. The Vite dev server proxy wasn't configured for Docker networking
2. Frontend `VITE_API_URL` was pointing to wrong host

### Root Cause

In Docker, the frontend container needs to reach the backend via Docker service name (`http://backend:8000/api`) instead of `localhost`.

### Solution

**Changes Made:**

**frontend/src/utils/api.ts**
```typescript
// Use /api as the default so the Vite dev proxy handles routing during local dev.
// Docker builds override this via ENV VITE_API_URL=/api in the Dockerfile.
const BASE_URL = import.meta.env.VITE_API_URL || '/api'
```

**frontend/Dockerfile.dev**
```dockerfile
ENV VITE_BACKEND_URL=http://backend:8000/api
```

### Key Takeaways

1. **Local dev**: Use relative `/api` paths for Vite proxy to handle routing
2. **Docker**: Set `VITE_API_URL` to absolute Docker service URL
3. **Check the proxy config** - Vite's `vite.config.ts` should have proper rewrite rules

---

## 2. E2E Auth Test Fix - April 27, 2026

### Problem Description

E2E authentication tests were failing because the `Authorization` header was not being sent with API requests, even after login.

### Root Cause

When using Playwright's `request.newContext()`, the new context doesn't inherit headers from previous contexts. The `getAuthenticatedContext()` function was creating a fresh context that dropped the Authorization header.

### Solution

**test/e2e/tests/fixtures/api.ts**
```typescript
// Before: Context created with headers (dropped on newContext)
return await request.newContext({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${access}`,
  },
});

// After: Return context and token separately, pass token per-request
return {
  context: apiContext,
  token: access,
};
```

Tests now manually pass the Authorization header:
```typescript
const { context, token } = await getAuthenticatedContext();
await context.post(`${API_BASE}/doctors/`, {
  headers: { Authorization: `Bearer ${token}` },
});
```

### Key Takeaways

1. **Playwright contexts don't inherit headers** - Each `request.newContext()` creates a fresh state
2. **Pass auth tokens explicitly per-request** in E2E tests
3. **Return both context and token** from fixture functions for flexibility

---

## 3. Appointment Creation 500 Error Fix - April 28, 2026

### Problem Description

POST requests to `/api/appointments/` returned HTTP 500 with error: `{"detail":"organization field cannot be null"}`

### Root Cause Analysis

The DRF serializer had two issues:

1. **`organization` was marked as `read_only`** but is a required (NOT NULL) model field
2. **Foreign key IDs were popped without being re-added** in `serializer.create()`

```python
# Broken code
def create(self, validated_data: dict) -> Appointment:
    validated_data.pop('doctor_id')  # Removed but never added back!
    validated_data.pop('patient_id')  # Removed but never added back!
```

### Solution

**backend/accounts/serializers.py**

```python
def create(self, validated_data: dict) -> Appointment:
    """Set organization and created_by from authenticated user."""
    doctor_id = validated_data.pop('doctor_id', None)
    patient_id = validated_data.pop('patient_id', None)

    request = self.context.get('request')
    
    if request and hasattr(request, 'user'):
        validated_data['organization'] = request.user.organization
        validated_data['created_by'] = request.user

    # Re-add foreign key IDs for parent create method
    if doctor_id:
        validated_data['doctor_id'] = doctor_id
    if patient_id:
        validated_data['patient_id'] = patient_id

    return super().create(validated_data)
```

**backend/accounts/views.py**

```python
def perform_create(self, serializer: AppointmentSerializer) -> None:
    """Let the serializer handle organization and created_by assignment."""
    serializer.save()
```

### Key Takeaways

1. **DRF read_only fields aren't passed from request data** - Set required model fields manually in `create()`
2. **Foreign key IDs use `_id` suffix** - DRF expects `doctor_id`, not `doctor` for write operations
3. **Access authenticated user via context** - Use `self.context['request'].user`

---

## General Guidelines

When fixing issues in this project:

1. **Check HowItWasFixed.md first** - Similar issues may have been solved before
2. **Review git history** - `git log --oneline` shows recent changes
3. **Test in both local and Docker modes** - Configuration differs between environments
4. **E2E tests require auth headers** - Always pass Bearer tokens explicitly

---

## Debugging Approach - April 28, 2026 (This Session)

### DRF Serializer Field Handling

When working with Django REST Framework serializers that have required model fields:

1. **Read-only fields aren't in request data**
   - Fields marked `read_only=True` won't appear in `validated_data` from POST requests
   - If the model requires them, you must set them manually in `create()` or `update()`

2. **Foreign key ID naming convention**
   - For a field named `doctor`, the write field is `doctor_id`
   - DRF handles the conversion: `doctor` (read) ↔ `doctor_id` (write)
   - If you pop one, remember to re-add it for the parent create method

3. **Context access pattern**
   ```python
   # View passes context automatically
   serializer = AppointmentSerializer(data=request.data, context={'request': request})
   
   # Serializer can access:
   user = self.context['request'].user
   ```

### Testing API Endpoints

Before writing frontend/test code, verify backend endpoints directly:

```bash
# Test with valid token
curl -s http://localhost:8000/api/appointments/ -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"doctor_id": "...", "patient_id": "...", ...}'

# Check response format:
# - 201 + JSON = success
# - 400 = validation errors (check error details)
# - 401 = auth issue (invalid/expired token)
# - 500 = server error (check Django logs)
```

### File Update Pattern

When copying code changes to Docker containers:

```bash
# Copy files to container
docker-compose cp backend/accounts/serializers.py backend:/app/accounts/
docker-compose cp backend/accounts/views.py backend:/app/accounts/

# Restart to load changes
docker-compose restart backend

# Check logs for errors
docker-compose logs -f backend
```

---

## 4. E2E Test Failures Fix - April 28, 2026

### Problem Description

Multiple E2E tests were failing with different issues:

1. **Dashboard navigation test** failed: `getByText('Dashboard')` resolved to no elements (page uses "Panel de Control")
2. **Invalid credentials test** failed: Regex `/error|inválido|credencial|caducado/i` didn't match "Invalid credentials" from backend
3. **Appointment creation verification** failed with strict mode error: `getByText('Juan')` matched 5 elements (hidden `<option>` + 3 table cells)

### Root Cause

1. **Translation mismatch**: Tests expected English "Dashboard" but UI renders Spanish "Panel de Control"
2. **API response language**: Backend returns English error messages ("Invalid credentials"), tests looked for Spanish keywords
3. **Selector specificity**: `getByText()` matches hidden dropdown options, not just visible table cells

### Solution

**test/e2e/tests/auth.test.ts**
```typescript
// Before:
await expect(page.getByText(/error|inválido|credencial|caducado/i)).toBeVisible(...)

// After:
await expect(page.getByText(/error|Invalid credentials/i)).toBeVisible(...)
```

**test/e2e/tests/frontend.test.ts**
```typescript
// Same fix - match actual backend response "Invalid credentials"
await expect(page.getByText(/error|Invalid credentials/i)).toBeVisible(...)
```

**test/e2e/tests/appointments.test.ts**
```typescript
// Fix 1: Use correct page title
await expect(page.getByRole('heading', { name: 'Panel de Control' })).toBeVisible(...)

// Fix 2: Use table cell role for specificity (avoids hidden <option> elements)
await expect(page.getByRole('cell', { name: patient.first_name }).first()).toBeVisible(...)
await expect(page.getByRole('cell', { name: doctor.first_name })).toBeVisible(...)
```

### Key Takeaways

1. **Match actual UI text**: The app is in Spanish, use "Panel de Control" not "Dashboard"
2. **Check backend error messages**: API returns English strings regardless of frontend language
3. **Use specific Playwright roles**: `getByRole('cell', { name: ... })` targets table cells only, avoids hidden elements
4. **Wait for list updates**: Use `page.waitForSelector('table tbody tr')` before asserting new items appear

---

## General Guidelines (Updated April 28, 2026)

When fixing issues in this project:

1. **Check HowItWasFixed.md first** - Similar issues may have been solved before
2. **Review git history** - `git log --oneline` shows recent changes
3. **Test in both local and Docker modes** - Configuration differs between environments
4. **E2E tests require auth headers** - Always pass Bearer tokens explicitly
5. **Playwright selectors need specificity** - Use `getByRole('cell')` instead of generic `getByText()` to avoid hidden elements
6. **Backend errors are in English** - Even though the frontend is Spanish, API returns English error messages

---

## 5. Appointment Timezone Bug Fix - April 28, 2026

### Problem Description

When users created appointments via the UI form:
1. User selects a specific time (e.g., 10:30 AM) in their local timezone
2. The appointment was stored with a shifted time (e.g., 6:30 PM or other offset)
3. The time displayed in the list didn't match what was selected in the form

### Root Cause

**The Issue:** HTML `datetime-local` inputs return **naive datetime strings** without timezone information (e.g., `"2026-04-30T10:30"`).

When Django with `USE_TZ=True` receives these naive timestamps:
- It interprets them as **UTC**
- Then converts to the server's timezone (`America/New_York`)
- Result: Time gets shifted by the timezone offset

**Example (EST/EDT timezone):**
- User selects: `2026-04-30T10:30` (intended as 10:30 AM local)
- Browser sends: `"2026-04-30T10:30"` (no timezone info)
- Django interprets as UTC: `2026-04-30T10:30 UTC`
- Server converts to EST: `2026-04-30 06:30 AM EST` (4 hours earlier!)
- User sees: Appointment at 6:30 AM instead of 10:30 AM

### Solution

**frontend/src/pages/Appointments.tsx**

Added a timezone-aware function that appends the user's local timezone offset before sending to backend:

```typescript
const formatWithOffset = (dtString: string): string => {
  const d = new Date(dtString)
  const offsetMinutes = d.getTimezoneOffset()
  const offsetHours = Math.floor(Math.abs(offsetMinutes) / 60)
  const offsetMins = Math.abs(offsetMinutes) % 60
  const sign = offsetMinutes <= 0 ? '+' : '-'
  // Example: "2026-04-30T10:30" -> "2026-04-30T10:30-04:00"
  const isoWithOffset = `${dtString}${sign}${offsetHours.toString().padStart(2, '0')}:${offsetMins.toString().padStart(2, '0')}`
  return isoWithOffset
}
```

**Before (buggy):**
```typescript
const payload = {
  start_at: form.startAt,  // "2026-04-30T10:30" - naive!
  end_at: form.endAt,
}
```

**After (fixed):**
```typescript
const payload = {
  start_at: formatWithOffset(form.startAt),  // "2026-04-30T10:30-04:00" - with offset!
  end_at: formatWithOffset(form.endAt),
}
```

### Test Coverage Added

**test/e2e/tests/appointments.test.ts**

Added new test `should display appointment time correctly in list after creating via form (timezone roundtrip)` that:

1. Creates an appointment via the UI form
2. Sets specific times (e.g., 10:30 AM)
3. Verifies the same times appear when editing the appointment
4. Confirms datetime roundtrip works end-to-end

### Key Takeaways

1. **`datetime-local` returns naive datetimes** - Always include timezone offset when sending to backend with `USE_TZ=True`
2. **Backend interprets naive timestamps as UTC** - This causes timezone shifts
3. **Roundtrip verification is critical** - Test that what you select in form = what you get back
4. **`getTimezoneOffset()` gives minutes east of UTC** - Negative values mean you're west of UTC (e.g., EST = -240)

### How to Verify the Fix

1. Create an appointment at 10:30 AM local time via the UI form
2. Edit the appointment - the form should show 10:30 AM (not shifted)
3. Check the backend database - stored timestamp should reflect correct UTC time
4. Run E2E test: `npm run test:e2e -- appointments.test.ts`

---

## 6. Appointment Timezone Fix - April 28, 2026 (Alternative Approach)

### Problem Description

The initial fix using timezone offset appending had issues because:
- The frontend's `formatWithOffset()` approach added offset to naive datetimes
- But the backend was still interpreting times in wrong timezone (America/Chicago instead of America/Santo_Domingo)
- System timezone detection in Playwright tests didn't match Dominican Republic timezone

### Root Cause

The **real issue** was that when users in the Dominican Republic selected times like "10:00 AM", they expected it to be 10:00 AM DR time. However:

1. HTML `datetime-local` inputs return **naive datetime strings** without any timezone info
2. Django with `USE_TZ=True` interprets naive datetimes as **UTC**
3. The system running the tests was in America/Chicago (UTC-5), not America/Santo_Domingo (UTC-4)

### Solution

**Backend Fix (`backend/accounts/serializers.py`):**

Created a custom serializer field that treats incoming naive datetimes as America/Santo_Domingo timezone:

```python
class TimeZoneDateTimeField(serializers.DateTimeField):
    """DateTimeField that treats naive datetimes as America/Santo_Domingo timezone."""
    
    def to_internal_value(self, value):
        if value is None:
            return value
        
        dt = super().to_internal_value(value)
        
        # If datetime is naive (no timezone), assume it's in America/Santo_Domingo
        if dt is not None and dt.tzinfo is None:
            dr_tz = timezone.get_fixed_timezone(-240)  # America/Santo_Domingo is UTC-4
            dt = timezone.make_aware(dt, dr_tz)
        
        return dt
```

Applied to appointment fields:
```python
class AppointmentSerializer(serializers.ModelSerializer):
    start_at = TimeZoneDateTimeField()
    end_at = TimeZoneDateTimeField()
    ...
```

**Frontend Fix (`frontend/src/pages/Appointments.tsx`):**

Added helper function to convert UTC datetimes from API to local timezone for form display:

```typescript
const formatDateTimeForInput = (isoString: string): string => {
  const date = new Date(isoString)
  
  // Get the user's local timezone components
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  
  // Return in the format expected by datetime-local input
  return `${year}-${month}-${day}T${hours}:${minutes}`
}
```

Used when editing appointments:
```typescript
const handleEdit = (a: Appointment) => {
  setEditingId(a.id)
  const startLocal = formatDateTimeForInput(a.start_at)
  const endLocal = formatDateTimeForInput(a.end_at)
  
  setForm({
    doctor_id: a.doctor.id,
    patient_id: a.patient.id,
    start_at: startLocal,  // Local time for form
    end_at: endLocal,
    ...
  })
}
```

### How It Works

1. **User creates/edits appointment:** Frontend sends naive datetime `"2026-04-30T10:00"`
2. **Backend receives:** `TimeZoneDateTimeField` treats it as DR time (UTC-4), converts to UTC for storage
3. **API returns:** Datetime in ISO format with timezone, e.g., `"2026-04-30T14:00:00Z"`
4. **Frontend displays:** `formatDateTimeForInput()` converts back to local time for form display

### Key Takeaways

1. **Backend should interpret naive datetimes in app timezone** - Not UTC, but the business's local timezone
2. **Frontend should convert UTC to local for display** - Users see times in their browser context
3. **Consistent behavior requires both sides** - Backend interprets as DR time, frontend displays in local context
4. **DRF serializer fields can customize parsing** - Extend `DateTimeField` for timezone-specific handling

### Testing

1. Create an appointment at 10:00 AM via the UI form
2. Edit the appointment - the form should show 10:00 AM (not shifted)
3. Verify in database that UTC time is correct (14:00 UTC = 10:00 AM DR time)
4. The table display shows times correctly for the user's local timezone

### E2E Test Coverage

Added test `should display appointment time correctly (timezone roundtrip - America/Santo_Domingo)` in `test/e2e/tests/appointments.test.ts` that:

1. **Creates first appointment at 10:30 AM** via UI form
   - Sets specific time using naive datetime string from `toISOString().slice(0, 16)`
   - Verifies the same time appears when editing (form roundtrip)

2. **Creates second appointment at 2:00 PM** for additional verification
   - Uses different time to ensure timezone handling is consistent across hours
   - Verifies multiple appointments don't interfere with each other

3. **Key verification points:**
   - When form opens for edit, `#start-at` and `#end-at` inputs show the same times entered
   - If backend incorrectly interprets naive datetimes as UTC, times would shift (e.g., 10:30 AM → 6:30 PM)
   - The test passes only if timezone conversion is correct on both sides

### Alternative Considered (Not Used)

Initially tried adding timezone offset to naive datetimes on frontend:
```typescript
// This approach was abandoned
const isoWithOffset = `${dtString}${sign}${offsetHours}:${offsetMins}`
```

This didn't work because:
- The backend was running in wrong timezone context (America/Chicago vs America/Santo_Domingo)
- Playwright tests use system timezone which may differ from app's business timezone

---

## 7. Docker Frontend-Backend Proxy Fix - May 11, 2026

### Problem Description

When running the application in Docker containers, the frontend could not communicate with the backend API. The Vite dev server proxy was failing because:

1. Inside the frontend container, `localhost` refers to the container itself, not the host machine
2. The proxy configuration was targeting `http://localhost:8000` which doesn't exist inside Docker
3. Need to use Docker service names (`backend:8000`) for inter-container communication

### Root Cause

Docker networking uses service discovery - containers communicate via service names, not `localhost`. When the frontend container tried to proxy `/api/*` requests to `http://localhost:8000`, it was looking for a server inside its own container (which doesn't exist).

### Solution

**frontend/vite.config.ts**

Updated the proxy configuration to use Docker service URL when running in Docker environment:

```typescript
const backendUrl = process.env.VITE_BACKEND_URL || 'http://localhost:8000'

proxy: {
  '/api': {
    target: backendUrl,
    changeOrigin: true,
    // ... other config
  }
}
```

**Environment Variables**

The `.env.docker` file already had the correct setting:
```bash
VITE_BACKEND_URL=http://backend:8000
```

This gets baked into the Docker image via `frontend/Dockerfile.dev`:
```dockerfile
ENV VITE_BACKEND_URL=http://backend:8000
```

### How It Works Now

When accessing the frontend via `http://localhost:5173` in Docker:

1. Browser requests go to the Vite dev server (frontend container)
2. `/api/*` requests are proxied by Vite to `http://backend:8000/api/*`
3. Backend processes the request and returns the response
4. Frontend receives the data seamlessly

### Key Takeaways

1. **Inside Docker, use service names** - `localhost` means "this container", not "host machine"
2. **Environment-specific URLs** - Use different backend URLs for local dev vs Docker
3. **Vite proxy is flexible** - Can be configured via environment variables at build time
4. **Test both modes** - Always verify API works in both local and Docker environments

### Verification Steps

```bash
# Reset admin password for testing
docker compose exec backend python manage.py shell -c "from apps.core.users.models import User; from django.contrib.auth.hashers import make_password; user = User.objects.get(username='admin'); user.password = make_password('admin123'); user.save(); print('Password updated')"

# Test login via frontend proxy
curl http://localhost:5173/api/auth/login/ -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Should return access and refresh tokens
```

---

## 8. TypeScript Type Mismatch Fix - May 11, 2026

### Problem Description

TypeScript compilation error:
```
frontend/src/utils/auth.tsx(37,29): error TS2339: Property 'access' does not exist on type 'User'.
```

The `refreshSession()` function was calling `authService.me()` and trying to access `.access` and `.refresh` properties that don't exist on the return type.

### Root Cause

**Type mismatch between implementation and interface:**

1. **Interface definition (`types.ts`):**
   ```typescript
   export interface AuthService {
     me(): Promise<User>  // Returns User directly
   }
   ```

2. **Implementation (`authService.ts`):**
   ```typescript
   async me() {
     const res = await api.get('/accounts/profile/')
     return res.data  // Returns raw API response with { access, refresh, user }
   }
   ```

3. **Usage in `auth.tsx`:**
   ```typescript
   const refreshSession = async () => {
     const me = await authService.me()  // TypeScript thinks this is User
     session.setUser(me)
     setUser(me)
   }
   ```

The code was written expecting the old API where `me()` returned `{ access, refresh, user }`, but after refactoring it should return just `User`.

### Solution

**backend/src/services/authService.ts** - Updated to match interface:

```typescript
async me() {
  const res = await api.get('/accounts/profile/')
  // Extract and return only the User object, not the full response
  return res.data.user as User
}
```

This ensures `authService.me()` returns a `User` object directly, matching the `AuthService` interface definition.

### Key Takeaways

1. **Interface contracts matter** - When you define an interface, implementations must match it exactly
2. **Type safety catches bugs early** - TypeScript would have prevented this mismatch from reaching production
3. **Refactoring requires updating all layers** - When changing return types, update:
   - The implementation
   - All callers of the function
   - Any type assertions or casts

### How to Verify the Fix

1. Run TypeScript check: `cd frontend && npx tsc --noEmit`
2. Build the project: `npm run build`
3. Both should complete without errors
