/* Marathi Quiz Progressive Web App (PWA) Service Worker */
const CACHE_NAME = 'marathi-quiz-cache-v1';
const PRECACHE_URLS = [
  '/',
  '/app/static/manifest.json',
  '/app/static/icons/icon-192.png',
  '/app/static/icons/icon-512.png',
  '/app/static/icons/icon-maskable-192.png',
  '/app/static/icons/icon-maskable-512.png',
  '/app/static/icons/favicon.png',
  'https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700;800&family=Outfit:wght@400;600;700&display=swap'
];

// Install Event - Pre-cache essential shell and assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(PRECACHE_URLS).catch((err) => {
          console.warn('PWA Precache warning (non-fatal):', err);
        });
      })
      .then(() => self.skipWaiting())
  );
});

// Activate Event - Clean up stale caches and claim clients immediately
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            console.log('PWA: Clearing old cache:', name);
            return caches.delete(name);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event - Fulfills PWA requirement and serves cached static assets when offline
self.addEventListener('fetch', (event) => {
  const request = event.request;

  if (request.method !== 'GET') {
    return;
  }

  const url = new URL(request.url);

  if (url.pathname.includes('/_stcore/') || url.pathname.includes('/stream') || url.pathname.includes('/healthz')) {
    return;
  }

  if (url.pathname.includes('/app/static/') || url.hostname.includes('fonts.gstatic.com')) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, responseToCache));
          }
          return networkResponse;
        }).catch(() => cachedResponse);
      })
    );
  } else {
    event.respondWith(
      fetch(request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, responseToCache));
          }
          return networkResponse;
        })
        .catch(() => {
          return caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }
            return caches.match('/');
          });
        })
    );
  }
});
