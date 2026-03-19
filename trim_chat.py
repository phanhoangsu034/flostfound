path = r"c:\Users\dell 5411\Desktop\JS-CLUB\LÀM PROJECT\CTV-Team-1X-BET-23-1\frontend\templates\messages\chat.html"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

js_replacement = """    // ==========================================
    // KHỞI TẠO CUỘC GỌI TOÀN CỤC CHẠY BÊN BASE.HTML
    // ==========================================
    const startVideoCallBtn = document.getElementById('startVideoCallBtn');
    const startVoiceCallBtn = document.getElementById('startVoiceCallBtn');

    if (startVideoCallBtn) {
        startVideoCallBtn.addEventListener('click', () => {
            if (window.startWebRTCCall) {
                window.startWebRTCCall(recipientId, '{{ recipient.username }}', '{{ recipient.avatar }}', true);
            }
        });
    }

    if (startVoiceCallBtn) {
        startVoiceCallBtn.addEventListener('click', () => {
            if (window.startWebRTCCall) {
                window.startWebRTCCall(recipientId, '{{ recipient.username }}', '{{ recipient.avatar }}', false);
            }
        });
    }

"""

lines[229:555] = [js_replacement]
lines[75:155] = []
lines[37:45] = [
    '        <!-- Audio for notification -->\n',
    '        <audio id="notifSound" src="https://www.myinstants.com/media/sounds/discord-notification.mp3" preload="auto"></audio>\n'
]

with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)
print("Done")
