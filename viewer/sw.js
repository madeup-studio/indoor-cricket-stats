// Minimal service worker: it exists so Android offers "Install app". Every request
// goes straight to the network (no caching), so the stats are never stale.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()));
self.addEventListener("fetch", (event) => {
  event.respondWith(fetch(event.request));
});
