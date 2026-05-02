import { expect, test } from '@playwright/test';

test('homepage is reachable on the configured base URL', async ({ page, baseURL }) => {
    await page.goto('/');

    await expect(page).toHaveURL(`${baseURL}/`);
    await expect(page.getByRole('heading', { level: 1, name: /AfroUrban/i })).toBeVisible();
});