import { test, expect } from '@playwright/test';

test.describe('Appointments Navigation', () => {
  test('should navigate to appointments from Dashboard "Today Appointments" card', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/username/i).fill('admin');
    await page.getByLabel(/password/i).fill('admin');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/dashboard$/, { timeout: 10000 });
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible({ timeout: 5000 });

    // Click the "Today Appointments" card on the dashboard
    await page.getByRole('link', { name: 'Today Appointments' }).click();
    await expect(page).toHaveURL(/\/appointments$/, { timeout: 5000 });
    await expect(page.getByRole('heading', { name: 'Appointments' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should navigate to appointments via sidebar', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/username/i).fill('admin');
    await page.getByLabel(/password/i).fill('admin');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/dashboard$/, { timeout: 10000 });

    // Click Appointments link in sidebar
    await page.getByRole('link', { name: 'Appointments', exact: true }).click();
    await expect(page).toHaveURL(/\/appointments$/, { timeout: 5000 });
    await expect(page.getByRole('heading', { name: 'Appointments' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });
});
