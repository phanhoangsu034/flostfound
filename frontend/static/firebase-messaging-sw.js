// ====================================================
// firebase-messaging-sw.js - Service Worker bắt buộc
// File này PHẢI đặt ở thư mục gốc (root) của web app
// Vì Flask serve /static/ nên ta cần route đặc biệt
// ====================================================

// Import Firebase scripts cho Service Worker
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

// Firebase config - sẽ được inject bởi Flask template nhưng SW không thể nhận
// nên ta hardcode hoặc fetch từ server
// CẤU HÌNH NÀY SẼ ĐƯỢC ĐỌC TỪ ServiceWorkerRegistration scope data
firebase.initializeApp({
  apiKey: self.FIREBASE_API_KEY || "REPLACE_WITH_API_KEY",
  authDomain: self.FIREBASE_AUTH_DOMAIN || "REPLACE_WITH_AUTH_DOMAIN",
  projectId: self.FIREBASE_PROJECT_ID || "REPLACE_WITH_PROJECT_ID", 
  storageBucket: self.FIREBASE_STORAGE_BUCKET || "REPLACE_WITH_STORAGE_BUCKET",
  messagingSenderId: self.FIREBASE_MESSAGING_SENDER_ID || "REPLACE_WITH_SENDER_ID",
  appId: self.FIREBASE_APP_ID || "REPLACE_WITH_APP_ID"
});

const messaging = firebase.messaging();

// Xử lý background notifications (khi web đóng hoặc tab không active)
messaging.onBackgroundMessage((payload) => {
  console.log('[SW] Background message received:', payload);

  const notificationTitle = payload.notification?.title || 'F-LostFound';
  const notificationOptions = {
    body: payload.notification?.body || 'Bạn có thông báo mới',
    icon: payload.notification?.icon || '/static/icons/icon-192x192.png',
    badge: '/static/icons/badge-72x72.png',
    tag: payload.data?.tag || 'flostfound-notification',
    data: {
      url: payload.data?.url || '/',
      ...payload.data
    },
    vibrate: [200, 100, 200],
    actions: [
      {
        action: 'open',
        title: 'Mở ngay'
      },
      {
        action: 'dismiss', 
        title: 'Bỏ qua'
      }
    ]
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// Xử lý khi người dùng click vào notification
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked:', event);
  event.notification.close();

  const urlToOpen = event.notification.data?.url || '/';

  if (event.action === 'dismiss') {
    return;
  }

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
      // Nếu đã có tab mở sẵn thì focus vào đó
      for (const client of windowClients) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          client.navigate(urlToOpen);
          return client.focus();
        }
      }
      // Nếu chưa có tab nào thì mở tab mới
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});

// Xử lý push event thô (fallback nếu không dùng FCM SDK)
self.addEventListener('push', (event) => {
  if (event.data) {
    try {
      const data = event.data.json();
      console.log('[SW] Raw push event:', data);
    } catch (e) {
      console.log('[SW] Raw push text:', event.data.text());
    }
  }
});
