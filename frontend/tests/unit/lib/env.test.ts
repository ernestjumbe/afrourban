import { beforeEach, describe, expect, it, vi } from 'vitest';

const logRuntimeConfigLoaded = vi.fn();
const logStartupFailure = vi.fn();

vi.mock('@/lib/logging', () => ({
    logRuntimeConfigLoaded,
    logStartupFailure,
}));

describe('getRuntimeConfig', () => {
    const originalEnv = process.env;

    beforeEach(async () => {
        vi.resetModules();
        logRuntimeConfigLoaded.mockReset();
        logStartupFailure.mockReset();
        process.env = {
            ...originalEnv,
            NODE_ENV: 'development',
            SITE_URL: 'http://localhost:3030',
        };

        const envModule = await import('@/lib/env');
        envModule.resetRuntimeConfigForTests();
    });

    it('uses port 3030 when no override is provided', async () => {
        delete process.env.FRONTEND_PORT;

        const { getRuntimeConfig } = await import('@/lib/env');
        const runtimeConfig = getRuntimeConfig();

        expect(runtimeConfig.port).toBe(3030);
        expect(runtimeConfig.siteUrl).toBe('http://localhost:3030');
        expect(logRuntimeConfigLoaded).toHaveBeenCalledWith({
            nodeEnv: 'development',
            port: 3030,
            siteUrl: 'http://localhost:3030',
        });
    });

    it('accepts a valid override inside the supported port range', async () => {
        process.env.FRONTEND_PORT = '3031';
        process.env.SITE_URL = 'http://localhost:3031';

        const { getRuntimeConfig } = await import('@/lib/env');
        const runtimeConfig = getRuntimeConfig();

        expect(runtimeConfig.port).toBe(3031);
        expect(runtimeConfig.siteUrl).toBe('http://localhost:3031');
    });

    it('rejects an override outside the supported port range', async () => {
        process.env.FRONTEND_PORT = '4001';
        process.env.SITE_URL = 'http://localhost:4001';

        const { getRuntimeConfig } = await import('@/lib/env');

        expect(() => getRuntimeConfig()).toThrow('Invalid frontend runtime configuration.');
        expect(logStartupFailure).toHaveBeenCalledWith([
            expect.objectContaining({
                path: 'FRONTEND_PORT',
            }),
        ]);
    });

    it('keeps reserved runtime fields optional until BFF or auth features use them', async () => {
        process.env.FRONTEND_PORT = '3030';
        delete process.env.API_URL;
        delete process.env.AUTH_SECRET;
        delete process.env.AUTH_TRUST_HOST;

        const { getReservedServerConfig } = await import('@/lib/env');

        expect(getReservedServerConfig()).toEqual({
            apiUrl: undefined,
            authSecret: undefined,
            authTrustHost: false,
        });
    });
});