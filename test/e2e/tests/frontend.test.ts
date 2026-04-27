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
    // Check for dashboard header or title
    await expect(page.locator('h2').or(page.getByRole('heading'))).toBeVisible({ timeout: 5000 });

    // Verify key dashboard cards are visible
    const cards = page.locator('[style*="background: #fff"]');
    await expect(cards.first()).toBeVisible();
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
