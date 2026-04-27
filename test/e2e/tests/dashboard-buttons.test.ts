import { test, expect } from '@playwright/test';

test.describe('Dashboard Buttons', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/username/i).fill('admin');
    await page.getByLabel(/password/i).fill('admin');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/dashboard$/, { timeout: 10000 });
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible({ timeout: 5000 });
  });

  test('should navigate to appointments from "Today Appointments" card', async ({ page }) => {
    await page.getByRole('link', { name: 'Today Appointments' }).click();
    await expect(page).toHaveURL(/\/appointments$/, { timeout: 5000 });
    await expect(page.getByRole('heading', { name: 'Appointments' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should navigate to user management from "Manage Users" card', async ({ page }) => {
    await page.getByRole('link', { name: 'Manage Users' }).click();
    await expect(page).toHaveURL(/\/admin\/users$/, { timeout: 5000 });
    // PageContainer renders <h1>Users</h1>
    await expect(page.getByRole('heading', { name: 'Users' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should navigate to register user from "Register User" card', async ({ page }) => {
    await page.getByRole('link', { name: 'Register User' }).click();
    await expect(page).toHaveURL(/\/admin\/users\/register$/, { timeout: 5000 });
    // Register page renders <h2>Register</h2>
    await expect(page.getByRole('heading', { name: 'Register' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should display "Pending Tasks" and "Alerts" cards', async ({ page }) => {
    await expect(page.getByText('Pending Tasks')).toBeVisible();
    await expect(page.getByText('Alerts')).toBeVisible();
  }, { timeout: 30000 });
});
