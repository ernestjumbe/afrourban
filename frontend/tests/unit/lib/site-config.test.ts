import { describe, expect, it } from 'vitest';

import {
    getVisibleNavigationItems,
    getReservedNavigationItems,
    siteShell,
} from '@/lib/site-config';

describe('site-config', () => {
    it('exposes only implemented launch destinations through the visible navigation helper', () => {
        expect(getVisibleNavigationItems()).toEqual([
            {
                href: '/',
                isPrimary: true,
                label: 'Home',
            },
        ]);
    });

    it('keeps reserved future destinations separate from launch navigation', () => {
        expect(getReservedNavigationItems()).toEqual([
            {
                href: '/stories',
                label: 'Stories',
            },
            {
                href: '/events',
                label: 'Events',
            },
            {
                href: '/organizations',
                label: 'Organizations',
            },
        ]);
        expect(siteShell.wordmark).toBe('AfroUrban');
    });
});