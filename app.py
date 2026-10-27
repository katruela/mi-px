from flask import Flask, Response
import requests
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
    
    try:
        res = requests.get(target_page, headers=headers, timeout=10)
        if res.status_code != 200:
            return f"Error HTTP: {res.status_code}", 500
            
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        m3u_content = "#EXTM3U\n"
        count = 0
        
        # Vamos a listar TODOS los enlaces que encuentre la página para ver qué hay dentro
        for link in links:
            href = link.get('href', '')
            texto = link.get_text(strip=True)
            
            # Ignoramos enlaces vacíos o de la propia página principal
            if not href or href == '#' or 'javascript' in href:
                continue
                
            if 'http' not in href:
                stream_url = f"https://streamtp99a.sbs/{href.lstrip('/')}"
            else:
                stream_url = href
                
            nombre_canal = texto if texto and len(texto) > 2 else f"Canal o Enlace {count+1}"
            
            m3u_content += f'#EXTINF:-1 group-title="Todos los Enlaces", {nombre_canal} ({href})\n'
            m3u_content += f'{stream_url}\n'
            count += 1
            
        if count == 0:
            return "La página cargó pero BeautifulSoup no encontró ninguna etiqueta 'a' con href.", 200
            
        return Response(m3u_content, mimetype='audio/x-mpegurl')
        
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
