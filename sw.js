// Service Worker for Deutsch Trainer PWA (v15 High Performance)
const CACHE_NAME = 'deutsch-trainer-v15';

// Critical core assets to precache immediately
const CORE_ASSETS = [
  '/',
  '/manifest.json',
  '/favicon.ico',
  '/favicon.png',
  '/icon-192.png',
  '/icon-512.png',
  '/apple-touch-icon.png',
  '/assets/gemini-live-sdk.js',
  '/assets/hero-badge.png',
  '/assets/img_18.webp',
  '/assets/img_8.webp',
  '/assets/img_23.webp',
  '/assets/img_24.webp'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(CORE_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  const url = e.request.url;

  // 1. Bypass dynamic API calls and external Supabase sync
  if (url.includes('/api/') || url.includes('supabase.co')) {
    return;
  }

  // 2. Video streaming & range requests: pass through directly to avoid Cache API 206 errors
  if (e.request.headers.has('range') || url.endsWith('.mp4')) {
    return;
  }

  // 3. Static assets (/assets/, images, icons, scripts): Cache-First for 0ms latency
  if (url.includes('/assets/') || url.match(/\.(webp|png|jpg|jpeg|svg|js|css|woff2?)$/i)) {
    e.respondWith(
      caches.match(e.request).then((cachedResponse) => {
        if (cachedResponse) return cachedResponse;
        return fetch(e.request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const clone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(e.request, clone));
          }
          return networkResponse;
        });
      })
    );
    return;
  }

  // 4. HTML Navigation: Network-First with Cache Fallback
  e.respondWith(
    fetch(e.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const clone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(e.request, clone));
        }
        return networkResponse;
      })
      .catch(() => caches.match(e.request).then((cached) => cached || caches.match('/')))
  );
});
