const CACHE_NAME = 'FuY-v24';
const ASSETS = ['./manifest.json', './icon-192.png', './icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
      .catch(err => console.log('Cache error:', err))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;

  const url = new URL(e.request.url);
  const isHTML = e.request.destination === 'document' || url.pathname.endsWith('.html');
  const isJSON = url.pathname.endsWith('.json') || url.hostname === 'api.github.com' || url.hostname === 'raw.githubusercontent.com';

  // HTML، JSON و همه درخواست‌های GitHub: همیشه از شبکه، هیچ‌وقت cache نشن
  if (isHTML || isJSON) {
    e.respondWith(
      fetch(e.request, { cache: 'no-store' })
        .then(resp => resp)
        .catch(() => caches.match(e.request))
    );
    return;
  }

  // بقیه فایل‌ها (آیکون‌ها و...): cache-first
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(resp => {
        if (resp && resp.status === 200) {
          const clone = resp.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
        }
        return resp;
      });
    })
  );
});
