import Link from 'next/link';

import type { SiteNavigationItem } from '@/lib/site-config';

type SiteNavigationProps = {
    items: SiteNavigationItem[];
    wordmark: string;
};

function NavigationLinks({ items }: { items: SiteNavigationItem[] }) {
    return (
        <ul className="site-nav__list">
            {items.map((item) => (
                <li key={item.href}>
                    <Link
                        className={item.isPrimary ? 'site-nav__link site-nav__link--primary' : 'site-nav__link'}
                        href={item.href}
                    >
                        {item.label}
                    </Link>
                </li>
            ))}
        </ul>
    );
}

export function SiteNavigation({ items, wordmark }: SiteNavigationProps) {
    return (
        <header className="site-header">
            <div className="page-shell__content site-header__inner">
                <Link className="site-header__brand" href="/">
                    {wordmark}
                </Link>

                <nav aria-label="Primary" className="site-nav site-nav--desktop">
                    <NavigationLinks items={items} />
                </nav>

                <details className="site-nav__drawer">
                    <summary aria-label="Open navigation menu" className="site-nav__menu-button" role="button">
                        Menu
                    </summary>

                    <nav aria-label="Mobile primary" className="site-nav__drawer-panel">
                        <NavigationLinks items={items} />
                    </nav>
                </details>
            </div>
        </header>
    );
}