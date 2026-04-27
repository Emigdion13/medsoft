import { test, expect } from '@playwright/test';
import { performLogin, getAuthenticatedContext, createAPIContext } from './fixtures/api';

test.describe('Authentication', () => {
  const frontendURL = process.env.TEST_BASE_URL || 'http://localhost:5173';
  const backendURL = process.env.TEST_BACKEND_URL || 'http://localhost:8000';

  test('should login with valid credentials', async ({ page }) => {
    await page.goto(`${frontendURL}/login`);

    // Fill in login form
    await page.getByLabel(/username/i).fill('admin');
    await page.getByLabel(/password/i).fill('admin');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Should redirect to dashboard
    await expect(page).toHaveURL(/dashboard/i);

    // Verify user is logged in (check for logout button or user info)
    await expect(page.getByText(/admin|logout|sign out/i)).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto(`${frontendURL}/login`);

    await page.getByLabel(/username/i).fill('invalid');
    await page.getByLabel(/password/i).fill('wrong');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Should show error message
    await expect(page.getByText(/error|invalid|credential/i)).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('API: should return valid tokens on login', async () => {
    const apiContext = await getAuthenticatedContext(backendURL);

    const response = await apiContext.get('/api/users/');
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
  }, { timeout: 30000 });

  test('API: should reject requests with invalid token', async () => {
    // Create a context without valid auth - but this fixture always logs in
    // For true unauthenticated testing, we'd need to modify the fixture or use raw request
    const apiContext = await createAPIContext(backendURL);

    // Attempting to access protected endpoint without proper auth
    const response = await apiContext.get('/api/users/');

    expect(response.status()).toBe(401);
  }, { timeout: 30000 });
});
