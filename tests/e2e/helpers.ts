/**
 * helpers.ts — shared utilities for the green-h2-catalyst E2E suite.
 *
 * KEY ARCHITECTURE NOTE:
 * Streamlit Cloud wraps the app inside an iframe at /~/+/.
 * All Streamlit elements (stApp, stSidebar, stTabs, etc.) live in this iframe.
 * Use `getAppFrame(page)` to get the FrameLocator and pass it to all locator calls.
 */

import { Page, FrameLocator, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

const SCREENSHOTS_DIR = path.join(__dirname, 'screenshots');

/**
 * Returns the FrameLocator for the Streamlit app iframe.
 * On Streamlit Cloud the app runs inside an iframe at /~/+/.
 */
export function getAppFrame(page: Page): FrameLocator {
  return page.frameLocator('iframe[src*="/~/+/"]');
}

/**
 * Wait for the Streamlit app iframe to fully load and render.
 * - Waits for the iframe element itself to be present
 * - Then waits for stApp to appear inside the iframe
 * - Then waits for spinners to clear
 */
export async function waitForStreamlit(page: Page, timeoutMs = 60_000): Promise<void> {
  // First wait for the outer shell to load
  await page.waitForSelector('iframe[src*="/~/+/"]', { timeout: timeoutMs });

  const frame = getAppFrame(page);

  // Wait for stApp in the iframe
  await frame.locator('[data-testid="stApp"]').waitFor({ state: 'visible', timeout: timeoutMs });

  // Wait for spinners to disappear inside the iframe
  // Use a short additional wait since Streamlit re-renders on load
  await page.waitForTimeout(1_000);
}

/**
 * Click a tab by its visible label text (inside the app iframe).
 * On mobile viewports, the sidebar may intercept clicks — use force:true.
 */
export async function clickTab(page: Page, labelText: string): Promise<void> {
  const frame = getAppFrame(page);
  const tab = frame.getByRole('tab', { name: new RegExp(labelText, 'i') });
  await expect(tab).toBeVisible({ timeout: 20_000 });
  // Use force:true to handle cases where sidebar overlays the tab on mobile
  await tab.click({ force: true });
  // Give Streamlit time to re-render after tab switch
  await page.waitForTimeout(1_500);
}

/**
 * Save a screenshot to the screenshots directory.
 */
export async function captureScreenshot(page: Page, name: string): Promise<void> {
  if (!fs.existsSync(SCREENSHOTS_DIR)) {
    fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
  }
  await page.screenshot({
    path: path.join(SCREENSHOTS_DIR, `${name}.png`),
    fullPage: false,
  });
}

/**
 * Check if Streamlit rendered an auth wall instead of app content.
 * Auth walls redirect to share.streamlit.io.
 */
export async function isAuthWall(page: Page): Promise<boolean> {
  const url = page.url();
  // Auth wall redirects away from the main app domain
  return url.includes('share.streamlit.io/-/auth') || url.includes('/-/auth/app');
}

/**
 * Get the full inner text of the main Streamlit content block (inside iframe).
 */
export async function getMainContent(page: Page): Promise<string> {
  const frame = getAppFrame(page);
  return frame.locator('[data-testid="stMainBlockContainer"]').innerText();
}

/**
 * Get the HTML of the main Streamlit content block (inside iframe).
 */
export async function getMainHTML(page: Page): Promise<string> {
  const frame = getAppFrame(page);
  return frame.locator('[data-testid="stMainBlockContainer"]').innerHTML();
}
