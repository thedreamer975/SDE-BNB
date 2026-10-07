import { NextRequest, NextResponse } from 'next/server';

/** Routes that require a logged-in session */
const PROTECTED = [
  '/trips',
  '/wishlists',
  '/notifications',
  '/account',
  '/messages',
  '/hosting',
  '/book',
  '/become-a-host',
];

/** Routes that should redirect logged-in users to home */
const AUTH_ONLY = ['/login', '/signup'];

function isProtected(pathname: string): boolean {
  return PROTECTED.some((p) => pathname === p || pathname.startsWith(`${p}/`));
}

function isAuthOnly(pathname: string): boolean {
  return AUTH_ONLY.some((p) => pathname === p || pathname.startsWith(`${p}/`));
}

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  const session = req.cookies.get('session')?.value;

  if (isProtected(pathname) && !session) {
    const url = req.nextUrl.clone();
    url.pathname = '/login';
    url.searchParams.set('next', pathname);
    return NextResponse.redirect(url);
  }

  if (isAuthOnly(pathname) && session) {
    const next = req.nextUrl.searchParams.get('next') ?? '/';
    const url = req.nextUrl.clone();
    url.pathname = next;
    url.search = '';
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico, images, robots, sitemap
     * - api (already protected by the server)
     */
    '/((?!_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml|api/).*)',
  ],
};
