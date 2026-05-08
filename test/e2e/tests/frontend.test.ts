import { test, expect } from '@playwright/test';

test.describe('Pruebas de Interfaz Frontend', () => {
  const frontendURL = process.env.TEST_BASE_URL || 'http://localhost:5173';

  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto(`${frontendURL}/login`);
    await page.getByLabel(/nombre de usuario/i).fill('admin');
    await page.getByLabel(/contraseña/i).fill('admin');
    await page.getByRole('button', { name: /iniciar sesión|login/i }).click();
    await expect(page).toHaveURL(/dashboard/i, { timeout: 10000 });
  });

  test('should display dashboard with welcome message', async ({ page }) => {
    // Check for dashboard heading
    await expect(page.getByRole('heading', { name: 'Panel de Control' })).toBeVisible({ timeout: 5000 });

    // Verify key dashboard cards are visible
    await expect(page.getByRole('link', { name: 'Citas de Hoy' })).toBeVisible();
    await expect(page.getByText('Tareas Pendientes')).toBeVisible();
    await expect(page.getByText('Alertas')).toBeVisible();
  }, { timeout: 30000 });

  test('should navigate to dashboard when clicking Panel Principal link', async ({ page }) => {
    await page.getByRole('link', { name: 'Panel Principal' }).click();
    await expect(page).toHaveURL(/\/dashboard$/, { timeout: 5000 });
    await expect(page.getByRole('heading', { name: 'Panel de Control' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should navigate to appointments page when clicking Appointments link', async ({ page }) => {
    await page.getByRole('link', { name: 'Citas', exact: true }).click();
    await expect(page).toHaveURL(/\/appointments$/, { timeout: 5000 });
    await expect(page.getByRole('heading', { name: 'Citas' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should navigate to patients page when clicking Patients link', async ({ page }) => {
    await page.getByRole('link', { name: 'Pacientes' }).click();
    await expect(page).toHaveURL(/\/patients$/, { timeout: 5000 });
    await expect(page.getByRole('heading', { name: 'Pacientes' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should navigate to medical records page when clicking Medical Records link', async ({ page }) => {
    await page.getByRole('link', { name: 'Historias Médicas' }).click();
    await expect(page).toHaveURL(/\/medical-records$/, { timeout: 5000 });
    await expect(page.getByRole('heading', { name: 'Historias Médicas' })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should navigate to user management when clicking User Management link', async ({ page }) => {
    await page.getByRole('link', { name: 'Gestión de Usuarios' }).click();
    await expect(page).toHaveURL(/\/admin\/users$/, { timeout: 5000 });
  }, { timeout: 30000 });

  test('should log out when clicking Logout button', async ({ page }) => {
    await page.getByRole('button', { name: 'Cerrar Sesión' }).click();
    await expect(page).toHaveURL(/\/login$/, { timeout: 5000 });
  }, { timeout: 30000 });

  test('should have working navigation from dashboard', async ({ page }) => {
    const links = page.locator('a');
    const linkCount = await links.count();

    // Should have at least some links
    expect(linkCount).toBeGreaterThanOrEqual(1);
  }, { timeout: 30000 });

  test('should show error if login fails', async ({ page }) => {
    await page.goto(`${frontendURL}/login`, { timeout: 30000, waitUntil: 'domcontentloaded' });

    // Wait for form to be ready
    await expect(page.locator('form')).toBeVisible({ timeout: 5000 });
    
    await page.getByLabel(/nombre de usuario/i).fill('wronguser');
    await page.getByLabel(/contraseña/i).fill('wrongpass');
    await page.getByRole('button', { name: /iniciar sesión|login/i }).click();

    // Wait for button to become enabled again (after error handling)
    await expect(page.getByRole('button', { name: /Iniciar Sesión/ })).not.toBeDisabled({ timeout: 10000 });

    // The error should be visible - pattern matches both Spanish and English errors
    const errorLocator = page.locator('form >> div', { hasText: /Session expired|Invalid|Error/ });
    await expect(errorLocator).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

});
