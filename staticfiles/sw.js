// Service Worker para PWA GestorTickets
// Versión SIN CACHE - Solo para hacer la app instalable
const VERSION = 'v1.0.13-no-cache';

// Instalar Service Worker
self.addEventListener('install', (event) => {
    console.log(`Service Worker ${VERSION}: Instalado (sin cache)`);
    // Activar inmediatamente el nuevo service worker
    self.skipWaiting();
});

// Activar Service Worker y limpiar TODOS los caches antiguos
self.addEventListener('activate', (event) => {
    console.log(`Service Worker ${VERSION}: Activado`);
    
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            // Eliminar TODOS los caches existentes
            return Promise.all(
                cacheNames.map((cacheName) => {
                    console.log(`Service Worker: Eliminando cache ${cacheName}`);
                    return caches.delete(cacheName);
                })
            );
        }).then(() => {
            // Tomar control de todas las páginas inmediatamente
            return self.clients.claim();
        })
    );
});

// NO interceptar peticiones - dejar que todo pase directo a la red
self.addEventListener('fetch', (event) => {
    // No hacer nada, dejar que todas las peticiones pasen normalmente
    // Esto asegura que siempre se obtenga contenido fresco del servidor
    return;
});

// Manejar mensajes desde el cliente
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    // Mensaje para limpiar cache manualmente si es necesario
    if (event.data && event.data.type === 'CLEAR_CACHE') {
        event.waitUntil(
            caches.keys().then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => caches.delete(cacheName))
                );
            }).then(() => {
                return self.clients.matchAll();
            }).then((clients) => {
                clients.forEach(client => {
                    client.postMessage({
                        type: 'CACHE_CLEARED',
                        message: 'Cache eliminado exitosamente'
                    });
                });
            })
        );
    }
});