import { test, expect } from '@playwright/test';

test('Recuperación RAG: Debe citar el artículo específico del reglamento', async ({ page }) => {
  await page.goto('/');
  const input = page.locator('textarea#pregunta');
  await input.fill('¿Qué dice el reglamento sobre la matrícula extraordinaria?');
  await page.locator('button[type="submit"]').click();

  // Comprueba que el bot cite el Art. 22 o el artículo correspondiente indexado
  await expect(page.locator('text=/Art(ículo|\.)\s*22/i').first()).toBeVisible({ timeout: 15000 });
});