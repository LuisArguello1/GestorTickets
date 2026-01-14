// Service Worker para PWA GestorTickets
const CACHE_NAME = 'gestortickets-v1.0.0';
const STATIC_CACHE = 'gestortickets-static-v1.0.0';
const DYNAMIC_CACHE = 'gestortickets-dynamic-v1.0.0';

// Archivos a cachear inicialmente
const STATIC_ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/css/base.css',
    '/static/css/message.css',
    '/static/css/loading.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.min.css',
    'https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.min.js'
];

// Instalar Service Worker
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                return cache.addAll(STATIC_ASSETS);
            })
            .catch((error) => {
                console.error('Service Worker: Error al cachear archivos estáticos:', error);
            })
    );
    self.skipWaiting();
});

// Activar Service Worker
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Interceptar peticiones
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Solo cachear peticiones GET
    if (request.method !== 'GET') return;

    // Estrategia Cache First para archivos estáticos
    if (STATIC_ASSETS.some(asset => request.url.includes(asset))) {
        event.respondWith(
            caches.match(request)
                .then((response) => {
                    if (response) {
                        return response;
                    }
                    return fetch(request)
                        .then((response) => {
                            if (response.status === 200) {
                                const responseClone = response.clone();
                                caches.open(STATIC_CACHE)
                                    .then((cache) => {
                                        cache.put(request, responseClone);
                                    });
                            }
                            return response;
                        });
                })
        );
        return;
    }

    // Estrategia Network First para páginas dinámicas
    if (request.destination === 'document' ||
        url.pathname.startsWith('/ticket/') ||
        url.pathname.startsWith('/company/') ||
        url.pathname === '/dashboard/') {

        event.respondWith(
            fetch(request)
                .then((response) => {
                    if (response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(DYNAMIC_CACHE)
                            .then((cache) => {
                                cache.put(request, responseClone);
                            });
                    }
                    return response;
                })
                .catch(() => {
                    return caches.match(request)
                        .then((response) => {
                            if (response) {
                                return response;
                            }
                            // Página offline básica
                            if (request.destination === 'document') {
                                return caches.match('/')
                                    .then((response) => response || new Response('Offline', { status: 503 }));
                            }
                        });
                })
        );
        return;
    }

    // Default: Network first con fallback a cache
    event.respondWith(
        fetch(request)
            .then((response) => {
                if (response.status === 200) {
                    const responseClone = response.clone();
                    caches.open(DYNAMIC_CACHE)
                        .then((cache) => {
                            cache.put(request, responseClone);
                        });
                }
                return response;
            })
            .catch(() => {
                return caches.match(request);
            })
    );
});

// Manejar mensajes desde el cliente
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});