from flask import Flask, redirect
import requests
import re
import base64
import json
import os

app = Flask(__name__)

def get_huya_fresh_url(room_id):
    # Header untuk mensimulasikan browser mobile agar mendapatkan token
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        'Referer': f'https://m.huya.com/{room_id}'
    }
    try:
        # Mengambil data terbaru dari server Huya
        res = requests.get(f"https://m.huya.com/{room_id}", headers=headers, timeout=10)
        data_decode = re.findall(r'data-decode="(.+?)"', res.text)
        
        if data_decode:
            decoded = base64.b64decode(data_decode[0]).decode('utf-8')
            # Mengambil informasi stream pertama (biasanya kualitas tertinggi)
            stream_info = json.loads(decoded)['vStreamInfo'][0]
            # Membuat link m3u8 dengan token wsSecret yang baru
            return f"http://{stream_info['sFlvUrl']}/{stream_info['sStreamName']}.m3u8?{stream_info['sFlvAntiCode']}"
    except Exception as e:
        print(f"Error: {e}")
    return None

@app.route('/')
def home():
    return "Huya Resolver is Running!"

@app.route('/play/<room_id>')
def serve_stream(room_id):
    # Mencari link yang tidak expired setiap kali link diakses
    link = get_huya_fresh_url(room_id)
    if link:
        # Mengarahkan player ke link asli yang aktif (Redirect 302)
        return redirect(link, code=302)
    return "Stream Offline atau Room ID Salah", 404

if __name__ == "__main__":
    # Render membutuhkan port dinamis yang ditentukan oleh sistem mereka
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
