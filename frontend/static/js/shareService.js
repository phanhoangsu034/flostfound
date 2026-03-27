// Multi-platform Sharing Service for F-LostFound

export const ShareService = {
    // 1. Cấu hình các nền tảng
    providers: {
        facebook: (url) => `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
        messenger: (url) => {
            const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            if (isMobile) return `fb-messenger://share?link=${encodeURIComponent(url)}`;
            return `https://www.facebook.com/dialog/send?link=${encodeURIComponent(url)}&app_id=2143054175924294&redirect_uri=${encodeURIComponent(url)}`;
        },
        zalo: (url) => `https://zalo.me/s/share?url=${encodeURIComponent(url)}`,
        twitter: (url, title) => `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`,
        whatsapp: (url, title) => `https://api.whatsapp.com/send?text=${encodeURIComponent(title + " " + url)}`,
    },

    // 2. Hàm xử lý chính (Native Share trên Mobile)
    async initShare(data) {
        const { title, text, url } = data;
        const trackedUrl = url.includes('?') ? `${url}&utm_source=f_lostfound_share` : `${url}?utm_source=f_lostfound_share`;

        // Kiểm tra xem có phải thiết bị di động không
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

        // Chỉ dùng Native Share trên Mobile và nếu browser hỗ trợ
        if (isMobile && navigator.share) {
            try {
                await navigator.share({
                    title: title,
                    text: text,
                    url: trackedUrl
                });
                return { success: true, method: 'native', trackedUrl };
            } catch (err) {
                console.log("[ShareService] Native share cancelled or error:", err);
                if (err.name === 'AbortError') return { success: false, method: 'cancelled' };
            }
        }
        
        // Nếu là Desktop hoặc Mobile không hỗ trợ Native Share, dùng Modal tùy chỉnh
        return { success: false, method: 'modal', trackedUrl };
    },

    // 3. Sao chép liên kết vào bộ nhớ tạm
    async copyLink(url) {
        try {
            await navigator.clipboard.writeText(url);
            return true;
        } catch (err) {
            console.error('[ShareService] Lỗi copy:', err);
            // Fallback cho browser cũ không có clipboard API
            const textArea = document.createElement("textarea");
            textArea.value = url;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand("copy");
            document.body.removeChild(textArea);
            return true;
        }
    }
};
