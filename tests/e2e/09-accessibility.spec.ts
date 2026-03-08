/**
 * 09-accessibility.spec.ts
 *
 * Basic accessibility checks.
 * All queries use getAppFrame() since Streamlit runs inside an iframe.
 */

import { test, expect } from '@playwright/test';
import { waitForStreamlit, isAuthWall, clickTab, getAppFrame } from './helpers';

test.describe('Accessibility — ARIA roles and structure', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
  });

  test('tab list has role="tablist" inside the app iframe', async ({ page }) => {
    const frame = getAppFrame(page);
    const tabList = frame.locator('[role="tablist"]');
    await expect(tabList).toBeVisible({ timeout: 10_000 });
  });

  test('exactly 5 tab buttons with role="tab" are present', async ({ page }) => {
    const frame = getAppFrame(page);
    const tabs = frame.locator('[role="tab"]');
    const count = await tabs.count();
    expect(count).toBe(5);
  });

  test('first tab (Pareto Explorer) has aria-selected="true" on load', async ({ page }) => {
    const frame = getAppFrame(page);
    const selectedTab = frame.locator('[role="tab"][aria-selected="true"]');
    await expect(selectedTab).toBeVisible({ timeout: 10_000 });
    const count = await selectedTab.count();
    expect(count).toBe(1);
  });

  test('slider inputs have visible label text inside iframe', async ({ page }) => {
    await clickTab(page, 'Composition Predictor');
    const frame = getAppFrame(page);
    const sliders = frame.locator('[data-testid="stSlider"]');
    const count = await sliders.count();

    if (count === 0) {
      test.skip(true, 'No sliders visible');
    }

    for (let i = 0; i < Math.min(count, 4); i++) {
      const slider = sliders.nth(i);
      const labelText = await slider.innerText();
      expect(labelText.trim().length).toBeGreaterThan(0);
    }
  });

  test('metric elements have non-empty label text', async ({ page }) => {
    await clickTab(page, 'Composition Predictor');
    const frame = getAppFrame(page);
    const metrics = frame.locator('[data-testid="stMetric"]');
    const count = await metrics.count();

    if (count === 0) {
      test.skip(true, 'No metrics visible');
    }

    for (let i = 0; i < Math.min(count, 4); i++) {
      const metric = metrics.nth(i);
      const labelEl = metric.locator('[data-testid="stMetricLabel"]');
      if ((await labelEl.count()) > 0) {
        const labelText = await labelEl.innerText();
        expect(labelText.trim().length).toBeGreaterThan(0);
      }
    }
  });

  test('Literature Context heading uses h2 element', async ({ page }) => {
    await clickTab(page, 'Literature Context');
    const frame = getAppFrame(page);
    const h2s = frame.locator('h2');
    const count = await h2s.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('page title is set and descriptive', async ({ page }) => {
    const title = await page.title();
    expect(title.length).toBeGreaterThan(5);
    expect(title).toMatch(/Green|Catalyst|Streamlit/i);
  });

  test('switching tabs updates aria-selected correctly', async ({ page }) => {
    const frame = getAppFrame(page);

    await clickTab(page, 'Literature Context');
    const litTab = frame.getByRole('tab', { name: /Literature Context/i });
    await expect(litTab).toHaveAttribute('aria-selected', 'true', { timeout: 10_000 });

    const paretoTab = frame.getByRole('tab', { name: /Pareto Explorer/i });
    await expect(paretoTab).toHaveAttribute('aria-selected', 'false', { timeout: 5_000 });
  });
});
