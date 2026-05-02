import type { ReactNode } from 'react';

import { SiteNavigation } from '@/components/site-navigation';
import { getVisibleNavigationItems, siteShell, type SiteNavigationItem } from '@/lib/site-config';

type PageShellProps = {
    children: ReactNode;
    navigationItems?: SiteNavigationItem[];
    wordmark?: string;
};

export function PageShell({
    children,
    navigationItems = getVisibleNavigationItems(),
    wordmark = siteShell.wordmark,
}: PageShellProps) {
    return (
        <div className={`page-shell page-shell--${siteShell.theme}`}>
            <a className="skip-link" href="#main-content">
                Skip to content
            </a>
            <div aria-hidden="true" className="page-shell__pattern" />
            <div aria-hidden="true" className="page-shell__trim" />
            <SiteNavigation items={navigationItems} wordmark={wordmark} />

            <main className="page-shell__main" id="main-content">
                <div className="page-shell__content">{children}</div>
            </main>
        </div>
    );
}