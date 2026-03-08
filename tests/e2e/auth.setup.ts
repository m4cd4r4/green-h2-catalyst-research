/**
 * auth.setup.ts
 *
 * Handles Streamlit Cloud authentication and saves storage state.
 *
 * Streamlit Cloud may redirect to https://share.streamlit.io/-/auth/app
 * before allowing access. This setup attempts to handle that flow.
 *
 * The app itself renders inside an iframe at /~/+/.
 *
 * Auth state is saved to tests/e2e/.auth/state.json and reused by
 * all other test files via storageState in playwright.config.ts.
 */

import { test as setup, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

const AUTH_FILE = path.join(__dirname, '.auth', 'state.json');
const SCREENSHOTS_DIR = path.join(__dirname, 'screenshots');

setup('authenticate or document auth state', async ({ page }) => {
  // Ensure directories exist
  [path.dirname(AUTH_FILE), SCREENSHOTS_DIR].forEach((dir) => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });

  await page.goto('https://green-h2-catalyst.streamlit.app/', {
    waitUntil: 'domcontentloaded',
    timeout: 60_000,
  });

  const currentUrl = page.url();
  console.log('Landing URL:', currentUrl);

  if (currentUrl.includes('share.streamlit.io') && currentUrl.includes('auth')) {
    console.log('Auth wall detected — saving current state');
    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, 'auth-wall.png'),
      fullPage: true,
    });

    // Try "Continue as guest" if available
    const guestBtn = page.getByRole('button', { name: /continue as guest/i });
    if (await guestBtn.isVisible({ timeout: 5_000 }).catch(() => false)) {
      await guestBtn.click();
      await page.waitForTimeout(3_000);
    }
  } else {
    // App loaded — wait briefly for the iframe to initialise
    await page.waitForSelector('iframe[src*="/~/+/"]', { timeout: 30_000 }).catch(() => {
      console.log('App iframe not found yet — saving state anyway');
    });
  }

  // Save storage state (cookies/localStorage) for reuse
  await page.context().storageState({ path: AUTH_FILE });
  console.log('Auth state saved to', AUTH_FILE);
});
