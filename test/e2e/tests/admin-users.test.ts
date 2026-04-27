import { test, expect } from '@playwright/test';

test.describe('User Management Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/username/i).fill('admin');
    await page.getByLabel(/password/i).fill('admin');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/dashboard$/, { timeout: 10000 });
  });

  test('should navigate to user management from sidebar', async ({ page }) => {
    await page.getByRole('link', { name: 'User Management' }).click();
    await expect(page).toHaveURL(/\/admin\/users$/, { timeout: 5000 });
    // PageContainer renders <h1>Users</h1>
    await expect(page.getByRole('heading', { name: 'Users' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should display user list table', async ({ page }) => {
    await page.getByRole('link', { name: 'User Management' }).click();
    await expect(page).toHaveURL(/\/admin\/users$/, { timeout: 5000 });

    // The UserList component renders a table with columns
    await expect(page.locator('table')).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });
});
