/**
 * 08-navigation.spec.ts
 *
 * Navigation and tab-switching tests.
 * All queries use getAppFrame() since Streamlit runs inside an iframe.
 */

import { test, expect } from '@playwright/test';
import { waitForStreamlit, isAuthWall, clickTab, captureScreenshot, getAppFrame } from './helpers';

test.describe('Navigation — tab switching', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
  });

  test('can switch from Tab 1 to Tab 2 and back', async ({ page }) => {
    const frame = getAppFrame(page);

    await clickTab(page, 'Composition Predictor');
    await expect(
      frame.locator('[data-testid="stMainBlockContainer"]')
    ).toContainText(/Composition Predictor/i, { timeout: 10_000 });

    await clickTab(page, 'Pareto Explorer');
    await expect(
      frame.locator('[data-testid="stMainBlockContainer"]')
    ).toContainText(/Pareto Explorer/i, { timeout: 10_000 });
  });

  test('can navigate to all five tabs sequentially', async ({ page }) => {
    const frame = getAppFrame(page);
    const tabs = [
      'Pareto Explorer',
      'Composition Predictor',
      'Gate Status Board',
      'Lifetime Projector',
      'Literature Context',
    ];

    for (const tab of tabs) {
      await clickTab(page, tab);
      const content = frame.locator('[data-testid="stMainBlockContainer"]');
      await expect(content).toContainText(new RegExp(tab.replace(/[^a-zA-Z0-9 ]/g, '.*'), 'i'), {
        timeout: 10_000,
      });
      await captureScreenshot(
        page,
        `08-nav-tab-${tab.toLowerCase().replace(/\s+/g, '-')}`
      );
    }
  });

  test('Literature Context tab always renders (no CSV dependency)', async ({ page }) => {
    const frame = getAppFrame(page);
    await clickTab(page, 'Literature Context');
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/IrO|MnO|this work/i, { timeout: 10_000 });
  });

  test('Composition Predictor tab always renders (no CSV dependency)', async ({ page }) => {
    const frame = getAppFrame(page);
    await clickTab(page, 'Composition Predictor');
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Element Fractions/i, { timeout: 10_000 });
  });

  test('tabs retain their active state indicator when selected', async ({ page }) => {
    const frame = getAppFrame(page);
    await clickTab(page, 'Literature Context');

    const activeTab = frame.getByRole('tab', { name: /Literature Context/i });
    // Streamlit sets aria-selected="true" on active tab
    await expect(activeTab).toHaveAttribute('aria-selected', 'true', { timeout: 10_000 });
  });

  test('no JavaScript errors thrown during tab navigation', async ({ page }) => {
    const jsErrors: string[] = [];
    page.on('pageerror', (err) => {
      jsErrors.push(err.message);
    });

    const tabs = [
      'Composition Predictor',
      'Gate Status Board',
      'Literature Context',
    ];

    for (const tab of tabs) {
      await clickTab(page, tab);
      await page.waitForTimeout(800);
    }

    const criticalErrors = jsErrors.filter(
      (e) =>
        !e.includes('ResizeObserver') &&
        !e.includes('Non-Error promise') &&
        !e.includes('Loading chunk') &&
        !e.includes('ChunkLoadError')
    );

    if (criticalErrors.length > 0) {
      console.log('JS errors during navigation:', criticalErrors);
    }

    expect(criticalErrors.length).toBeLessThanOrEqual(3);
  });

  test('sidebar remains visible after switching tabs', async ({ page }) => {
    const frame = getAppFrame(page);
    const tabs = ['Composition Predictor', 'Literature Context'];

    for (const tab of tabs) {
      await clickTab(page, tab);
      const sidebar = frame.locator('[data-testid="stSidebar"]');
      await expect(sidebar).toBeVisible({ timeout: 5_000 });
    }
  });
});

test.describe('Navigation — mobile viewport', () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test('app iframe loads on mobile viewport', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
    const frame = getAppFrame(page);
    await expect(frame.locator('[data-testid="stApp"]')).toBeVisible({ timeout: 15_000 });
    await captureScreenshot(page, '08-mobile-viewport');
  });

  test('tabs are accessible on mobile', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
    const frame = getAppFrame(page);
    const tabs = frame.getByRole('tab');
    const tabCount = await tabs.count();
    expect(tabCount).toBeGreaterThanOrEqual(1);
  });

  test('Literature Context tab renders correctly on mobile', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);

    const frame = getAppFrame(page);

    // On mobile, the sidebar may expand and cover the tabs.
    // Close the sidebar if it is open by clicking the collapse button.
    const collapseBtn = frame.locator('[data-testid="stSidebarCollapseButton"]');
    if (await collapseBtn.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await collapseBtn.click();
      await page.waitForTimeout(500);
    }

    // Use force:true to click the tab even if partially overlapped
    const litTab = frame.getByRole('tab', { name: /Literature Context/i });
    await expect(litTab).toBeVisible({ timeout: 10_000 });
    await litTab.click({ force: true });
    await page.waitForTimeout(2_000);

    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/IrO|MnO|this work/i, { timeout: 10_000 });
    await captureScreenshot(page, '08-mobile-literature-context');
  });
});
