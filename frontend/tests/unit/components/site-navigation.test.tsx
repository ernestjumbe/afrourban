import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

vi.mock('next/link', () => ({
    default: ({ children, href, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) => (
        <a href={href} {...props}>
            {children}
        </a>
    ),
}));

import { SiteNavigation } from '@/components/site-navigation';
import { getVisibleNavigationItems, siteShell } from '@/lib/site-config';

describe('SiteNavigation', () => {
    it('renders only the launch navigation items and exposes a menu trigger', () => {
        render(<SiteNavigation items={getVisibleNavigationItems()} wordmark={siteShell.wordmark} />);

        const homeLinks = screen.getAllByRole('link', { name: 'Home' });

        expect(homeLinks).toHaveLength(2);
        expect(homeLinks.every((link) => link.getAttribute('href') === '/')).toBe(true);
        expect(screen.queryByRole('link', { name: 'Stories' })).toBeNull();
        expect(screen.queryByRole('link', { name: 'Events' })).toBeNull();
        expect(screen.getByRole('button', { name: 'Open navigation menu' })).not.toBeNull();
    });
});