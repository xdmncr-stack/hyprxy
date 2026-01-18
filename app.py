from flask import Flask, redirect
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Hyprxy Bypass Active"

@app.route('/play/<room_id>')
def play(room_id):
    # Menggunakan API m.huya.com yang paling simpel
    target_url = f"https://mp.huya.com/cache.php?m=Live&do=profileRoom&roomid={room_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
    }
    
    try:
        r = requests.get(target_url, headers=headers, timeout=5)
        data = r.json()
        
        # Ambil link m3u8 langsung dari data JSON
        # Huya menyediakan beberapa jalur (multi-line), kita ambil yang pertama
        stream_url = data['data']['stream']['base_stream_list'][0]['m3u8_url']
        
        if stream_url:
            # Redirect ke link asli
            return redirect(stream_url.replace('\\', ''), code=302)
    except:
        pass
        
    return "IP Server Render diblokir oleh Huya. Silakan coba ganti Region di Settings.", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
