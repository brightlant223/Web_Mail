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

// --- Web Push: show a notification even when the app/tab is closed ---
self.addEventListener('push', event => {
  let payload = {};
  try { payload = event.data ? event.data.json() : {}; } catch (e) { payload = {}; }
  const title = payload.title || 'Brightlant Webmail';
  const options = {
    body: payload.body || 'You have a new alert.',
    icon: '/static/images/icon-192.png',
    badge: '/static/images/icon-192.png',
    tag: payload.tag || 'brightlant-alert',
    data: { url: payload.url || '/notifications' },
    vibrate: [120, 60, 120]
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  const target = (event.notification.data && event.notification.data.url) || '/notifications';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(list => {
      for (const client of list) {
        if ('focus' in client) { client.navigate(target); return client.focus(); }
      }
      if (clients.openWindow) return clients.openWindow(target);
    })
  );
});
