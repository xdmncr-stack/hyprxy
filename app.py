from flask import Flask, redirect, Response
import requests
import re
import base64
import json
import os
import time

app = Flask(__name__)

def get_huya_v4(room_id):
    # Menggunakan kombinasi User-Agent PC dan Mobile
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Referer': f'https://www.huya.com/{room_id}',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }

    try:
        # Step 1: Ambil halaman utama untuk mendapatkan session/cookie dasar
        session = requests.Session()
        res = session.get(f"https://www.huya.com/{room_id}", headers=headers, timeout=10)
        
        # Step 2: Cari data stream di dalam tag script HY_ROOM_CONFIG atau HNF_GLOBAL_CONF
        pattern = r'"stream":\s*"(.+?)"'
        stream_base64 = re.findall(pattern, res.text)
        
        if not stream_base64:
            # Pola cadangan: mencari langsung di dalam JSON config
            pattern_alt = r'window\.HNF_GLOBAL_CONF\s*=\s*(\{.+?\})'
            config_json = re.findall(pattern_alt, res.text)
            if config_json:
                data = json.loads(config_json[0])
                stream_info = data.get('roomInfo', {}).get('tLiveInfo', {}).get('tLiveStreamInfo', {}).get('vStreamInfo', {}).get('value', [])
                if stream_info:
                    # Ambil stream pertama dan rakit URL
                    s = stream_info[0]
                    url = f"{s['sFlvUrl']}/{s['sStreamName']}.m3u8?{s['sFlvAntiCode']}"
                    return url.replace('http://', 'https://').replace('&amp;', '&')

        if stream_base64:
            # Decode data stream yang di-encode base64 oleh Huya
            decoded_data = json.loads(base64.b64decode(stream_base64[0]).decode('utf-8'))
            v_stream_info = decoded_data.get('data', [{}])[0].get('gameStreamInfoList', [])
            
            if v_stream_info:
                s = v_stream_info[0]
                # Menggunakan sHlsUrl untuk format m3u8
                final_url = f"{s['sHlsUrl']}/{s['sStreamName']}.{s['sHlsUrlSuffix']}?{s['sHlsAntiCode']}"
                return final_url.replace('&amp;', '&')

    except Exception as e:
        print(f"Error v4: {e}")
    
    return None

@app.route('/')
def health_check():
    return "Huya Resolver V4 Online"

@app.route('/play/<room_id>')
def play(room_id):
    stream_url = get_huya_v4(room_id)
    if stream_url:
        # Gunakan status 302 agar player (VLC/TiviMate) langsung diarahkan ke sumber asli
        return redirect(stream_url, code=302)
    return "Offline atau Terblokir. Coba 'Manual Deploy' di Render.", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
