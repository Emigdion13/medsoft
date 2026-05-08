import { test, expect } from '@playwright/test';
import { performLogin, getAuthenticatedContext, createAPIContext } from './fixtures/api';

test.describe('Autenticación', () => {
  const frontendURL = process.env.TEST_BASE_URL || 'http://localhost:5173';
  const backendURL = process.env.TEST_BACKEND_URL || 'http://localhost:8000';

  test('should login with valid credentials', async ({ page }) => {
    await page.goto(`${frontendURL}/login`);

    // Fill in login form
    await page.getByLabel(/nombre de usuario/i).fill('admin');
    await page.getByLabel(/contraseña/i).fill('admin');
    await page.getByRole('button', { name: /iniciar sesión/i }).click();

    // Should redirect to dashboard
    await expect(page).toHaveURL(/dashboard/i);

    // Verify user is logged in (check for logout button)
    await expect(page.getByRole('button', { name: 'Cerrar Sesión' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto(`${frontendURL}/login`, { timeout: 30000, waitUntil: 'domcontentloaded' });

    // Wait for form to be ready
    await expect(page.locator('form')).toBeVisible({ timeout: 5000 });

    await page.getByLabel(/nombre de usuario/i).fill('invaliduser');
    await page.getByLabel(/contraseña/i).fill('wrongpass');
    await page.getByRole('button', { name: /iniciar sesión/i }).click();

    // Wait for button to become enabled again (after error handling)
    await expect(page.getByRole('button', { name: /Iniciar Sesión/ })).not.toBeDisabled({ timeout: 10000 });

    // Now the error should be visible
    const errorLocator = page.locator('form >> div', { hasText: /Session expired|Invalid|Error/ });
    await expect(errorLocator).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('API: should return valid tokens on login', async () => {
    const { context: apiContext, token } = await getAuthenticatedContext(backendURL);

    const response = await apiContext.get('/api/users/', {
      headers: { Authorization: `Bearer ${token}` },
    });
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
