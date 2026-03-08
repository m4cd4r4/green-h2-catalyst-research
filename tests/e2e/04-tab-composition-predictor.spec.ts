/**
 * 04-tab-composition-predictor.spec.ts
 *
 * Tests for Tab 2 — Composition Predictor.
 *
 * This tab is purely reactive (no CSV dependency) — it always renders.
 * All queries use getAppFrame() since Streamlit runs inside an iframe.
 *
 * UI elements:
 *  - 4 element sliders: Ca (%), Mn (%), W (%), Ti (%)
 *  - Total validation: error if >100, info if <100, success if =100
 *  - 4 predicted-property metrics: CaWO₄ Fraction, E_diss (eV), eg Estimate, η₁₀ Estimate (mV)
 *  - Gate 1/2/3 traffic-light cards (GO / MARGINAL / NO-GO)
 *  - Volcano curve Plotly chart
 *  - Synthesis Recommendation glass card
 */

import { test, expect } from '@playwright/test';
import { waitForStreamlit, isAuthWall, clickTab, captureScreenshot, getAppFrame } from './helpers';

test.describe('Tab 2 — Composition Predictor (structure)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
    await clickTab(page, 'Composition Predictor');
  });

  test('Composition Predictor heading is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Composition Predictor/i, { timeout: 15_000 });
    await captureScreenshot(page, '04-composition-predictor');
  });

  test('subtitle about adjusting element fractions is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Adjust element fractions/i, { timeout: 10_000 });
  });

  test('"Element Fractions" sub-heading is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    // Use exact match to avoid strict-mode violation (subtitle also contains "element fractions")
    await expect(
      frame.getByText('Element Fractions', { exact: true })
    ).toBeVisible({ timeout: 10_000 });
  });

  test('Ca (%) slider is present', async ({ page }) => {
    const frame = getAppFrame(page);
    const caSlider = frame
      .locator('[data-testid="stSlider"]')
      .filter({ hasText: /\bCa\b.*%/i });
    await expect(caSlider.first()).toBeVisible({ timeout: 10_000 });
  });

  test('Mn (%) slider is present', async ({ page }) => {
    const frame = getAppFrame(page);
    const mnSlider = frame
      .locator('[data-testid="stSlider"]')
      .filter({ hasText: /\bMn\b.*%/i });
    await expect(mnSlider.first()).toBeVisible({ timeout: 10_000 });
  });

  test('W (%) slider is present', async ({ page }) => {
    const frame = getAppFrame(page);
    const wSlider = frame
      .locator('[data-testid="stSlider"]')
      .filter({ hasText: /\bW\b.*%/i });
    await expect(wSlider.first()).toBeVisible({ timeout: 10_000 });
  });

  test('Ti (%) slider is present', async ({ page }) => {
    const frame = getAppFrame(page);
    const tiSlider = frame
      .locator('[data-testid="stSlider"]')
      .filter({ hasText: /\bTi\b.*%/i });
    await expect(tiSlider.first()).toBeVisible({ timeout: 10_000 });
  });

  test('exactly 4 element sliders are visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const sliders = frame.locator('[data-testid="stSlider"]');
    const count = await sliders.count();
    expect(count).toBe(4);
  });

  test('a total-percentage message is displayed', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    // Default: Ca=11+Mn=55+W=34+Ti=0=100 → "Total = 100% ✓"
    await expect(content).toContainText(/Total.*100|100.*Total|100.*%/i, { timeout: 10_000 });
  });

  test('"Predicted Properties" sub-heading is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    await expect(
      frame.getByText(/Predicted Properties/i)
    ).toBeVisible({ timeout: 10_000 });
  });

  test('"CaWO₄ Fraction" metric is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const metric = frame
      .locator('[data-testid="stMetric"]')
      .filter({ hasText: /CaWO.*Fraction/i });
    await expect(metric.first()).toBeVisible({ timeout: 10_000 });
  });

  test('"Composite E_diss" metric is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const metric = frame
      .locator('[data-testid="stMetric"]')
      .filter({ hasText: /E_diss|Composite/i });
    await expect(metric.first()).toBeVisible({ timeout: 10_000 });
  });

  test('"eg Estimate" metric is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const metric = frame
      .locator('[data-testid="stMetric"]')
      .filter({ hasText: /eg Estimate/i });
    await expect(metric.first()).toBeVisible({ timeout: 10_000 });
  });

  test('"η₁₀ Estimate" metric is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const metric = frame
      .locator('[data-testid="stMetric"]')
      .filter({ hasText: /η₁₀ Estimate/i });
    await expect(metric.first()).toBeVisible({ timeout: 10_000 });
  });

  test('"Gate Traffic Lights" section heading is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    await expect(
      frame.getByText(/Gate Traffic Lights/i)
    ).toBeVisible({ timeout: 10_000 });
  });

  test('Gate 1 — Synthesis card is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Gate 1.*Synthesis/i, { timeout: 10_000 });
  });

  test('Gate 2 — eg Tuning card is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Gate 2.*eg Tuning/i, { timeout: 10_000 });
  });

  test('Gate 3 — Activity card is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Gate 3.*Activity/i, { timeout: 10_000 });
  });

  test('Gate 2 shows target range (0.45–0.59)', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/0\.45.*0\.59|target.*0\.45/i, { timeout: 10_000 });
  });

  test('at least one gate badge (GO/MARGINAL/NO-GO) is rendered', async ({ page }) => {
    const frame = getAppFrame(page);
    const pageHtml = await frame
      .locator('[data-testid="stMainBlockContainer"]')
      .innerHTML();
    const hasBadge = /badge-go|badge-nogo|badge-warn|>\s*(GO|NO-GO|MARGINAL)\s*</.test(pageHtml);
    expect(hasBadge).toBe(true);
  });

  test('Volcano Curve Plotly chart is rendered', async ({ page }) => {
    const frame = getAppFrame(page);
    const charts = frame.locator('.js-plotly-plot, [data-testid="stPlotlyChart"]');
    await expect(charts.first()).toBeVisible({ timeout: 15_000 });
  });

  test('volcano chart title "Volcano Curve" appears in page', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = await frame
      .locator('[data-testid="stMainBlockContainer"]')
      .innerHTML();
    expect(content).toMatch(/Volcano Curve|Volcano.*η₁₀/i);
  });

  test('"Synthesis Recommendation" section heading is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    await expect(
      frame.getByText(/Synthesis Recommendation/i)
    ).toBeVisible({ timeout: 10_000 });
  });

  test('synthesis recommendation mentions a synthesis method', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    // With default Ca+W values → co-precipitation text
    await expect(content).toContainText(/precipitation|hydrothermal|sol-gel|anneal|Calcination/i, {
      timeout: 10_000,
    });
  });
});

