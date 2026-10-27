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
                href = link.get('href', '').strip()
                texto = link.get_text(strip=True)
                
                if not href or href == '#' or href == '/' or 'index' in href:
                    continue
                
                if '.php' in href or 'ver' in href or 'play' in href or 'stream' in href:
                    if 'http' not in href:
                        stream_url = f"https://streamtp99a.sbs/{href.lstrip('/')}"
                    else:
                        stream_url = href
                        
                    if stream_url in ['https://streamtp99a.sbs/', 'https://streamtp99a.sbs']:
                        continue
                        
                    nombre_canal = texto if texto and len(texto) > 2 and texto not in ["Ver", "Copiar"] else f"Evento Deportivo {canal_idx}"
                    
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
        # 1. Entramos a la página del evento
        res = requests.get(target_url, headers=headers, timeout=10)
        if res.status_code == 200:
            # Buscamos el .m3u8 directamente por si está a la vista
            match = re.search(r'https?://[^\s"\']+\.m3u8[^\s"\']*', res.text)
            if match:
                return redirect(match.group(0))
            
            # 2. Si no está a la vista, buscamos si hay un reproductor embebido (iframe)
            soup = BeautifulSoup(res.text, 'html.parser')
            iframe = soup.find('iframe', src=True)
            if iframe:
                iframe_src = iframe['src']
                if 'http' not in iframe_src:
                    if iframe_src.startswith('/'):
                        iframe_url = f"https://streamtp99a.sbs{iframe_src}"
                    else:
                        iframe_url = f"{target_url.rsplit('/', 1)[0]}/{iframe_src}"
                else:
                    iframe_url = iframe_src
                
                # Entramos al iframe a buscar el video real
                headers['Referer'] = target_url
                res_iframe = requests.get(iframe_url, headers=headers, timeout=10)
                if res_iframe.status_code == 200:
                    match_iframe = re.search(r'https?://[^\s"\']+\.m3u8[^\s"\']*', res_iframe.text)
                    if match_iframe:
                        return redirect(match_iframe.group(0))
                        
    except Exception as e:
        print(f"Error resolviendo stream: {e}")
        
    return "No se pudo extraer el stream de este evento", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
