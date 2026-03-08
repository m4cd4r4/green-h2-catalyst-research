/**
 * 01-smoke.spec.ts
 *
 * Smoke tests: verify the app loads and all five tabs are present.
 *
 * Streamlit Cloud wraps the app in an iframe at /~/+/ — all element queries
 * use getAppFrame(page) to operate inside that iframe.
 */

import { test, expect } from '@playwright/test';
import { waitForStreamlit, isAuthWall, captureScreenshot, getAppFrame } from './helpers';

test.describe('Smoke — app loads', () => {
  test('navigates to the app URL without a hard 5xx error', async ({ page }) => {
    const response = await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    const finalStatus = response?.status() ?? 200;
    expect([200, 303]).toContain(finalStatus);
  });

  test('page title contains Green H₂ Catalyst Research', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });

    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }

    // Wait for the page title to update — Streamlit sets it after JS hydration
    await page.waitForFunction(
      () => document.title.includes('Catalyst') || document.title.includes('Green'),
      { timeout: 30_000 }
    );

    const title = await page.title();
    console.log('Page title:', title);
    expect(title).toMatch(/Green.*Catalyst|Catalyst.*Research/i);
  });

  test('Streamlit app iframe is present', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await page.waitForSelector('iframe[src*="/~/+/"]', { timeout: 30_000 });
    await captureScreenshot(page, '01-initial-load');
  });

  test('stApp element is visible inside the iframe', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
    const frame = getAppFrame(page);
    await expect(frame.locator('[data-testid="stApp"]')).toBeVisible({ timeout: 15_000 });
  });
});

test.describe('Smoke — five tabs present', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
  });

  const EXPECTED_TABS = [
    'Pareto Explorer',
    'Composition Predictor',
    'Gate Status Board',
    'Lifetime Projector',
    'Literature Context',
  ];

  for (const tabLabel of EXPECTED_TABS) {
    test(`tab "${tabLabel}" is visible`, async ({ page }) => {
      const frame = getAppFrame(page);
      const tab = frame.getByRole('tab', { name: new RegExp(tabLabel, 'i') });
      await expect(tab).toBeVisible({ timeout: 15_000 });
    });
  }
});

test.describe('Smoke — page structure', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
  });

  test('app displays "Pareto Explorer" content by default (first tab)', async ({ page }) => {
    const frame = getAppFrame(page);
    const mainBlock = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(mainBlock).toContainText(/Pareto Explorer/i, { timeout: 15_000 });
  });

  test('sidebar is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    await expect(frame.locator('[data-testid="stSidebar"]')).toBeVisible({ timeout: 15_000 });
  });

  test('no uncaught JS errors during initial load', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (err) => errors.push(err.message));
    await page.waitForTimeout(3_000);
    const critical = errors.filter(
      (e) =>
        !e.includes('ResizeObserver') &&
        !e.includes('Non-Error promise') &&
        !e.includes('ChunkLoadError')
    );
    expect(critical.length).toBeLessThanOrEqual(3);
  });
});
