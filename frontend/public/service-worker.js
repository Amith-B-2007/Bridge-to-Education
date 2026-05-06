const CACHE_STATIC = 'static-v1';
const CACHE_API = 'api-v1';

const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json'
];

// Install: cache static assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_STATIC)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate: clean old caches, claim all clients
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(names => Promise.all(
        names
          .filter(name => name !== CACHE_STATIC && name !== CACHE_API)
          .map(name => caches.delete(name))
      ))
      .then(() => self.clients.claim())
  );
});

// Fetch: intelligent routing
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // API requests: network-first with API cache fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_API).then(cache => {
              cache.put(request, clone);
            });
          }
          return response;
        })
        .catch(error => {
          return caches.match(request)
            .then(cached => cached || new Response(
              JSON.stringify({ error: 'Offline - no cached data available' }),
              { status: 503, statusText: 'Service Unavailable' }
            ));
        })
    );
  }
  // Static assets: cache-first
  else {
    event.respondWith(
      caches.match(request)
        .then(response => response || fetch(request))
        .catch(() => caches.match('/index.html'))
    );
  }
});

// Background sync
self.addEventListener('sync', event => {
  if (event.tag === 'sync-pending-actions') {
    event.waitUntil(syncPendingActions());
  }
});

async function syncPendingActions() {
  const clients = await self.clients.matchAll();
  clients.forEach(client => {
    client.postMessage({
      type: 'SYNC_PENDING_ACTIONS'
    });
  });
}
