import { test, expect } from '@playwright/test';

test.describe('Example Tests', () => {
  const frontendURL = process.env.TEST_BASE_URL || 'http://localhost:5173';

  test('should display homepage correctly', async ({ page }) => {
    await page.goto(frontendURL);
    
    // Wait for page to load
    await expect(page.locator('html')).toBeVisible();
    
    // Verify title contains MediSoft
    const title = await page.title();
    expect(title.toLowerCase()).toContain('medisoft');
  });

  test('should show health endpoint works', async ({ request }) => {
    const backendURL = process.env.TEST_BACKEND_URL || 'http://localhost:8000';
    const response = await request.get(`${backendURL}/health/`);
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });
});
