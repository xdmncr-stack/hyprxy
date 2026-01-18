from flask import Flask, redirect
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Hyprxy M3U8 Resolver Active"

@app.route('/play/<room_id>')
def play(room_id):
    # API ini sering digunakan oleh playlist m3u populer
    url = f"https://mp.huya.com/cache.php?m=Live&do=profileRoom&roomid={room_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        # Mengambil URL m3u8 dari data stream
        m3u8_url = data['data']['stream']['base_stream_list'][0]['m3u8_url']
        if m3u8_url:
            return redirect(m3u8_url, code=302)
    except:
        pass
        
    return "Gagal mengambil stream. IP Render kemungkinan besar diblokir oleh Huya.", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
