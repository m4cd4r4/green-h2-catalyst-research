/**
 * 03-tab-pareto-explorer.spec.ts
 *
 * Tests for Tab 1 — Pareto Explorer.
 * All queries use getAppFrame() since Streamlit runs inside an iframe.
 *
 * UI elements:
 *  - "Dataset" radio buttons: "9-Element Optimizer" / "Ca-Mn-W Focused"
 *  - "Max η₁₀ (mV)" slider (200–600, default 400)
 *  - "Max dissolution (µg/cm²/h)" slider (0.01–50, default 10)
 *  - 3 KPI metrics: Best η₁₀, Best Dissolution Rate, Pareto Front Size
 *  - Plotly scatter chart with Pareto Front and IrO₂ benchmark
 */

import { test, expect } from '@playwright/test';
import { waitForStreamlit, isAuthWall, clickTab, captureScreenshot, getAppFrame, getMainHTML } from './helpers';

test.describe('Tab 1 — Pareto Explorer', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
    // Tab 1 is active by default — no need to click
  });

  test('Pareto Explorer heading is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    await expect(
      frame.locator('[data-testid="stMainBlockContainer"]')
    ).toContainText(/Pareto Explorer/i, { timeout: 15_000 });
    await captureScreenshot(page, '03-pareto-explorer');
  });

  test('subtitle text about tradeoff/dissolution is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Tradeoff|lower.*left|dissolution/i, {
      timeout: 10_000,
    });
  });

  test('shows dataset radio buttons or missing-data warning', async ({ page }) => {
    const frame = getAppFrame(page);
    const radioGroup = frame.locator('[data-testid="stRadio"]');
    const warning = frame.locator('[data-testid="stAlert"]');

    const hasRadio = (await radioGroup.count()) > 0;
    const hasWarning = (await warning.count()) > 0;
    expect(hasRadio || hasWarning).toBe(true);
  });

  test('if data loaded: "9-Element Optimizer" radio option exists', async ({ page }) => {
    const frame = getAppFrame(page);
    const radioGroup = frame.locator('[data-testid="stRadio"]').first();
    if ((await radioGroup.count()) === 0) {
      test.skip(true, 'No data loaded');
    }
    await expect(frame.getByText(/9-Element Optimizer/i)).toBeVisible({ timeout: 10_000 });
  });

  test('if data loaded: "Ca-Mn-W Focused" radio option exists', async ({ page }) => {
    const frame = getAppFrame(page);
    const radioGroup = frame.locator('[data-testid="stRadio"]').first();
    if ((await radioGroup.count()) === 0) {
      test.skip(true, 'No data loaded');
    }
    await expect(frame.getByText(/Ca-Mn-W Focused/i)).toBeVisible({ timeout: 10_000 });
  });

  test('if data loaded: Max η₁₀ slider is present', async ({ page }) => {
    const frame = getAppFrame(page);
    const sliders = frame.locator('[data-testid="stSlider"]');
    if ((await sliders.count()) === 0) {
      test.skip(true, 'No data loaded');
    }
    const etaSlider = frame
      .locator('[data-testid="stSlider"]')
      .filter({ hasText: /η₁₀|Max.*mV/i });
    await expect(etaSlider.first()).toBeVisible({ timeout: 10_000 });
  });

  test('if data loaded: Max dissolution slider is present', async ({ page }) => {
    const frame = getAppFrame(page);
    const sliders = frame.locator('[data-testid="stSlider"]');
    if ((await sliders.count()) === 0) {
      test.skip(true, 'No data loaded');
    }
    const dissSlider = frame
      .locator('[data-testid="stSlider"]')
      .filter({ hasText: /dissolution/i });
    await expect(dissSlider.first()).toBeVisible({ timeout: 10_000 });
  });

  test('if data loaded: KPI metric "Best η₁₀ (Pareto)" is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    if ((await frame.locator('[data-testid="stMetric"]').count()) === 0) {
      test.skip(true, 'No data loaded');
    }
    const metricEl = frame
      .locator('[data-testid="stMetric"]')
      .filter({ hasText: /Best η₁₀|Best.*Pareto/i });
    await expect(metricEl.first()).toBeVisible({ timeout: 10_000 });
  });

  test('if data loaded: KPI metric "Best Dissolution Rate" is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    if ((await frame.locator('[data-testid="stMetric"]').count()) === 0) {
      test.skip(true, 'No data loaded');
    }
    const metricEl = frame
      .locator('[data-testid="stMetric"]')
      .filter({ hasText: /Dissolution Rate/i });
    await expect(metricEl.first()).toBeVisible({ timeout: 10_000 });
  });

  test('if data loaded: KPI metric "Pareto Front Size" is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    if ((await frame.locator('[data-testid="stMetric"]').count()) === 0) {
      test.skip(true, 'No data loaded');
    }
    const metricEl = frame
      .locator('[data-testid="stMetric"]')
      .filter({ hasText: /Pareto Front Size/i });
    await expect(metricEl.first()).toBeVisible({ timeout: 10_000 });
  });

  test('shows Plotly chart or missing-data warning', async ({ page }) => {
    const frame = getAppFrame(page);
    // Either a chart or a warning — one of them must be present
    const charts = frame.locator('.js-plotly-plot, [data-testid="stPlotlyChart"]');
    const warnings = frame.locator('[data-testid="stAlert"]');

    const hasChart = (await charts.count()) > 0;
    const hasWarning = (await warnings.count()) > 0;
    expect(hasChart || hasWarning).toBe(true);
  });

  test('if data loaded: Plotly scatter chart is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const charts = frame.locator('.js-plotly-plot, [data-testid="stPlotlyChart"]');
    if ((await charts.count()) === 0) {
      test.skip(true, 'No charts rendered — data may be missing');
    }
    await expect(charts.first()).toBeVisible({ timeout: 15_000 });
  });

  test('if data loaded: switching to Ca-Mn-W updates content', async ({ page }) => {
    const frame = getAppFrame(page);
    const radioGroup = frame.locator('[data-testid="stRadio"]').first();
    if ((await radioGroup.count()) === 0) {
      test.skip(true, 'No data loaded');
    }
    const caMnwOption = frame.getByText(/Ca-Mn-W Focused/i);
    if ((await caMnwOption.count()) === 0) {
      test.skip(true, 'Ca-Mn-W option not present');
    }
    await caMnwOption.click();
    await page.waitForTimeout(2_000);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Ca-Mn-W|Ca.*Mn.*W/i, { timeout: 10_000 });
  });

  test('warning message mentions the correct script name when data missing', async ({ page }) => {
    const frame = getAppFrame(page);
    const alerts = frame.locator('[data-testid="stAlert"]');
    if ((await alerts.count()) === 0) {
      test.skip(true, 'No warnings — data is present');
    }
    const alertText = await alerts.first().innerText();
    expect(alertText).toMatch(/optimizer\.py|\.py|generate/i);
  });
});
