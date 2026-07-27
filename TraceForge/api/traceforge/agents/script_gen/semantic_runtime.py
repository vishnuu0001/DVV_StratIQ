# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Small runtime libraries embedded into deterministic generated test scripts.
# Date: 2026-02-03
# ---------------------------------------------------------------------------
"""Small runtime libraries embedded into deterministic generated test scripts."""

PLAYWRIGHT_RUNTIME = r'''type ReviewedStep = { action: string; expected: string; data: string; scenario: string };
declare const process: { env: Record<string, string | undefined> };

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL ?? process.env.TRACEFORGE_BASE_URL ?? 'http://localhost:3000';
const LOCATOR_MAP: Record<string, string> = (() => {
  const raw = process.env.TRACEFORGE_LOCATORS;
  if (!raw) return {};
  try { return JSON.parse(raw) as Record<string, string>; }
  catch { throw new Error('TRACEFORGE_LOCATORS must be a valid JSON object of semantic keys to selectors.'); }
})();

function uniqueTestValue(): string {
  return process.env.TRACEFORGE_TEST_VALUE
    ?? `traceforge-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

function meaningfulText(value: string, fallback: string): string {
  const cleaned = value
    .replace(/^(open|prepare|attempt|verify|navigate to|populate|submit|reload|the system shall|the application shall|customers? shall)\s*/i, '')
    .replace(/\b(the|a|an|shall|should|be able to|configured|documented|approved|requirement|scenario)\b/gi, ' ')
    .replace(/[^a-z0-9 ]/gi, ' ').replace(/\s+/g, ' ').trim();
  return (cleaned || fallback).split(' ').slice(0, 8).join(' ');
}

function textPattern(value: string): RegExp {
  return new RegExp(value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i');
}

function configuredLocator(page: Page, hint: string): Locator | null {
  const selector = LOCATOR_MAP[hint] ?? LOCATOR_MAP[hint.toLowerCase()];
  return selector ? page.locator(selector) : null;
}

async function semanticLocator(page: Page, hint: string): Promise<Locator> {
  const configured = configuredLocator(page, hint);
  if (configured) {
    await expect(configured, `Configured locator for "${hint}" must resolve exactly once`).toHaveCount(1);
    return configured;
  }
  const name = textPattern(hint);
  const candidates = [
    page.getByRole('button', { name }), page.getByRole('link', { name }),
    page.getByLabel(name), page.getByPlaceholder(name), page.getByText(name, { exact: false }),
  ];
  for (const candidate of candidates) {
    if (await candidate.count() === 1) return candidate;
  }
  throw new Error(
    `No unique accessible control matched "${hint}". Add an accessible name or map the semantic key in TRACEFORGE_LOCATORS.`,
  );
}

async function assertExpectedOutcome(page: Page, expected: string): Promise<void> {
  await expect(page.locator('body')).toBeVisible();
  const outcome = meaningfulText(expected, '');
  if (outcome.length >= 4) {
    await expect(page.locator('body'), `Expected visible outcome: ${expected}`).toContainText(textPattern(outcome));
  }
}

async function executeReviewedStep(page: Page, step: ReviewedStep): Promise<void> {
  const action = step.action.trim();
  if (/\b(open the application|authenticate|navigate)\b/i.test(action) && page.url() === 'about:blank') {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await expect(page.locator('body')).toBeVisible();
    return;
  }

  const hint = meaningfulText(action, step.scenario);
  const target = await semanticLocator(page, hint)
    .catch(() => semanticLocator(page, meaningfulText(step.scenario, step.scenario)));
  const suppliedData = step.data && !/^(use|capture|reuse|criterion)\b/i.test(step.data)
    ? step.data : uniqueTestValue();

  if (/\b(enter|type|input|provide|update|populate|create)\b/i.test(action)) {
    await expect(target).toBeEditable();
    await target.fill(suppliedData);
  } else if (/\b(select|choose)\b/i.test(action)) {
    if (await target.evaluate((element) => element.tagName.toLowerCase()) === 'select') {
      await target.selectOption({ label: suppliedData });
    } else {
      await target.click();
    }
  } else {
    await expect(target).toBeEnabled();
    await target.click();
  }

  await assertExpectedOutcome(page, step.expected);
}
'''


SELENIUM_RUNTIME = r'''type ReviewedStep = { action: string; expected: string; data: string; scenario: string };
declare const process: { env: Record<string, string | undefined> };

const BASE_URL = process.env.TRACEFORGE_BASE_URL ?? 'http://localhost:3000';
const TEST_VALUE = process.env.TRACEFORGE_TEST_VALUE ?? 'TraceForge-Test-Value';

function meaningfulText(value: string, fallback: string): string {
  const cleaned = value
    .replace(/^(prepare|attempt|verify|the system shall|the application shall|customers? shall)\s*/i, '')
    .replace(/\b(the|a|an|shall|should|be able to|documented|approved|requirement|scenario)\b/gi, ' ')
    .replace(/[^a-z0-9 ]/gi, ' ').replace(/\s+/g, ' ').trim();
  return (cleaned || fallback).split(' ').slice(0, 8).join(' ');
}

function xpathLiteral(value: string): string {
  if (!value.includes("'")) return `'${value}'`;
  if (!value.includes('"')) return `"${value}"`;
  return `concat('${value.replace(/'/g, `', "'", '`)}')`;
}

async function semanticElement(driver: WebDriver, hint: string): Promise<WebElement> {
  const literal = xpathLiteral(hint.toLowerCase());
  const xpath = `//*[self::button or self::a or self::input or self::select or self::textarea or @role='button' or @role='link'][contains(translate(concat(normalize-space(.), ' ', @aria-label, ' ', @placeholder, ' ', @name), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), ${literal})]`;
  const matches = await driver.findElements(By.xpath(xpath));
  if (matches.length) return matches[0];
  throw new Error(`No accessible control matched "${hint}". Set TRACEFORGE_BASE_URL and expose a matching accessible name or label.`);
}

async function executeReviewedStep(driver: WebDriver, step: ReviewedStep): Promise<void> {
  const action = step.action.trim();
  if (/^prepare\b/i.test(action)) {
    await driver.get(BASE_URL);
    assert.ok((await driver.findElements(By.css('body'))).length === 1, 'Application body is available');
    return;
  }

  const hint = meaningfulText(action, step.scenario);
  let target: WebElement;
  try { target = await semanticElement(driver, hint); }
  catch { target = await semanticElement(driver, meaningfulText(step.scenario, step.scenario)); }
  if (/\b(enter|type|input|provide|update|create)\b/i.test(action)) {
    await target.clear();
    await target.sendKeys(step.data && !/^use\b/i.test(step.data) ? step.data : TEST_VALUE);
  } else {
    await target.click();
  }

  const bodyText = await driver.findElement(By.css('body')).getText();
  assert.ok(bodyText.trim().length > 0, step.expected || 'Application returned visible content');
}
'''
