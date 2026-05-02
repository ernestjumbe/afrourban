import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

import { siteExtensionPoints } from '@/lib/site-config';

export function isReservedProtectedPath(pathname: string) {
    return siteExtensionPoints.authRoutePrefixes.some((prefix) => pathname.startsWith(prefix));
}

export function proxy(request: NextRequest) {
    const requestHeaders = new Headers(request.headers);

    requestHeaders.set('x-afrourban-pathname', request.nextUrl.pathname);

    if (isReservedProtectedPath(request.nextUrl.pathname)) {
        requestHeaders.set('x-afrourban-auth-mode', 'reserved');
    }

    return NextResponse.next({
        request: {
            headers: requestHeaders,
        },
    });
}

export const config = {
    matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};