// T019: Storage & Cookie Utilities

interface CookieOptions {
  maxAge?: number;
  path?: string;
  secure?: boolean;
  sameSite?: 'Strict' | 'Lax' | 'None';
}

export function getCookie(name: string): string | null {
  if (typeof window === 'undefined') {
    return null;
  }

  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [cookieName, cookieValue] = cookie.trim().split('=');
    if (cookieName === name) {
      return decodeURIComponent(cookieValue);
    }
  }

  return null;
}

export function setCookie(
  name: string,
  value: string,
  options: CookieOptions = {}
): void {
  if (typeof window === 'undefined') {
    return;
  }

  let cookieString = `${name}=${encodeURIComponent(value)}`;

  if (options.maxAge) {
    cookieString += `; Max-Age=${options.maxAge}`;
  }

  if (options.path) {
    cookieString += `; path=${options.path}`;
  } else {
    cookieString += '; path=/';
  }

  if (options.secure) {
    cookieString += '; Secure';
  }

  if (options.sameSite) {
    cookieString += `; SameSite=${options.sameSite}`;
  }

  document.cookie = cookieString;
}

export function deleteCookie(name: string): void {
  setCookie(name, '', { maxAge: -1, path: '/' });
}

// Token-specific helpers
export function getToken(): string | null {
  return getCookie('token');
}

export function setToken(token: string): void {
  // Set token with 15 minute expiration
  setCookie('token', token, {
    maxAge: 15 * 60,
    path: '/',
    sameSite: 'Lax',
  });
}

export function clearToken(): void {
  deleteCookie('token');
}
