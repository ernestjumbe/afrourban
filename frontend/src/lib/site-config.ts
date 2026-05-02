export type SiteNavigationItem = {
    label: string;
    href: string;
    isPrimary?: boolean;
};

export type ReservedNavigationItem = {
    label: string;
    href: string;
};

export const siteShell = {
    theme: 'dark' as const,
    goldTrimHeight: 6,
    contentWidth: '1400px',
    wordmark: 'AfroUrban',
    description: 'Stories, places, and people shaping the AfroUrban city rhythm.',
};

export const siteExtensionPoints = {
    authRoutePrefixes: ['/account', '/saved', '/settings'],
    bffRoutePrefix: '/api',
};

const launchNavigation: SiteNavigationItem[] = [
    {
        label: 'Home',
        href: '/',
        isPrimary: true,
    },
];

const reservedNavigation: ReservedNavigationItem[] = [
    {
        label: 'Stories',
        href: '/stories',
    },
    {
        label: 'Events',
        href: '/events',
    },
    {
        label: 'Organizations',
        href: '/organizations',
    },
];

export function getVisibleNavigationItems(): SiteNavigationItem[] {
    return launchNavigation;
}

export function getReservedNavigationItems(): ReservedNavigationItem[] {
    return reservedNavigation;
}