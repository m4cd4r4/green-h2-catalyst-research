/**
 * 02-sidebar.spec.ts
 *
 * Tests for the sidebar: branding card, gate script references, target info.
 * All queries use getAppFrame() since Streamlit runs inside an iframe.
 */

import { test, expect } from '@playwright/test';
import { waitForStreamlit, isAuthWall, captureScreenshot, getAppFrame } from './helpers';

test.describe('Sidebar', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
  });

  test('sidebar is visible inside the iframe', async ({ page }) => {
    const frame = getAppFrame(page);
    const sidebar = frame.locator('[data-testid="stSidebar"]');
    await expect(sidebar).toBeVisible({ timeout: 15_000 });
    await captureScreenshot(page, '02-sidebar');
  });

  test('sidebar contains app title "Green H₂ Catalyst"', async ({ page }) => {
    const frame = getAppFrame(page);
    const sidebar = frame.locator('[data-testid="stSidebar"]');
    await expect(sidebar).toContainText(/Green H.*Catalyst/i, { timeout: 10_000 });
  });

  test('sidebar shows Research Dashboard version label', async ({ page }) => {
    const frame = getAppFrame(page);
    const sidebar = frame.locator('[data-testid="stSidebar"]');
    await expect(sidebar).toContainText(/Research Dashboard/i, { timeout: 10_000 });
  });

  test('sidebar lists "Gate Scripts" heading', async ({ page }) => {
    const frame = getAppFrame(page);
    const sidebar = frame.locator('[data-testid="stSidebar"]');
    await expect(sidebar).toContainText(/Gate Scripts/i, { timeout: 10_000 });
  });

  test('sidebar references Gate 1 Synthesis script', async ({ page }) => {
    const frame = getAppFrame(page);
    const sidebar = frame.locator('[data-testid="stSidebar"]');
    await expect(sidebar).toContainText(/Gate 1 Synthesis/i, { timeout: 10_000 });
  });

  test('sidebar references Gate 2 eg Tuning script', async ({ page }) => {
    const frame = getAppFrame(page);
    const sidebar = frame.locator('[data-testid="stSidebar"]');
    await expect(sidebar).toContainText(/Gate 2/i, { timeout: 10_000 });
  });

  test('sidebar references Gate 3 Lifetime script', async ({ page }) => {
    const frame = getAppFrame(page);
    const sidebar = frame.locator('[data-testid="stSidebar"]');
    await expect(sidebar).toContainText(/Gate 3 Lifetime/i, { timeout: 10_000 });
  });

  test('sidebar shows IrO₂ benchmark with η₁₀=250 mV', async ({ page }) => {
    const frame = getAppFrame(page);
    const sidebar = frame.locator('[data-testid="stSidebar"]');
    await expect(sidebar).toContainText(/IrO.*250|250.*mV/i, { timeout: 10_000 });
  });

  test('sidebar shows target overpotential < 300 mV', async ({ page }) => {
    const frame = getAppFrame(page);
    const sidebar = frame.locator('[data-testid="stSidebar"]');
    await expect(sidebar).toContainText(/300.*mV|η.*300/i, { timeout: 10_000 });
  });

  test('sidebar shows D_ss dissolution target', async ({ page }) => {
    const frame = getAppFrame(page);
    const sidebar = frame.locator('[data-testid="stSidebar"]');
    await expect(sidebar).toContainText(/D_ss|dissolution/i, { timeout: 10_000 });
  });

  test('session loaded timestamp is displayed in sidebar', async ({ page }) => {
    const frame = getAppFrame(page);
    const sidebar = frame.locator('[data-testid="stSidebar"]');
    await expect(sidebar).toContainText(/202[5-9]/, { timeout: 10_000 });
  });

  test('sidebar shows the flask/beaker emoji icon (⚗️)', async ({ page }) => {
    const frame = getAppFrame(page);
    const sidebar = frame.locator('[data-testid="stSidebar"]');
    // The sidebar header has ⚗️ Green H₂ Catalyst
    const text = await sidebar.innerText();
    expect(text).toMatch(/⚗️|Green H.*Catalyst/);
  });
});
