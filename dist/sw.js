/* Service worker de Aleister's Codex: la página se instala y abre sin conexión.
   - Navegación (index.html) y data/*.js: primero la red (siempre lo más nuevo) y, si no hay red, lo último que se guardó.
   - art/, sheets/ y fuentes: primero lo guardado y se refresca por detrás (no cambian de un día para otro).
   - Lo de otros dominios (imágenes de cartas, dolarapi) no se toca: cada uno maneja sus propios errores.
   La versión llega en la dirección (sw.js?v=FECHA-DEL-BUILD): cada publicación distinta crea cachés nuevos y borra los anteriores. */
const V = new URL(self.location.href).searchParams.get('v') || 'dev';
const SHELL = 'codex-shell-' + V, DATA = 'codex-data-' + V, STATIC = 'codex-static-1';
const KEEP = [SHELL, DATA, STATIC];

self.addEventListener('install', e => { self.skipWaiting(); e.waitUntil(caches.open(SHELL).then(c => c.addAll(['./', 'manifest.webmanifest', 'art/icon-192.png']).catch(() => {}))); });
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('codex-') && !KEEP.includes(k)).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

async function networkFirst(req, cacheName, fallbackUrl) {
  const c = await caches.open(cacheName);
  try {
    const r = await fetch(req);
    if (r && r.ok) c.put(req, r.clone());
    return r;
  } catch (err) {
    return (await c.match(req)) || (fallbackUrl && await c.match(fallbackUrl)) || Response.error();
  }
}
async function staleWhileRevalidate(req, cacheName) {
  const c = await caches.open(cacheName);
  const hit = await c.match(req);
  const net = fetch(req).then(r => { if (r && r.ok) c.put(req, r.clone()); return r; }).catch(() => null);
  return hit || (await net) || Response.error();
}

self.addEventListener('fetch', e => {
  const req = e.request, u = new URL(req.url);
  if (req.method !== 'GET' || u.origin !== location.origin) return;
  if (req.headers.has('range')) return;
  if (req.mode === 'navigate') { e.respondWith(networkFirst(req, SHELL, './')); return; }
  if (/\/data\/[^/]+\.js$/.test(u.pathname)) { e.respondWith(networkFirst(req, DATA)); return; }
  if (/\/(art|sheets|og|images)\//.test(u.pathname) || /\.(woff2|webmanifest)$/.test(u.pathname)) { e.respondWith(staleWhileRevalidate(req, STATIC)); return; }
});
