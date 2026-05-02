import { expect, test } from '@playwright/test';

test('homepage shows the launch intro and intentional empty state', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { level: 1, name: /AfroUrban, after dark/i })).toBeVisible();
    await expect(page.getByText(/A new editorial city guide is taking shape/i)).toBeVisible();
    await expect(page.getByText(/No listings are being faked for launch/i)).toBeVisible();
    await expect(page.getByRole('link', { name: 'Home' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Stories' })).toHaveCount(0);
});

test('homepage stays usable on a mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/');

    await expect(page.getByRole('button', { name: 'Open navigation menu' })).toBeVisible();

    const fitsViewport = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);

    expect(fitsViewport).toBe(true);
});

test('homepage remains usable without backend content requests', async ({ page }) => {
    await page.route('**/api/**', async (route) => {
        await route.abort();
    });

    await page.goto('/');

    await expect(page.getByRole('heading', { level: 1, name: /AfroUrban, after dark/i })).toBeVisible();
    await expect(page.getByText(/Nothing is being padded for launch/i)).toBeVisible();
    await expect(page.getByRole('link', { name: 'Stories' })).toHaveCount(0);
    await expect(page.getByRole('link', { name: 'Events' })).toHaveCount(0);
    await expect(page.getByRole('link', { name: 'Organizations' })).toHaveCount(0);
});