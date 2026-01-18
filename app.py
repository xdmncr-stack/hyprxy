from flask import Flask, redirect, Response
import requests
import re
import json
import os

app = Flask(__name__)

def get_huya_live(room_id):
    # Menggunakan API yang lebih stabil untuk mobile
    api_url = f"https://mp.huya.com/cache.php?m=Live&do=profileRoom&roomid={room_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36',
        'Referer': 'https://mp.huya.com/'
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        data = response.json()
        
        # Mengecek apakah status room sedang LIVE
        if data.get('status') == 200 and data['data']['liveStatus'] == 'ON':
            # Mengambil URL stream m3u8
            stream_info = data['data']['stream']['base_stream_list'][0]
            s_url = stream_info['m3u8_url']
            
            # Membersihkan URL dari karakter escape agar bisa diputar
            clean_url = s_url.replace('\\', '')
            return clean_url
            
    except Exception as e:
        print(f"Error: {e}")
    
    return None

@app.route('/')
def index():
    return "Hyprxy API v3 is Online"

@app.route('/play/<room_id>')
def play(room_id):
    stream_url = get_huya_live(room_id)
    if stream_url:
        # Langsung mengalihkan ke link m3u8 asli
        return redirect(stream_url, code=302)
    return "Gagal mengambil stream. Room mungkin offline atau IP Render diblokir.", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
