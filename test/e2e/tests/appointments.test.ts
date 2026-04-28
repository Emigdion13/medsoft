import { test, expect } from '@playwright/test';

const API_BASE = 'http://localhost:8000';

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

test.describe('Appointments CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/username/i).fill('admin');
    await page.getByLabel(/password/i).fill('admin');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/dashboard$/, { timeout: 10000 });
  });

  test('should open and close the new appointment form', async ({ page }) => {
    await page.getByRole('link', { name: 'Appointments', exact: true }).click();
    await expect(page).toHaveURL(/\/appointments$/, { timeout: 5000 });

    // Click "New Appointment" to open the form
    await page.getByRole('button', { name: /new appointment/i }).click();
    await expect(page.getByRole('heading', { name: 'Create Appointment' })).toBeVisible({ timeout: 5000 });

    // Click "Close" to dismiss
    await page.getByRole('button', { name: /close/i }).click();
    await expect(page.getByRole('heading', { name: 'Create Appointment' })).not.toBeVisible({ timeout: 3000 });
  }, { timeout: 30000 });

  test('should display validation errors on empty form submission', async ({ page }) => {
    await page.getByRole('link', { name: 'Appointments', exact: true }).click();
    await expect(page).toHaveURL(/\/appointments$/, { timeout: 5000 });

    // Open the form
    await page.getByRole('button', { name: /new appointment/i }).click();
    await expect(page.getByRole('heading', { name: 'Create Appointment' })).toBeVisible({ timeout: 5000 });

    // Click Create without filling anything
    await page.getByRole('button', { name: /create$/i }).click();

    // Check for validation errors
    await expect(page.getByText(/select a doctor/i, { ignoreCase: true })).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/select a patient/i, { ignoreCase: true })).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/reason is required/i, { ignoreCase: true })).toBeVisible({ timeout: 5000 });
  }, { timeout: 30000 });

  test('should create an appointment via the API and verify it appears in the list', async ({ page }) => {
    await page.getByRole('link', { name: 'Appointments', exact: true }).click();
    await expect(page).toHaveURL(/\/appointments$/, { timeout: 5000 });

    // Get a doctor and patient via the API
    const loginRes = await page.request.post(`${API_BASE}/api/auth/login/`, {
      data: { username: 'admin', password: 'admin' },
    });
    const authData = await loginRes.json();
    const token = (authData as { access: string }).access;

    const doctorsRes = await page.request.get(`${API_BASE}/api/doctors/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const doctorsData = (await doctorsRes.json()) as { results: Array<{ id: string; first_name: string; last_name: string; specialty_main?: { name: string } }> };
    const doctor = doctorsData.results[0];

    const patientsRes = await page.request.get(`${API_BASE}/api/patients/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const patientsData = (await patientsRes.json()) as { results: Array<{ id: string; first_name: string; last_name: string; cedula: string }> };
    const patient = patientsData.results[0];

    test.skip(!doctor || !patient, 'Need at least one doctor and one patient to test');

    // Open the form
    await page.getByRole('button', { name: /new appointment/i }).click();
    await expect(page.getByRole('heading', { name: 'Create Appointment' })).toBeVisible({ timeout: 5000 });

    // Fill in the form
    await page.getByLabel(/doctor/i).selectOption(doctor.id);
    await page.getByLabel(/patient/i).selectOption(patient.id);

    // Set start/end times (start now + 1 hour, end now + 2 hours)
    const start = new Date(Date.now() + 3600000).toISOString().slice(0, 16);
    const end = new Date(Date.now() + 7200000).toISOString().slice(0, 16);
    await page.getByLabel(/start/i).fill(start);
    await page.getByLabel(/end/i).fill(end);

    // Set reason
    await page.getByLabel(/reason/i).fill('Annual checkup');

    // Submit
    await page.getByRole('button', { name: /create$/i }).click();

    // Verify appointment appears in the list
    await expect(page.getByText(patient.first_name, { ignoreCase: true })).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(doctor.first_name, { ignoreCase: true })).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Annual checkup', { ignoreCase: true })).toBeVisible({ timeout: 5000 });
  }, { timeout: 60000 });

  test('should cancel an existing appointment', async ({ page }) => {
    await page.getByRole('link', { name: 'Appointments', exact: true }).click();
    await expect(page).toHaveURL(/\/appointments$/, { timeout: 5000 });

    // Get an appointment via the API
    const loginRes = await page.request.post(`${API_BASE}/api/auth/login/`, {
      data: { username: 'admin', password: 'admin' },
    });
    const authData = await loginRes.json();
    const token = (authData as { access: string }).access;

    const apptsRes = await page.request.get(`${API_BASE}/api/appointments/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const apptsData = (await apptsRes.json()) as { results: Array<{ id: string; status: string }> };
    const appt = apptsData.results.find((a) => a.status !== 'CANCELLED');

    test.skip(!appt, 'Need at least one non-cancelled appointment to test');

    // Click cancel button for the appointment
    await page.getByRole('button', { name: /cancel/i }).first().click();

    // Verify status shows CANCELLED
    await expect(page.getByText('CANCELLED')).toBeVisible({ timeout: 10000 });
  }, { timeout: 60000 });
});
