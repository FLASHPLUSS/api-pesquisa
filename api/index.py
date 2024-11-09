# api/index.py

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request

app = Flask(__name__)

def buscar_link_reproducao(titulo):
    # URL de pesquisa
    url_pesquisa = "https://wix.maxcine.top/public/pesquisa"
    params = {"search": titulo}
    response = requests.get(url_pesquisa, params=params)
    
    if response.status_code != 200:
        return None, "Erro na pesquisa do filme"

    # Usar BeautifulSoup para encontrar o link da página do filme
    soup = BeautifulSoup(response.content, 'html.parser')
    link_pagina_filme = None
    for link in soup.find_all('a', href=True):
        if "/public/filme/" in link['href']:
            link_pagina_filme = link['href']
            break

    if not link_pagina_filme:
        return None, "Filme não encontrado"

    # Formar a URL completa da página do filme
    url_pagina_filme = f"https://wix.maxcine.top{link_pagina_filme}"
    
    # Acessar a página do filme para obter o link do play
    response = requests.get(url_pagina_filme)
    if response.status_code != 200:
        return None, "Erro ao acessar a página do filme"

    soup = BeautifulSoup(response.content, 'html.parser')
    link_video = None

    # Extrair o link do botão webvideocast
    button = soup.find('button', {'class': 'webvideocast'})
    if button and 'onclick' in button.attrs:
        onclick_value = button['onclick']
        link_video = onclick_value.split("encodeURIComponent('")[1].split("'))")[0]

    # Se o link não foi encontrado no botão, procurar na div com classe option
    if not link_video:
        option = soup.find('div', {'class': 'option', 'data-link': True})
        if option:
            link_video = option['data-link']

    if link_video:
        return link_video, None
    else:
        return None, "Link de reprodução não encontrado"

@app.route('/api/pesquisar', methods=['GET'])
def pesquisar_filme():
    titulo = request.args.get('titulo')
    if not titulo:
        return jsonify({"erro": "Parâmetro 'titulo' é obrigatório"}), 400

    link_play, erro = buscar_link_reproducao(titulo)
    if erro:
        return jsonify({"erro": erro}), 404

    return jsonify({"titulo": titulo, "link_play": link_play})

# Este bloco permite rodar o servidor Flask localmente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
