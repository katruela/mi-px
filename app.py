from flask import Flask, redirect, Response
import requests
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return "Proxy de Eventos IPTV funcionando. Usa /playlist.m3u en tu reproductor.", 200

# Ruta principal que genera la lista M3U automáticamente leyendo la web de eventos
@app.route('/playlist.m3u')
def generar_playlist():
    target_page = 'https://streamtp99a.sbs/eventos.html'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://streamtp99a.sbs/'
    }
    
    m3u_content = "#EXTM3U\n"
    
    try:
        res = requests.get(target_page, headers=headers, timeout=8)
        if res.status_code == 200:
            # Usamos BeautifulSoup para buscar los eventos y sus enlaces
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Buscamos los bloques de partidos (ajustado a la estructura típica de estas webs)
            # Esto busca elementos que contengan los botones de reproducción o enlaces de los streams
            links = soup.find_all('a', href=True)
            
            canal_idx = 1
            for link in links:
                href = link['href']
                texto = link.get_text(strip=True)
                
                # Filtramos los enlaces internos que llevan a las transmisiones
                if 'embed' in href or 'stream' in href or 'play' in href:
                    if 'http' not in href:
                        stream_url = f"https://streamtp99a.sbs/{href.lstrip('/')}"
                    else:
                        stream_url = href
                        
                    # Limpiamos el nombre para que se vea bien en el Roku / VLC
                    nombre_canal = f"Evento {canal_idx}"
                    
                    # Añadimos el item a la lista M3U apuntando a nuestro propio proxy en Render
                    m3u_content += f'#EXTINF:-1 group-title="Eventos En Vivo", {nombre_canal}\n'
                    m3u_content += f'https://mi-px.onrender.com/resolver?url={stream_url}\n'
                    canal_idx += 1
                    
    except Exception as e:
        print(f"Error generando la lista: {e}")
        
    return Response(m3u_content, mimetype='audio/x-mpegurl')

# Ruta que resuelve el enlace del evento y te manda al video real (.m3u8)
@app.route('/resolver')
def resolver_stream():
    from flask import request
    target_url = request.args.get('url')
    
    if not target_url:
        return "URL no especificada", 400
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://streamtp99a.sbs/'
    }
    
    try:
        res = requests.get(target_url, headers=headers, timeout=8)
        if res.status_code == 200:
            # Buscamos el enlace .m3u8 oculto dentro del reproductor del evento
            match = re.search(r'https?://[^\s"\']+\.m3u8[^\s"\']*', res.text)
            if match:
                return redirect(match.group(0))
    except Exception as e:
        print(f"Error resolviendo stream: {e}")
        
    return "No se pudo extraer el stream de este evento", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
