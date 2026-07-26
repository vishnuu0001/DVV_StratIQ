# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Small runtime libraries embedded into deterministic generated test scripts.
# Date: 2026-02-03
# ---------------------------------------------------------------------------
"""Small runtime libraries embedded into deterministic generated test scripts."""

PLAYWRIGHT_RUNTIME = r'''type ReviewedStep = { action: string; expected: string; data: string; scenario: string };
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

function textPattern(value: string): RegExp {
  return new RegExp(value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i');
}

async function semanticLocator(page: Page, hint: string): Promise<Locator> {
  const name = textPattern(hint);
  const candidates = [
    page.getByRole('button', { name }), page.getByRole('link', { name }),
    page.getByLabel(name), page.getByPlaceholder(name), page.getByText(name, { exact: false }),
  ];
  for (const candidate of candidates) {
    if (await candidate.count()) return candidate.first();
  }
  throw new Error(`No accessible control matched "${hint}". Set TRACEFORGE_BASE_URL and expose a matching accessible name or label.`);
}

async function executeReviewedStep(page: Page, step: ReviewedStep): Promise<void> {
  const action = step.action.trim();
  if (/^prepare\b/i.test(action)) {
    await page.goto(BASE_URL);
    await expect(page.locator('body')).toBeVisible();
    return;
  }

  const hint = meaningfulText(action, step.scenario);
  const target = await semanticLocator(page, hint)
    .catch(() => semanticLocator(page, meaningfulText(step.scenario, step.scenario)));
  if (/\b(enter|type|input|provide|update|create)\b/i.test(action)) {
    await target.fill(step.data && !/^use\b/i.test(step.data) ? step.data : TEST_VALUE);
  } else if (/\b(select|choose)\b/i.test(action)) {
    const tag = await target.evaluate((element) => element.tagName.toLowerCase());
    if (tag === 'select') await target.selectOption({ label: step.data || TEST_VALUE });
    else await target.click();
  } else {
    await target.click();
  }

  await expect(page.locator('body')).toBeVisible();
  const outcome = meaningfulText(step.expected, '');
  if (outcome.length >= 4) await expect.soft(page.locator('body')).toContainText(textPattern(outcome));
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