test.describe('Tab 2 — Composition Predictor (metric values)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
    await clickTab(page, 'Composition Predictor');
  });

  test('CaWO₄ fraction metric value is a percentage', async ({ page }) => {
    const frame = getAppFrame(page);
    const metric = frame
      .locator('[data-testid="stMetric"]')
      .filter({ hasText: /CaWO.*Fraction/i });
    const valueEl = metric.first().locator('[data-testid="stMetricValue"]');
    const valueText = await valueEl.innerText({ timeout: 10_000 });
    expect(valueText).toMatch(/\d+(\.\d+)?%/);
  });

  test('eg Estimate metric value is a decimal number (3 decimal places)', async ({
    page,
  }) => {
    const frame = getAppFrame(page);
    const metric = frame
      .locator('[data-testid="stMetric"]')
      .filter({ hasText: /eg Estimate/i });
    const valueEl = metric.first().locator('[data-testid="stMetricValue"]');
    const valueText = await valueEl.innerText({ timeout: 10_000 });
    expect(valueText).toMatch(/\d+\.\d{3}/);
  });

  test('η₁₀ Estimate metric value ends in "mV"', async ({ page }) => {
    const frame = getAppFrame(page);
    const metric = frame
      .locator('[data-testid="stMetric"]')
      .filter({ hasText: /η₁₀ Estimate/i });
    const valueEl = metric.first().locator('[data-testid="stMetricValue"]');
    const valueText = await valueEl.innerText({ timeout: 10_000 });
    expect(valueText).toMatch(/\d+(\.\d+)?\s*mV/i);
  });

  test('E_diss metric value is a decimal number', async ({ page }) => {
    const frame = getAppFrame(page);
    const metric = frame
      .locator('[data-testid="stMetric"]')
      .filter({ hasText: /E_diss|Composite/i });
    const valueEl = metric.first().locator('[data-testid="stMetricValue"]');
    const valueText = await valueEl.innerText({ timeout: 10_000 });
    // The metric label says "(eV)" but the value is just the number e.g. "1.909"
    expect(valueText).toMatch(/\d+\.\d+/);
    // Value should be in physically reasonable eV range (0.5 to 2.5 eV)
    const num = parseFloat(valueText);
    expect(num).toBeGreaterThan(0.5);
    expect(num).toBeLessThan(2.5);
  });

  test('η₁₀ Estimate is a plausible overpotential (200–700 mV range)', async ({ page }) => {
    const frame = getAppFrame(page);
    const metric = frame
      .locator('[data-testid="stMetric"]')
      .filter({ hasText: /η₁₀ Estimate/i });
    const valueEl = metric.first().locator('[data-testid="stMetricValue"]');
    const valueText = await valueEl.innerText({ timeout: 10_000 });
    const numMatch = valueText.match(/(\d+(\.\d+)?)/);
    if (numMatch) {
      const val = parseFloat(numMatch[1]);
      expect(val).toBeGreaterThanOrEqual(200);
      expect(val).toBeLessThanOrEqual(700);
    }
  });
});
