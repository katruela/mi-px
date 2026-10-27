from flask import Flask, redirect, Response
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
        
        # Si la web externa nos bloquea o da error, te lo mostraremos en pantalla
        if res.status_code != 200:
            return f"Error: La web externa respondio con el codigo de bloqueo {res.status_code}", 500
            
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        m3u_content = "#EXTM3U\n"
        count = 0
        
        for link in links:
            href = link.get('href', '')
            texto = link.get_text(strip=True)
            
            # Buscamos cualquier enlace que parezca un stream o php
            if '.php' in href or 'stream' in href or 'global' in href or 'embed' in href:
                if 'http' not in href:
                    stream_url = f"https://streamtp99a.sbs/{href.lstrip('/')}"
                else:
                    stream_url = href
                    
                nombre_canal = texto if texto and texto not in ["Ver", "Copiar", ""] else f"Evento {count+1}"
                
                m3u_content += f'#EXTINF:-1 group-title="Eventos En Vivo", {nombre_canal}\n'
                m3u_content += f'https://mi-px.onrender.com/resolver?url={stream_url}\n'
                count += 1
                
        # Si leyó la página pero no encontró enlaces, te avisará en vez de dar un archivo vacío
        if count == 0:
            return f"Aviso: Render entro a la web (tamano: {len(res.text)} bytes), pero la estructura cambio y no encontro enlaces de eventos.", 200
            
        return Response(m3u_content, mimetype='audio/x-mpegurl')
        
    except Exception as e:
        return f"Error de conexion: {str(e)}", 500

@app.route('/resolver')
def resolver_stream():
    from flask import request
    target_url = request.args.get('url')
    if not target_url:
        return "URL no especificada", 400
    return redirect(target_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
