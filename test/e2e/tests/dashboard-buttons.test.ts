import { test, expect } from '@playwright/test';

test.describe('Botones del Panel de Control', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/nombre de usuario/i).fill('admin');
    await page.getByLabel(/contraseña/i).fill('admin');
    await page.getByRole('button', { name: /iniciar sesión/i }).click();
    await expect(page).toHaveURL(/\/dashboard$/, { timeout: 10000 });
    await expect(page.getByRole('heading', { name: 'Panel de Control' })).toBeVisible({ timeout: 5000 });
  });

  test('should navigate to appointments from "Today Appointments" card', async ({ page }) => {
    await page.getByRole('link', { name: 'Citas de Hoy' }).click();
    await expect(page).toHaveURL(/\/citas$/, { timeout: 5000 });
    await expect(page.getByRole('heading', { name: 'Citas' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should navigate to user management from "Manage Users" card', async ({ page }) => {
    await page.getByRole('link', { name: 'Gestionar Usuarios' }).click();
    await expect(page).toHaveURL(/\/admin\/users$/, { timeout: 5000 });
    // PageContainer renders <h1>Usuarios</h1>
    await expect(page.getByRole('heading', { name: 'Usuarios' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should navigate to register user from "Register User" card', async ({ page }) => {
    await page.getByRole('link', { name: 'Registrar Usuario' }).click();
    await expect(page).toHaveURL(/\/admin\/users\/register$/, { timeout: 5000 });
    // Register page renders <h2>Registro</h2>
    await expect(page.getByRole('heading', { name: 'Registro' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should display "Pending Tasks" and "Alerts" cards', async ({ page }) => {
    await expect(page.getByText('Tareas Pendientes')).toBeVisible();
    await expect(page.getByText('Alertas')).toBeVisible();
  }, { timeout: 30000 });
});
