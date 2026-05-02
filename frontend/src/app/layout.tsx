import type { Metadata } from 'next';
import type { ReactNode } from 'react';

import { PageShell } from '@/components/page-shell';
import { getRuntimeConfig } from '@/lib/env';
import { siteShell } from '@/lib/site-config';

import './globals.css';

export const metadata: Metadata = {
    title: {
        default: siteShell.wordmark,
        template: `%s | ${siteShell.wordmark}`,
    },
    description: siteShell.description,
};

type RootLayoutProps = Readonly<{
    children: ReactNode;
}>;

export default function RootLayout({ children }: RootLayoutProps) {
    getRuntimeConfig();

    return (
        <html lang="en">
            <body>
                <PageShell>{children}</PageShell>
            </body>
        </html>
    );
}