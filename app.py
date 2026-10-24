from flask import Flask, redirect
import requests
import re

app = Flask(__name__)

@app.route('/')
def home():
    return "Proxy IPTV funcionando correctamente", 200

@app.route('/stream/<id_canal>')
def proxy_stream(id_canal):
    iframe_url = f'https://thedaddy.pk/stream/stream-{id_canal}.php'
    
    # Cabeceras avanzadas para imitar a un navegador web real y evitar bloqueos
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://thedaddy.pk/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    try:
        res = requests.get(iframe_url, headers=headers, timeout=8)
        print(f"Status Code recibido: {res.status_code}")
        
        if res.status_code == 200:
            html = res.text
            
            # Buscar cualquier enlace .m3u8 dentro del código
            match = re.search(r'https?://[^\s"\']+\.m3u8[^\s"\']*', html)
            if match:
                m3u8_url = match.group(0)
                print(f"Stream encontrado: {m3u8_url}")
                return redirect(m3u8_url)
            else:
                print("No se encontró el patrón .m3u8 en el HTML recibido.")
        else:
            print(f"La página bloqueó la petición con código: {res.status_code}")
                
    except Exception as e:
        print(f"Error en la petición: {e}")
        
    return "No se pudo obtener el stream del canal", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
