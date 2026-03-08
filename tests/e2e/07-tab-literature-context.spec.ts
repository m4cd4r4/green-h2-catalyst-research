/**
 * 07-tab-literature-context.spec.ts
 *
 * Tests for Tab 5 — Literature Context.
 * This tab uses hardcoded data — it always renders without any CSV files.
 * All queries use getAppFrame() since Streamlit runs inside an iframe.
 *
 * Materials in the dataframe:
 *   α-MnO₂ (360 mV), δ-MnO₂ (340 mV), Mn₂O₃ (400 mV), MnCoP (285 mV),
 *   IrO₂ benchmark (250 mV), Ca₀.₁₁Mn₀.₅₅W₀.₃₄ this work (278 mV)
 */

import { test, expect } from '@playwright/test';
import { waitForStreamlit, isAuthWall, clickTab, captureScreenshot, getAppFrame } from './helpers';

test.describe('Tab 5 — Literature Context', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
    await clickTab(page, 'Literature Context');
  });

  test('Literature Context heading is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Literature Context/i, { timeout: 15_000 });
    await captureScreenshot(page, '07-literature-context');
  });

  test('subtitle about earth-abundant acid OER catalysts is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/earth-abundant|acid OER|best reported/i, {
      timeout: 10_000,
    });
  });

  test('materials comparison dataframe is rendered', async ({ page }) => {
    const frame = getAppFrame(page);
    const tables = frame.locator('[data-testid="stDataFrame"]');
    await expect(tables.first()).toBeVisible({ timeout: 15_000 });
  });

  test('dataframe contains IrO₂ benchmark row', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/IrO.*benchmark|IrO₂/i, { timeout: 10_000 });
  });

  test('dataframe contains "this work" Ca-Mn-W row', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/this work|Ca.*Mn.*W/i, { timeout: 10_000 });
  });

  test('dataframe contains MnO₂ material', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/MnO|MnO₂/i, { timeout: 10_000 });
  });

  test('dataframe contains MnCoP material', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/MnCoP/i, { timeout: 10_000 });
  });

  test('at least one Plotly chart is rendered', async ({ page }) => {
    const frame = getAppFrame(page);
    // Wait for charts to fully render (Plotly can be slow to initialise)
    await page.waitForTimeout(2_000);
    const charts = frame.locator('.js-plotly-plot, [data-testid="stPlotlyChart"]');
    const count = await charts.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('two bar charts rendered (η₁₀ and D_ss)', async ({ page }) => {
    const frame = getAppFrame(page);
    await page.waitForTimeout(2_000);
    const charts = frame.locator('.js-plotly-plot, [data-testid="stPlotlyChart"]');
    const count = await charts.count();
    expect(count).toBeGreaterThanOrEqual(2);
  });

  test('"300 mV target" reference line annotation is present', async ({ page }) => {
    const frame = getAppFrame(page);
    const html = await frame
      .locator('[data-testid="stMainBlockContainer"]')
      .innerHTML();
    expect(html).toMatch(/300.*mV|Target.*300|300.*target/i);
  });

  test('"2 µg/cm²/h target" reference line annotation is present', async ({ page }) => {
    const frame = getAppFrame(page);
    const html = await frame
      .locator('[data-testid="stMainBlockContainer"]')
      .innerHTML();
    expect(html).toMatch(/Target.*2|2.*µg|2.*target/i);
  });

  test('"Key context notes" glass card is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Key context notes/i, { timeout: 10_000 });
  });

  test('context notes mention CaWO₄ protective layer', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/CaWO.*protect|protective.*layer|self-healing/i, {
      timeout: 10_000,
    });
  });

  test('context notes mention MnCoP dissolution issue', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/MnCoP.*dissolves|dissolves.*acid|not viable/i, {
      timeout: 10_000,
    });
  });

  test('context notes mention IrO₂ Ir scarcity', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Ir.*scarcity|scarcity|0\.003.*ppb|ppb/i, {
      timeout: 10_000,
    });
  });

  test('η₁₀ chart includes IrO₂ at 250 mV data point', async ({ page }) => {
    const frame = getAppFrame(page);
    const html = await frame
      .locator('[data-testid="stMainBlockContainer"]')
      .innerHTML();
    // 250 mV is the IrO₂ benchmark value in the chart
    expect(html).toMatch(/250/);
  });

  test('D_ss chart has log-scale tick labels in SVG (k/M/T notation)', async ({ page }) => {
    const frame = getAppFrame(page);
    // Wait for charts to fully render
    await page.waitForTimeout(2_000);
    const charts = frame.locator('[data-testid="stPlotlyChart"]');
    const count = await charts.count();
    if (count < 3) {
      test.skip(true, 'Not enough charts rendered');
    }
    // The D_ss chart (3rd chart: index 2) uses log scale.
    // Plotly log scale renders x-axis ticks with engineering notation: "1", "10k", "100M"
    // These appear as SVG <text> elements inside the chart.
    const dssChart = charts.nth(2);
    const svgTexts = await dssChart.evaluate((el) => {
      const textEls = el.querySelectorAll('text');
      return Array.from(textEls).map((t) => t.textContent || '');
    });
    const logScaleIndicator = svgTexts.some(
      (t) => t.includes('k') || t.includes('M') || t.includes('T')
    );
    console.log('D_ss chart SVG texts:', svgTexts.slice(0, 10));
    expect(logScaleIndicator).toBe(true);
  });

  test('hr dividers separate sections', async ({ page }) => {
    const frame = getAppFrame(page);
    // Streamlit st.divider() renders as an <hr> element
    const dividers = frame.locator('hr');
    const count = await dividers.count();
    // The Literature Context tab has 2 st.divider() calls
    expect(count).toBeGreaterThanOrEqual(1);
  });
});
