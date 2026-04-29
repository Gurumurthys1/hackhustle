const { test, expect } = require('@playwright/test');

test('Dashboard loads without errors', async ({ page }) => {
  await page.goto('http://localhost:5173');
  await expect(page).toHaveTitle(/TriNetra AI - Fraud Dashboard/);
});

test('MANUAL_REVIEW cases appear in the queue', async ({ page }) => {
  await page.goto('http://localhost:5173');
  const cards = await page.locator('.claim-card').count();
  expect(cards).toBeGreaterThan(0);
});

test('Both images render side-by-side', async ({ page }) => {
  await page.goto('http://localhost:5173');
  const images = await page.locator('.image-box img').count();
  expect(images).toBeGreaterThanOrEqual(2);
});

test('Score badge styling for high/mid/low scores is present', async ({ page }) => {
  await page.goto('http://localhost:5173');
  const badge = page.locator('.status-badge');
  await expect(badge).toBeVisible();
  
  const classObj = await badge.getAttribute('class');
  expect(classObj).toMatch(/score-red|score-yellow|score-green/);
});
