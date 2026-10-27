from flask import Flask, redirect, Response, request
import requests
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return "Proxy de Eventos IPTV funcionando. Usa /playlist.m3u en tu reproductor.", 200

@app.route('/playlist.m3u')
def generar_playlist():
    target_page = 'https://streamtp99a.sbs/eventos.html'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://streamtp99a.sbs/'
    }
    
    m3u_content = "#EXTM3U\n"
    
    try:
        res = requests.get(target_page, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            links = soup.find_all('a', href=True)
            
            canal_idx = 1
            for link in links:
                href = link.get('href', '')
                texto = link.get_text(strip=True)
                
                # Filtramos los enlaces que llevan a las transmisiones y páginas de eventos
                if '.php' in href or 'stream' in href or 'play' in href or 'ver' in href:
                    if 'http' not in href:
                        stream_url = f"https://streamtp99a.sbs/{href.lstrip('/')}"
                    else:
                        stream_url = href
                        
                    nombre_canal = texto if texto and len(texto) > 2 and texto not in ["Ver", "Copiar"] else f"Evento Deportivo {canal_idx}"
                    
                    # Cada canal apunta a nuestro /resolver para que extraiga el video real al hacer clic
                    m3u_content += f'#EXTINF:-1 group-title="Eventos En Vivo", {nombre_canal}\n'
                    m3u_content += f'https://mi-px.onrender.com/resolver?url={stream_url}\n'
                    canal_idx += 1
    except Exception as e:
        print(f"Error generando la lista: {e}")
        
    return Response(m3u_content, mimetype='audio/x-mpegurl')

@app.route('/resolver')
def resolver_stream():
    target_url = request.args.get('url')
    if not target_url:
        return "URL no especificada", 400
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://streamtp99a.sbs/'
    }
    
    try:
        res = requests.get(target_url, headers=headers, timeout=10)
        if res.status_code == 200:
            # Buscamos el enlace de video real (.m3u8) oculto dentro del código del evento
            match = re.search(r'https?://[^\s"\']+\.m3u8[^\s"\']*', res.text)
            if match:
                return redirect(match.group(0))
    except Exception as e:
        print(f"Error resolviendo stream: {e}")
        
    return "No se pudo extraer el stream de este evento", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
