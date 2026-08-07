#!/usr/bin/env node
/**
 * Capture real synthetic-dashboard screenshots via system Chrome/Edge + puppeteer-core.
 * Bind: 127.0.0.1 only. Temporary browser profile. No personal profile / extensions.
 */
import { createRequire } from 'node:module';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const IMAGES = path.join(ROOT, 'docs', 'images');
const MARKER = 'SYNTHETIC DEMONSTRATION DATA';
const BASE = process.env.SNSL_UI_URL || 'http://127.0.0.1:5173';
const VIEWPORT = { width: 1440, height: 1000 };

const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
].filter(Boolean);

function findChrome() {
  for (const p of CHROME_CANDIDATES) {
    if (p && fs.existsSync(p)) return p;
  }
  return null;
}

function ensurePuppeteer(moduleRoot) {
  const pkg = path.join(moduleRoot, 'node_modules', 'puppeteer-core');
  if (!fs.existsSync(pkg)) {
    fs.mkdirSync(moduleRoot, { recursive: true });
    const packageJson = path.join(moduleRoot, 'package.json');
    if (!fs.existsSync(packageJson)) {
      fs.writeFileSync(
        packageJson,
        JSON.stringify({ name: 'snsl-capture-deps', private: true, version: '1.0.0' }, null, 2),
      );
    }
    const install = spawnSync('npm', ['install', 'puppeteer-core@23.11.1', '--no-save', '--no-package-lock'], {
      cwd: moduleRoot,
      shell: true,
      stdio: 'inherit',
    });
    if (install.status !== 0) throw new Error('puppeteer-core install failed');
  }
  const require = createRequire(path.join(moduleRoot, 'package.json'));
  return require('puppeteer-core');
}

async function waitForMarker(page) {
  await page.waitForFunction(
    (marker) => document.body && document.body.innerText.includes(marker),
    { timeout: 60000 },
    MARKER,
  );
  const has = await page.evaluate((marker) => document.body.innerText.includes(marker), MARKER);
  if (!has) throw new Error(`Marker missing: ${MARKER}`);
}

async function sleep(ms) {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

async function settleScene(page) {
  await page.waitForSelector('[data-testid="network-scene"] canvas', { timeout: 60000 });
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('.toolbar button'));
    const fitBtn = buttons.find((b) => (b.textContent || '').trim() === 'Fit');
    fitBtn?.click();
  });
  await sleep(3500);
}

async function main() {
  const chrome = findChrome();
  if (!chrome) {
    console.error('REFUSE SCREENSHOT: Chrome/Edge not found');
    process.exit(1);
  }

  const moduleRoot = path.join(ROOT, 'capture-node-deps');
  const puppeteer = ensurePuppeteer(moduleRoot);
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'snsl-browser-'));

  fs.mkdirSync(IMAGES, { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: chrome,
    headless: 'new',
    defaultViewport: VIEWPORT,
    args: [
      `--user-data-dir=${profile}`,
      '--no-first-run',
      '--no-default-browser-check',
      '--disable-extensions',
      '--disable-sync',
      '--disable-background-networking',
      '--disable-component-update',
      '--deny-permission-prompts',
      '--window-size=1440,1000',
    ],
  });

  try {
    const page = await browser.newPage();
    await page.setViewport(VIEWPORT);
    await page.goto(BASE, { waitUntil: 'networkidle0', timeout: 90000 });
    await waitForMarker(page);
    await page.waitForSelector('[data-testid="app-root"]', { timeout: 30000 });
    // Ensure API-backed lab (no mock fallback banner preferred).
    await page.waitForFunction(
      () => !document.querySelector('[data-testid="loading"]'),
      { timeout: 60000 },
    );
    const apiError = await page.$('[data-testid="api-error"]');
    if (apiError) {
      const msg = await page.evaluate((el) => el.textContent || '', apiError);
      throw new Error(`Dashboard using mock fallback (API failed): ${msg}`);
    }

    // --- Screenshot 1: 3D topology / segmentation ---
    await page.evaluate(() => {
      const btn = Array.from(document.querySelectorAll('nav button')).find((b) =>
        b.textContent?.includes('3D Topology'),
      );
      btn?.click();
    });
    await page.waitForSelector('[data-testid="topology-view"]', { timeout: 30000 });
    await page.click('[data-testid="view-mode-SEGMENTATION"]');
    await settleScene(page);
    const out1 = path.join(IMAGES, 'sample-3d-network-security-map.png');
    await page.screenshot({ path: out1, fullPage: false });
    console.log('Wrote', out1);

    // --- Screenshot 2: POLICY_REACHABILITY ---
    await page.click('[data-testid="view-mode-POLICY_REACHABILITY"]');
    await settleScene(page);
    const bodyText = await page.evaluate(() => document.body.innerText);
    if (!/modelled|modeled|SIMULATED|PROPOSED|Reachability|POLICY/i.test(bodyText)) {
      throw new Error('Reachability/policy context missing from page text');
    }
    const out2 = path.join(IMAGES, 'sample-policy-reachability-view.png');
    await page.screenshot({ path: out2, fullPage: false });
    console.log('Wrote', out2);

    // Prefer UNKNOWN / pending-approval device detail.
    let picked = null;
    await page.evaluate(() => {
      const btn = Array.from(document.querySelectorAll('nav button')).find((b) =>
        b.textContent?.includes('Quarantine'),
      );
      btn?.click();
    });
    await page.waitForSelector('[data-testid="quarantine-view"]', { timeout: 30000 });
    picked = await page.evaluate(() => {
      const buttons = Array.from(
        document.querySelectorAll('[data-testid="quarantine-view"] button.btn'),
      );
      const prefer = buttons.find((b) => /unk/i.test(b.textContent || ''));
      const target = prefer || buttons[0];
      if (!target) return null;
      const label = target.textContent || '';
      target.click();
      return label;
    });
    if (!picked) {
      await page.evaluate(() => {
        const btn = Array.from(document.querySelectorAll('nav button')).find((b) =>
          b.textContent?.includes('Inventory'),
        );
        btn?.click();
      });
      await page.waitForSelector('[data-testid="inventory-view"]', { timeout: 30000 });
      picked = await page.evaluate(() => {
        const rows = Array.from(document.querySelectorAll('[data-testid="inventory-view"] button, [data-testid="inventory-view"] a, [data-testid="inventory-view"] tr'));
        const prefer = rows.find((el) => /UNK|unknown|pending/i.test(el.textContent || ''));
        if (!prefer) return null;
        const clickable = prefer.closest('tr')?.querySelector('button') || prefer;
        if (clickable && 'click' in clickable) clickable.click();
        return prefer.textContent || 'inventory-device';
      });
    }
    if (!picked) throw new Error('No quarantined/interesting device to open');
    await page.waitForSelector('[data-testid="device-detail-view"]', { timeout: 30000 });
    await sleep(800);
    const openApproval = await page.$('[data-testid="open-approval"]');
    if (openApproval) {
      await openApproval.click();
      await page.waitForSelector('[data-testid="approval-warning"]', { timeout: 10000 });
    }
    const detailText = await page.evaluate(() => document.body.innerText);
    if (!detailText.includes(MARKER)) throw new Error('Marker missing on device detail');
    const out3 = path.join(IMAGES, 'sample-device-detail.png');
    await page.screenshot({ path: out3, fullPage: false });
    console.log('Wrote', out3, 'device=', picked.trim());
  } finally {
    await browser.close();
    fs.rmSync(profile, { recursive: true, force: true });
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
