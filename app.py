from flask import Flask, redirect, Response
import requests
import re
import base64
import json
import os

app = Flask(__name__)

def get_huya_fresh_url(room_id):
    # Header diperkuat agar benar-benar terlihat seperti HP asli
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
        'Referer': f'https://m.huya.com/{room_id}',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }
    
    try:
        url = f"https://m.huya.com/{room_id}"
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        
        # Mencari data stream di dalam tag script atau atribut data-decode
        data_decode = re.findall(r'data-decode="(.+?)"', res.text)
        
        if not data_decode:
            # Cara cadangan jika format di atas gagal
            data_decode = re.findall(r'window\.HNF_GLOBAL_CONF\s*=\s*(\{.+?\})', res.text)

        if data_decode:
            try:
                # Coba decode base64
                decoded = base64.b64decode(data_decode[0]).decode('utf-8')
                stream_data = json.loads(decoded)
            except:
                # Jika bukan base64, coba parse JSON langsung
                stream_data = json.loads(data_decode[0])
            
            # Ambil info stream kualitas terbaik
            v_info = stream_data.get('vStreamInfo', []) or stream_data.get('roomInfo', {}).get('tLiveInfo', {}).get('tLiveStreamInfo', {}).get('vStreamInfo', {}).get('value', [])
            
            if v_info:
                s_info = v_info[0]
                # Rakit URL m3u8
                # Kadang sFlvUrl berisi protokol http/https, kita bersihkan agar aman
                base_url = s_info['sFlvUrl'].replace('http://', '').replace('https://', '')
                final_link = f"http://{base_url}/{s_info['sStreamName']}.m3u8?{s_info['sFlvAntiCode']}"
                
                # Bersihkan karakter &amp; yang sering merusak link
                final_link = final_link.replace('&amp;', '&')
                return final_link
                
    except Exception as e:
        print(f"Error detail: {e}")
        
    return None

@app.route('/')
def home():
    return "Server Hyprxy Aktif di Singapore!"

@app.route('/play/<room_id>')
def serve_stream(room_id):
    link = get_huya_fresh_url(room_id)
    if link:
        # Gunakan redirect 302 agar player langsung ke sumber asli
        return redirect(link, code=302)
    return "Stream Offline atau Room ID Salah. Pastikan room sedang LIVE.", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
