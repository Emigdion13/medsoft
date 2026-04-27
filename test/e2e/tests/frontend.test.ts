import { test, expect } from '@playwright/test';

test.describe('Frontend UI Tests', () => {
  const frontendURL = process.env.TEST_BASE_URL || 'http://localhost:5173';

  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto(`${frontendURL}/login`);
    await page.getByLabel(/username/i).fill('admin');
    await page.getByLabel(/password/i).fill('admin');
    await page.getByRole('button', { name: /sign in|login/i }).click();
    await expect(page).toHaveURL(/dashboard/i, { timeout: 10000 });
  });

  test('should display dashboard with welcome message', async ({ page }) => {
    // Check for dashboard heading
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible({ timeout: 5000 });

    // Verify key dashboard cards are visible
    await expect(page.getByRole('link', { name: 'Today Appointments' })).toBeVisible();
    await expect(page.getByText('Pending Tasks')).toBeVisible();
    await expect(page.getByText('Alerts')).toBeVisible();
  }, { timeout: 30000 });

  test('should navigate to dashboard when clicking Dashboard link', async ({ page }) => {
    await page.getByRole('link', { name: 'Dashboard' }).click();
    await expect(page).toHaveURL(/\/dashboard$/, { timeout: 5000 });
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should navigate to appointments page when clicking Appointments link', async ({ page }) => {
    await page.getByRole('link', { name: 'Appointments', exact: true }).click();
    await expect(page).toHaveURL(/\/appointments$/, { timeout: 5000 });
    await expect(page.getByRole('heading', { name: 'Appointments' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should navigate to patients page when clicking Patients link', async ({ page }) => {
    await page.getByRole('link', { name: 'Patients' }).click();
    await expect(page).toHaveURL(/\/patients$/, { timeout: 5000 });
    await expect(page.getByRole('heading', { name: 'Patients' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should navigate to medical records page when clicking Medical Records link', async ({ page }) => {
    await page.getByRole('link', { name: 'Medical Records' }).click();
    await expect(page).toHaveURL(/\/medical-records$/, { timeout: 5000 });
    await expect(page.getByRole('heading', { name: 'Medical Records' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should navigate to user management when clicking User Management link', async ({ page }) => {
    await page.getByRole('link', { name: 'User Management' }).click();
    await expect(page).toHaveURL(/\/admin\/users$/, { timeout: 5000 });
  }, { timeout: 30000 });

  test('should log out when clicking Logout button', async ({ page }) => {
    await page.getByRole('button', { name: 'Logout' }).click();
    await expect(page).toHaveURL(/\/login$/, { timeout: 5000 });
  }, { timeout: 30000 });

  test('should have working navigation from dashboard', async ({ page }) => {
    const links = page.locator('a');
    const linkCount = await links.count();

    // Should have at least some links
    expect(linkCount).toBeGreaterThanOrEqual(1);
  }, { timeout: 30000 });

  test('should show error if login fails', async ({ page }) => {
    await page.goto(`${frontendURL}/login`);
    await page.getByLabel(/username/i).fill('wrong');
    await page.getByLabel(/password/i).fill('wrong');
    await page.getByRole('button', { name: /sign in|login/i }).click();

    await expect(page.getByText(/error|invalid|failed/i)).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

});
