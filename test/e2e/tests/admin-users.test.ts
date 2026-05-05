import { test, expect } from '@playwright/test';

test.describe('Gestión de Usuarios', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/nombre de usuario/i).fill('admin');
    await page.getByLabel(/contraseña/i).fill('admin');
    await page.getByRole('button', { name: /iniciar sesión/i }).click();
    await expect(page).toHaveURL(/\/dashboard$/, { timeout: 10000 });
  });

  test('should navigate to user management from sidebar', async ({ page }) => {
    await page.getByRole('link', { name: 'Gestión de Usuarios' }).click();
    await expect(page).toHaveURL(/\/admin\/users$/, { timeout: 5000 });
    // PageContainer renders <h1>Usuarios</h1>
    await expect(page.getByRole('heading', { name: 'Usuarios' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should display user list table', async ({ page }) => {
    await page.getByRole('link', { name: 'Gestión de Usuarios' }).click();
    await expect(page).toHaveURL(/\/admin\/users$/, { timeout: 5000 });

    // The UserList component renders a table with columns
    await expect(page.locator('table')).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });
});
