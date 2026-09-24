// Brightlant Webmail PWA Service Worker
const CACHE_NAME = 'brightlant-webmail-v2';

// Only precache assets that are public and reliably return 200.
// (Pages like /inbox require login and would 302 — never precache those.)
const urlsToCache = [
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/images/logo.png',
  '/static/images/icon-192.png',
  '/static/images/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache =>
      // Cache each item independently so one missing file can't fail the whole install.
      Promise.all(urlsToCache.map(url =>
        cache.add(url).catch(err => console.log('SW precache skip:', url, err))
      ))
    )
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(name => name !== CACHE_NAME).map(name => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
