// Service Worker for PWA and Push Notifications
const CACHE_NAME = 'halaqat-v2'; // تم التحديث لإجبار المتصفح على تحديث الكاش
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/images/logo.png'
];

// تثبيت Service Worker
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

// تفعيل Service Worker
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// التعامل مع الطلبات - استراتيجية Network First
self.addEventListener('fetch', event => {
    event.respondWith(
        fetch(event.request)
            .then(response => {
                // حفظ نسخة جديدة في الكاش فقط إذا كان الطلب GET
                if (event.request.method === 'GET') {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            })
            .catch(() => {
                // إذا فشل الاتصال، استخدم الكاش
                return caches.match(event.request);
            })
    );
});

// استقبال الإشعارات Push
self.addEventListener('push', event => {
    console.log('Push notification received:', event);

    let data = {
        title: 'إشعار جديد',
        body: 'لديك إشعار جديد',
        icon: '/static/images/logo.png',
        badge: '/static/images/badge.png',
        url: '/'
    };

    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            console.error('Error parsing notification data:', e);
        }
    }

    const options = {
        body: data.body,
        icon: data.icon || '/static/images/logo.png',
        badge: data.badge || '/static/images/badge.png',
        data: {
            url: data.url || '/'
        },
        vibrate: [200, 100, 200],
        tag: 'halaqat-notification',
        requireInteraction: false,
        dir: 'rtl', // للغة العربية
        lang: 'ar'
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// التعامل مع النقر على الإشعار
self.addEventListener('notificationclick', event => {
    console.log('Notification clicked:', event);

    event.notification.close();

    const urlToOpen = event.notification.data.url || '/';

    event.waitUntil(
        clients.matchAll({
            type: 'window',
            includeUncontrolled: true
        })
            .then(windowClients => {
                // البحث عن نافذة مفتوحة بالفعل
                for (let client of windowClients) {
                    if (client.url === urlToOpen && 'focus' in client) {
                        return client.focus();
                    }
                }
                // فتح نافذة جديدة إذا لم تكن موجودة
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});
