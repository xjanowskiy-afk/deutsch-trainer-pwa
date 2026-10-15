// Service Worker for Deutsch Trainer PWA
const CACHE_NAME = 'deutsch-trainer-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE)).then(() => self.skipWaiting())
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
  // Network first with cache fallback
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then((response) => {
        if (response && response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            // cache static assets
            if (!e.request.url.includes('/api/') && !e.request.url.includes('supabase.co')) {
              cache.put(e.request, responseClone);
            }
          });
        }
        return response;
      })
      .catch(() => caches.match(e.request))
  );
});
