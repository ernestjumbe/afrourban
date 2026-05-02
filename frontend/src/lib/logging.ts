type LogLevel = 'info' | 'warn' | 'error';

type LogContext = Record<string, unknown>;

type StartupIssue = {
    path: string;
    message: string;
};

function writeLog(level: LogLevel, event: string, context: LogContext = {}): void {
    const payload = {
        timestamp: new Date().toISOString(),
        level,
        event,
        service: 'afrourban-frontend',
        ...context,
    };

    const message = JSON.stringify(payload);

    if (level === 'error') {
        console.error(message);
        return;
    }

    if (level === 'warn') {
        console.warn(message);
        return;
    }

    console.info(message);
}

export function logRuntimeConfigLoaded(context: {
    nodeEnv: string;
    port: number;
    siteUrl: string;
}): void {
    writeLog('info', 'frontend.runtime.loaded', context);
}

export function logStartupFailure(issues: StartupIssue[]): void {
    writeLog('error', 'frontend.runtime.invalid', { issues });
}