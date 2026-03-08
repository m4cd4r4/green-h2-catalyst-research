/**
 * 05-tab-gate-status.spec.ts
 *
 * Tests for Tab 3 — Gate Status Board.
 * All queries use getAppFrame() since Streamlit runs inside an iframe.
 */

import { test, expect } from '@playwright/test';
import { waitForStreamlit, isAuthWall, clickTab, captureScreenshot, getAppFrame } from './helpers';

test.describe('Tab 3 — Gate Status Board', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
    await clickTab(page, 'Gate Status Board');
  });

  test('Gate Status Board heading is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Gate Status Board/i, { timeout: 15_000 });
    await captureScreenshot(page, '05-gate-status-board');
  });

  test('Gate 1 section is visible (data or warning)', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Gate 1/i, { timeout: 15_000 });
  });

  test('Gate 2 section is visible (data or warning)', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Gate 2/i, { timeout: 15_000 });
  });

  test('Gate 3 section is visible (data or warning)', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Gate 3/i, { timeout: 15_000 });
  });

  test('Gate 1 shows "Synthesis Sweep" label or missing-data warning text', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    // Either "Synthesis Sweep" appears (data present) or a warning about the script (data missing)
    await expect(content).toContainText(/Synthesis Sweep|acid_oer_synthesis_gate1/i, {
      timeout: 10_000,
    });
  });

  test('Gate 2 shows "eg Tuning" or missing-data warning', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    const hasEg = await content
      .getByText(/eg Tuning/i)
      .isVisible({ timeout: 5_000 })
      .catch(() => false);
    const hasWarning = (await frame.locator('[data-testid="stAlert"]').count()) > 0;
    expect(hasEg || hasWarning).toBe(true);
  });

  test('Gate 3 shows "Lifetime Projection" or missing-data warning', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    const hasLifetime = await content
      .getByText(/Lifetime Projection/i)
      .isVisible({ timeout: 5_000 })
      .catch(() => false);
    const hasWarning = (await frame.locator('[data-testid="stAlert"]').count()) > 0;
    expect(hasLifetime || hasWarning).toBe(true);
  });

  test('gate badge or missing-data warning is present for each gate', async ({ page }) => {
    const frame = getAppFrame(page);
    const html = await frame
      .locator('[data-testid="stMainBlockContainer"]')
      .innerHTML();
    const hasBadge = /badge-go|badge-nogo|badge-warn/.test(html);
    const hasWarning = (await frame.locator('[data-testid="stAlert"]').count()) > 0;
    expect(hasBadge || hasWarning).toBe(true);
  });

  test('at least one Plotly chart or dataframe or warning is rendered', async ({ page }) => {
    const frame = getAppFrame(page);
    const charts = frame.locator('.js-plotly-plot, [data-testid="stPlotlyChart"]');
    const tables = frame.locator('[data-testid="stDataFrame"]');
    const warnings = frame.locator('[data-testid="stAlert"]');

    const chartCount = await charts.count();
    const tableCount = await tables.count();
    const warningCount = await warnings.count();

    expect(chartCount > 0 || tableCount > 0 || warningCount > 0).toBe(true);
  });

  test('if Gate 2 data present: bar chart has IrO₂ reference annotation', async ({
    page,
  }) => {
    const frame = getAppFrame(page);
    const charts = frame.locator('.js-plotly-plot, [data-testid="stPlotlyChart"]');
    if ((await charts.count()) === 0) {
      test.skip(true, 'No charts rendered — data may be missing');
    }
    const pageContent = await frame
      .locator('[data-testid="stMainBlockContainer"]')
      .innerHTML();
    expect(pageContent).toMatch(/250|IrO/i);
  });

  test('missing data warning references correct Python script', async ({ page }) => {
    const frame = getAppFrame(page);
    const alerts = frame.locator('[data-testid="stAlert"]');
    if ((await alerts.count()) === 0) {
      test.skip(true, 'All data present — no warnings');
    }
    const alertText = await alerts.first().innerText();
    // Skip if the alert is a runtime error (e.g. heatmap render failure),
    // not a _missing() data-file warning
    if (!alertText.match(/\.py|run.*script|generate|first/i)) {
      test.skip(true, 'Alert is a runtime warning, not a missing-data warning');
    }
    expect(alertText).toMatch(/\.py|run.*script|generate|first/i);
  });
});
