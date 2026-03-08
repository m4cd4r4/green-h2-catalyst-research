/**
 * 06-tab-lifetime-projector.spec.ts
 *
 * Tests for Tab 4 — Lifetime Projector.
 * All queries use getAppFrame() since Streamlit runs inside an iframe.
 *
 * IMPORTANT: The Lifetime Projector only renders its specific metrics
 * (D_ss Pulsed, P50 Pulsed, P50 Continuous) when results_gate3_projection.csv
 * exists. The guard for "data present" is the presence of a [data-testid="stSelectbox"]
 * element in the tab (the composition selector), NOT the generic metrics count.
 */

import { test, expect } from '@playwright/test';
import { waitForStreamlit, isAuthWall, clickTab, captureScreenshot, getAppFrame } from './helpers';

/**
 * Helper: Check if Lifetime Projector data is loaded.
 * Data is loaded when a selectbox (composition selector) is visible.
 */
async function hasLifetimeData(page: any): Promise<boolean> {
  const frame = getAppFrame(page);
  const selectbox = frame.locator('[data-testid="stSelectbox"]');
  return (await selectbox.count()) > 0;
}

test.describe('Tab 4 — Lifetime Projector', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
    await clickTab(page, 'Lifetime Projector');
  });

  test('Lifetime Projector heading is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Lifetime Projector/i, { timeout: 15_000 });
    await captureScreenshot(page, '06-lifetime-projector');
  });

  test('P50 lifetime description text is visible', async ({ page }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/P50 lifetime|median time|dissolution rate/i, {
      timeout: 10_000,
    });
  });

  test('shows composition selectbox or missing-data warning', async ({ page }) => {
    const frame = getAppFrame(page);
    const selectbox = frame.locator('[data-testid="stSelectbox"]');
    const hasSelect = (await selectbox.count()) > 0;
    if (hasSelect) {
      // Data present — selectbox is visible
      await expect(selectbox.first()).toBeVisible({ timeout: 5_000 });
    } else {
      // No data — warning should mention the script to run
      const content = frame.locator('[data-testid="stMainBlockContainer"]');
      await expect(content).toContainText(/gate3_lifetime|Data file not found/i, {
        timeout: 10_000,
      });
    }
  });

  test('if data present: composition selectbox is visible', async ({ page }) => {
    if (!(await hasLifetimeData(page))) {
      test.skip(true, 'No Lifetime Projector data loaded');
    }
    const frame = getAppFrame(page);
    await expect(frame.locator('[data-testid="stSelectbox"]').first()).toBeVisible({
      timeout: 10_000,
    });
  });

  test('if data present: "D_ss Pulsed" metric is visible', async ({ page }) => {
    if (!(await hasLifetimeData(page))) {
      test.skip(true, 'No Lifetime Projector data loaded');
    }
    const frame = getAppFrame(page);
    const metricEl = frame
      .locator('[data-testid="stMetric"]')
      .filter({ hasText: /D_ss Pulsed/i });
    await expect(metricEl.first()).toBeVisible({ timeout: 10_000 });
  });

  test('if data present: "P50 Pulsed (hours)" metric is visible', async ({ page }) => {
    if (!(await hasLifetimeData(page))) {
      test.skip(true, 'No Lifetime Projector data loaded');
    }
    const frame = getAppFrame(page);
    const metricEl = frame
      .locator('[data-testid="stMetric"]')
      .filter({ hasText: /P50 Pulsed/i });
    await expect(metricEl.first()).toBeVisible({ timeout: 10_000 });
  });

  test('if data present: "P50 Continuous (hours)" metric is visible', async ({ page }) => {
    if (!(await hasLifetimeData(page))) {
      test.skip(true, 'No Lifetime Projector data loaded');
    }
    const frame = getAppFrame(page);
    const metricEl = frame
      .locator('[data-testid="stMetric"]')
      .filter({ hasText: /P50 Continuous/i });
    await expect(metricEl.first()).toBeVisible({ timeout: 10_000 });
  });

  test('if data present: Gate 3 GO/NO-GO badge is displayed', async ({ page }) => {
    if (!(await hasLifetimeData(page))) {
      test.skip(true, 'No Lifetime Projector data loaded');
    }
    const frame = getAppFrame(page);
    const html = await frame
      .locator('[data-testid="stMainBlockContainer"]')
      .innerHTML();
    expect(/badge-go|badge-nogo|GATE 3.*GO|GATE 3.*NO-GO/.test(html)).toBe(true);
  });

  test('if data present: "1 MW stack" informational text is visible', async ({ page }) => {
    if (!(await hasLifetimeData(page))) {
      test.skip(true, 'No Lifetime Projector data loaded');
    }
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/1 MW|1MW|megawatt/i, { timeout: 10_000 });
  });

  test('if data present: P50 > 20,000 h context text is visible', async ({ page }) => {
    if (!(await hasLifetimeData(page))) {
      test.skip(true, 'No Lifetime Projector data loaded');
    }
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/20.000|20,000/, { timeout: 10_000 });
  });

  test('if data present: P50 > 50,000 h IrO₂ comparison text is visible', async ({
    page,
  }) => {
    if (!(await hasLifetimeData(page))) {
      test.skip(true, 'No Lifetime Projector data loaded');
    }
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/50.000|50,000/, { timeout: 10_000 });
  });

  test('if data present: P50 bar chart is rendered', async ({ page }) => {
    if (!(await hasLifetimeData(page))) {
      test.skip(true, 'No Lifetime Projector data loaded');
    }
    const frame = getAppFrame(page);
    // Wait for the selectbox to be fully visible before asserting the chart —
    // hasLifetimeData may return true before the right-column chart has rendered
    await expect(frame.locator('[data-testid="stSelectbox"]').first()).toBeVisible({ timeout: 15_000 });
    const charts = frame.locator('.js-plotly-plot, [data-testid="stPlotlyChart"]');
    await expect(charts.first()).toBeVisible({ timeout: 20_000 });
  });

  test('if data present: data table is rendered', async ({ page }) => {
    if (!(await hasLifetimeData(page))) {
      test.skip(true, 'No Lifetime Projector data loaded');
    }
    const frame = getAppFrame(page);
    await expect(frame.locator('[data-testid="stSelectbox"]').first()).toBeVisible({ timeout: 15_000 });
    // Accept both legacy and newer Streamlit dataframe testids
    const tables = frame.locator('[data-testid="stDataFrame"], [data-testid="stDataFrameResizable"]');
    await expect(tables.first()).toBeVisible({ timeout: 15_000 });
  });

  test('shows data or missing-data warning referencing gate3_lifetime script', async ({
    page,
  }) => {
    const frame = getAppFrame(page);
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    // Either data is loaded (selectbox visible) or the warning about the script is shown
    const hasData = await hasLifetimeData(page);
    if (hasData) {
      // Data present — selectbox visible
      await expect(frame.locator('[data-testid="stSelectbox"]').first()).toBeVisible({
        timeout: 5_000,
      });
    } else {
      // No data — warning with script name should be shown
      await expect(content).toContainText(/gate3_lifetime|\.py|first/i, {
        timeout: 10_000,
      });
    }
  });
});
