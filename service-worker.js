// 番茄时钟 PWA Service Worker
const CACHE_NAME = 'pomodoro-timer-v1';
const ASSETS_TO_CACHE = [
    './',
    './index.html',
    './styles.css',
    './script.js',
    './manifest.json',
    './icons/icon.svg'
];

// 安装事件 - 缓存所有静态资源
self.addEventListener('install', (event) => {
    console.log('[Service Worker] 安装中...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[Service Worker] 缓存静态资源');
                return cache.addAll(ASSETS_TO_CACHE);
            })
            .then(() => {
                console.log('[Service Worker] 安装完成');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('[Service Worker] 缓存失败:', error);
            })
    );
});

// 激活事件 - 清理旧缓存
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] 激活中...');
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== CACHE_NAME) {
                            console.log('[Service Worker] 删除旧缓存:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('[Service Worker] 激活完成');
                return self.clients.claim();
            })
    );
});

// 请求拦截 - 优先使用缓存，失败则请求网络
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((cachedResponse) => {
                if (cachedResponse) {
                    return cachedResponse;
                }

                return fetch(event.request)
                    .then((response) => {
                        // 检查是否是有效的响应
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // 克隆响应（因为响应流只能读取一次）
                        const responseToCache = response.clone();

                        caches.open(CACHE_NAME)
                            .then((cache) => {
                                cache.put(event.request, responseToCache);
                            });

                        return response;
                    })
                    .catch(() => {
                        // 网络请求失败，返回离线页面（如果请求的是HTML）
                        if (event.request.headers.get('accept')?.includes('text/html')) {
                            return caches.match('./index.html');
                        }
                    });
            })
    );
});

// 监听消息
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});
