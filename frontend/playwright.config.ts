import { defineConfig, devices } from '@playwright/test';

const port = process.env.FRONTEND_PORT ?? '3030';
const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? `http://127.0.0.1:${port}`;
const managedWebServer = process.env.PLAYWRIGHT_BASE_URL
    ? undefined
    : {
        command: `NODE_ENV=test FRONTEND_PORT=${port} SITE_URL=${baseURL} npm run dev -- --hostname 127.0.0.1 --port ${port}`,
        url: baseURL,
        reuseExistingServer: true,
    };

export default defineConfig({
    testDir: './tests/e2e',
    fullyParallel: true,
    retries: process.env.CI ? 2 : 0,
    use: {
        baseURL,
        trace: 'on-first-retry',
    },
    webServer: managedWebServer,
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
    ],
});