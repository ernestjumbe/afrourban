import { z } from 'zod';

import { logRuntimeConfigLoaded, logStartupFailure } from './logging';

const portSchema = z.preprocess(
    (value) => (value === undefined || value === '' ? 3030 : value),
    z.coerce.number().int().min(3030).max(4000),
);

const booleanSchema = z.preprocess((value) => {
    if (typeof value === 'string') {
        return value.toLowerCase() === 'true';
    }

    return value;
}, z.boolean());

const runtimeConfigSchema = z
    .object({
        FRONTEND_PORT: portSchema,
        NODE_ENV: z.enum(['development', 'test', 'production']),
        SITE_URL: z.string().url(),
        API_URL: z.string().url().optional(),
        AUTH_SECRET: z.string().min(1).optional(),
        AUTH_TRUST_HOST: booleanSchema.optional(),
    })
    .superRefine((env, context) => {
        const parsedSiteUrl = new URL(env.SITE_URL);
        const sitePort = parsedSiteUrl.port === '' ? 80 : Number(parsedSiteUrl.port);

        if (sitePort !== env.FRONTEND_PORT) {
            context.addIssue({
                code: z.ZodIssueCode.custom,
                message: 'SITE_URL port must match FRONTEND_PORT.',
                path: ['SITE_URL'],
            });
        }
    })
    .transform((env) => ({
        port: env.FRONTEND_PORT,
        nodeEnv: env.NODE_ENV,
        siteUrl: env.SITE_URL,
        apiUrl: env.API_URL,
        authSecret: env.AUTH_SECRET,
        authTrustHost: env.AUTH_TRUST_HOST ?? false,
    }));

export type FrontendRuntimeConfig = z.infer<typeof runtimeConfigSchema>;
export type ReservedServerConfig = Pick<FrontendRuntimeConfig, 'apiUrl' | 'authSecret' | 'authTrustHost'>;

let cachedRuntimeConfig: FrontendRuntimeConfig | null = null;

export function parseRuntimeConfig(env: NodeJS.ProcessEnv): FrontendRuntimeConfig {
    const parsed = runtimeConfigSchema.safeParse(env);

    if (!parsed.success) {
        logStartupFailure(
            parsed.error.issues.map((issue) => ({
                path: issue.path.join('.') || 'root',
                message: issue.message,
            })),
        );

        throw new Error('Invalid frontend runtime configuration.');
    }

    logRuntimeConfigLoaded({
        nodeEnv: parsed.data.nodeEnv,
        port: parsed.data.port,
        siteUrl: parsed.data.siteUrl,
    });

    return parsed.data;
}

export function getRuntimeConfig(): FrontendRuntimeConfig {
    if (cachedRuntimeConfig) {
        return cachedRuntimeConfig;
    }

    cachedRuntimeConfig = parseRuntimeConfig(process.env);

    return cachedRuntimeConfig;
}

export function getReservedServerConfig(): ReservedServerConfig {
    const runtimeConfig = getRuntimeConfig();

    return {
        apiUrl: runtimeConfig.apiUrl,
        authSecret: runtimeConfig.authSecret,
        authTrustHost: runtimeConfig.authTrustHost,
    };
}

export function resetRuntimeConfigForTests(): void {
    cachedRuntimeConfig = null;
}