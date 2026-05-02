import { render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

vi.mock('next/link', () => ({
    default: ({ children, href, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) => (
        <a href={href} {...props}>
            {children}
        </a>
    ),
}));

import { PageShell } from '@/components/page-shell';

describe('PageShell', () => {
    it('renders the editorial frame and wraps page content in the main landmark', () => {
        render(
            <PageShell>
                <section>
                    <h1>Launch Edition</h1>
                </section>
            </PageShell>,
        );

        const main = screen.getByRole('main');

        expect(document.querySelector('.page-shell__trim')).not.toBeNull();
        expect(screen.getByRole('link', { name: 'AfroUrban' }).getAttribute('href')).toBe('/');
        expect(within(main).getByRole('heading', { level: 1, name: 'Launch Edition' })).not.toBeNull();
    });
});