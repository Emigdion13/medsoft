import { chromium } from 'playwright';

const run = async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.goto('http://medisoft-frontend:80/login');
  
  console.log('Page title:', await page.title());
  
  // Wait for React to mount
  await new Promise(r => setTimeout(r, 3000));
  
  // Try to find the form elements
  try {
    const usernameField = await page.locator('#username').waitFor({ timeout: 5000 });
    console.log('Username field found');
    
    await usernameField.fill('admin');
    console.log('Filled username');
    
    const passwordField = await page.locator('#password').waitFor({ timeout: 5000 });
    console.log('Password field found');
    
    await passwordField.fill('admin');
    console.log('Filled password');
    
    const button = await page.getByRole('button', { name: /sign in/i }).waitFor({ timeout: 5000 });
    console.log('Button found');
    
    await button.click();
    console.log('Clicked button');
    
    // Wait for navigation
    await page.waitForURL(/dashboard/, { timeout: 10000 });
    console.log('Navigation complete, current URL:', page.url());
  } catch (err) {
    console.error('Error:', err.message);
    const screenshot = await page.screenshot();
    require('fs').writeFileSync('/tmp/screenshot.png', screenshot);
    console.log('Screenshot saved to /tmp/screenshot.png');
  }
  
  await browser.close();
};

run().catch(console.error);
