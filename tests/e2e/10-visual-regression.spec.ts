/**
 * 10-visual-regression.spec.ts
 *
 * Visual regression: captures screenshots of each tab.
 * All queries use getAppFrame() since Streamlit runs inside an iframe.
 *
 * These tests capture screenshots and verify key elements are visible.
 * Screenshots are saved to tests/e2e/screenshots/visual-regression/
 */

import { test, expect } from '@playwright/test';
import { waitForStreamlit, isAuthWall, clickTab, getAppFrame } from './helpers';
import path from 'path';
import fs from 'fs';

const SCREENSHOTS_DIR = path.join(__dirname, 'screenshots', 'visual-regression');

function ensureDir(dir: string) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

async function saveTabScreenshot(page: any, name: string) {
  ensureDir(SCREENSHOTS_DIR);
  const filename = `${name}.png`;
  await page.screenshot({
    path: path.join(SCREENSHOTS_DIR, filename),
    fullPage: false,
  });
  console.log(`Screenshot saved: ${filename}`);
}

test.describe('Visual Regression — Desktop 1440×900', () => {
  test.use({ viewport: { width: 1440, height: 900 } });

  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
  });

  test('Tab 1 — Pareto Explorer desktop screenshot', async ({ page }) => {
    const frame = getAppFrame(page);
    await page.waitForTimeout(2_000);
    await saveTabScreenshot(page, 'pareto-explorer-desktop');
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Pareto Explorer/i);
  });

  test('Tab 2 — Composition Predictor desktop screenshot', async ({ page }) => {
    const frame = getAppFrame(page);
    await clickTab(page, 'Composition Predictor');
    await page.waitForTimeout(1_500);
    await saveTabScreenshot(page, 'composition-predictor-desktop');
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Composition Predictor/i);
  });

  test('Tab 3 — Gate Status Board desktop screenshot', async ({ page }) => {
    const frame = getAppFrame(page);
    await clickTab(page, 'Gate Status Board');
    await page.waitForTimeout(2_000);
    await saveTabScreenshot(page, 'gate-status-board-desktop');
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Gate Status Board/i);
  });

  test('Tab 4 — Lifetime Projector desktop screenshot', async ({ page }) => {
    const frame = getAppFrame(page);
    await clickTab(page, 'Lifetime Projector');
    await page.waitForTimeout(2_000);
    await saveTabScreenshot(page, 'lifetime-projector-desktop');
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Lifetime Projector/i);
  });

  test('Tab 5 — Literature Context desktop screenshot', async ({ page }) => {
    const frame = getAppFrame(page);
    await clickTab(page, 'Literature Context');
    await page.waitForTimeout(2_000);
    await saveTabScreenshot(page, 'literature-context-desktop');
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Literature Context/i);
  });
});

test.describe('Visual Regression — Mobile 390×844', () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 60_000 });
    if (await isAuthWall(page)) {
      test.skip(true, 'Auth wall active');
    }
    await waitForStreamlit(page);
  });

  test('Tab 2 — Composition Predictor mobile screenshot', async ({ page }) => {
    const frame = getAppFrame(page);
    await clickTab(page, 'Composition Predictor');
    await page.waitForTimeout(2_000);
    await saveTabScreenshot(page, 'composition-predictor-mobile');
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Composition Predictor/i);
  });

  test('Tab 5 — Literature Context mobile screenshot', async ({ page }) => {
    const frame = getAppFrame(page);
    await clickTab(page, 'Literature Context');
    await page.waitForTimeout(2_000);
    await saveTabScreenshot(page, 'literature-context-mobile');
    const content = frame.locator('[data-testid="stMainBlockContainer"]');
    await expect(content).toContainText(/Literature Context/i);
  });
});
