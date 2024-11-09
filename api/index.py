import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request

app = Flask(__name__)

# Função para buscar o link da página do filme
def buscar_pagina_filme(titulo):
    url_pesquisa = "https://wix.maxcine.top/public/pesquisa"
    params = {"search": titulo}

    response = requests.get(url_pesquisa, params=params)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    link_pagina_filme = None
    for link in soup.find_all('a', href=True):
        if "/public/filme/" in link['href']:
            link_pagina_filme = link['href']
            break

    if link_pagina_filme:
        return f"https://wix.maxcine.top{link_pagina_filme}"
    else:
        return None

# Função para buscar o link de reprodução do vídeo
def buscar_link_play(url_pagina_filme):
    response = requests.get(url_pagina_filme)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Busca pelo link do vídeo no botão de espelhar ou na opção do servidor
    link_video = None

    # Primeira tentativa: procura no botão "Espelhar"
    button = soup.find('button', {'class': 'webvideocast'})
    if button and 'onclick' in button.attrs:
        onclick_value = button['onclick']
        # Extrai o link do 'onclick'
        link_video = onclick_value.split("encodeURIComponent('")[1].split("'))")[0]

    # Segunda tentativa: busca nas divs de opções de servidor
    if not link_video:
        option = soup.find('div', {'class': 'option', 'data-link': True})
        if option:
            link_video = option['data-link']

    return link_video

# Rota da API para buscar o link de reprodução do filme
@app.route('/api/buscar_link_play', methods=['GET'])
def buscar_link_play_filme():
    titulo = request.args.get('titulo')
    if not titulo:
        return jsonify({"erro": "Parâmetro 'titulo' é obrigatório"}), 400

    # Busca o link da página do filme
    url_pagina_filme = buscar_pagina_filme(titulo)
    if not url_pagina_filme:
        return jsonify({"erro": "Filme não encontrado"}), 404

    # Busca o link de reprodução do vídeo
    link_play = buscar_link_play(url_pagina_filme)
    if link_play:
        return jsonify({"titulo": titulo, "link_play": link_play})
    else:
        return jsonify({"erro": "Link de reprodução não encontrado"}), 404

# Executa o app Flask
if __name__ == '__main__':
    app.run(debug=True)
