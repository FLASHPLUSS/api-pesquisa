import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import traceback

app = Flask(__name__)

def buscar_link_reproducao(titulo):
    try:
        # URL para pesquisar pelo título do filme
        url_pesquisa = "https://wix.maxcine.top/public/pesquisa-em-tempo-real"
        params = {"search": titulo}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Faz a requisição de pesquisa
        response = requests.get(url_pesquisa, params=params, headers=headers)
        
        if response.status_code != 200:
            return None, f"Erro na pesquisa do filme, status: {response.status_code}"

        # Usar BeautifulSoup para encontrar a URL da página do filme
        soup = BeautifulSoup(response.content, 'html.parser')
        link_pagina_filme = None
        for link in soup.find_all('a', href=True):
            if "/public/filme/" in link['href']:
                link_pagina_filme = f"https://wix.maxcine.top{link['href']}"
                break  # Encontrado o primeiro filme correspondente

        if not link_pagina_filme:
            return None, "Filme não encontrado"

        # Acessa a página do filme para obter o link de reprodução
        response_filme = requests.get(link_pagina_filme, headers=headers)
        if response_filme.status_code != 200:
            return None, f"Erro ao acessar a página do filme, status: {response_filme.status_code}"

        # Usar BeautifulSoup para extrair o link de reprodução da página do filme
        soup_filme = BeautifulSoup(response_filme.content, 'html.parser')
        link_video = None

        # Procurar o link no botão 'webvideocast'
        button = soup_filme.find('button', {'class': 'webvideocast'})
        if button and 'onclick' in button.attrs:
            onclick_value = button['onclick']
            link_video = onclick_value.split("encodeURIComponent('")[1].split("'))")[0]

        # Se o link não foi encontrado no botão, procurar na div com classe option
        if not link_video:
            option = soup_filme.find('div', {'class': 'option', 'data-link': True})
            if option:
                link_video = option['data-link']

        if link_video:
            return link_video, None
        else:
            return None, "Link de reprodução não encontrado"
    
    except Exception as e:
        return None, f"Erro inesperado: {str(e)}\n{traceback.format_exc()}"

@app.route('/api/pesquisar', methods=['GET'])
def pesquisar_filme():
    try:
        titulo = request.args.get('titulo')
        if not titulo:
            return jsonify({"erro": "Parâmetro 'titulo' é obrigatório"}), 400

        link_play, erro = buscar_link_reproducao(titulo)
        if erro:
            return jsonify({"erro": erro}), 500

        return jsonify({"titulo": titulo, "link_play": link_play})
    
    except Exception as e:
        return jsonify({"erro": f"Erro no servidor: {str(e)}\n{traceback.format_exc()}"}), 500

# Este bloco permite rodar o servidor Flask localmente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
