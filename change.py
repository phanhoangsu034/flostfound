import sys
import re

chat_path = r'c:\Users\dell 5411\Desktop\JS-CLUB\LÀM PROJECT\CTV-Team-1X-BET-23-1\frontend\templates\messages\chat.html'

with open(chat_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Strip audio
text = re.sub(r'<!-- Audio for notification & Calls -->[\s\S]*?{% for msg in messages %}', '<!-- Audio for notification -->\n        <audio id="notifSound" src="https://www.myinstants.com/media/sounds/discord-notification.mp3" preload="auto"></audio>\n\n        {% for msg in messages %}', text)

# 2. Strip Modals
text = re.sub(r'<!-- Incoming Call Modal -->[\s\S]*?{% endblock %}', '{% endblock %}', text)

# 3. Strip WebRTC JS
js_replacement = '''    // ==========================================
    // KÍCH HOẠT GỌI GLOBAL WEBRTC
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

</script>'''

text = re.sub(r'// ==========================================[\s\S]*// WebRTC VIDEO CALL LOGIC \(Peer-to-Peer\)[\s\S]*?</script>', js_replacement, text)

with open(chat_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Done')
