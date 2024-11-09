import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import traceback

app = Flask(__name__)

def buscar_link_reproducao(titulo):
    try:
        # URL de pesquisa em tempo real
        url_pesquisa = f"https://wix.maxcine.top/public/pesquisa-em-tempo-real?search={titulo}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Faz a requisição de pesquisa em tempo real
        response = requests.get(url_pesquisa, headers=headers)

        if response.status_code != 200:
            return None, f"Erro na pesquisa do filme, status: {response.status_code}"

        # A resposta é esperada como um JSON com a lista de filmes
        filmes = response.json()

        if not filmes or 'id' not in filmes[0]:
            return None, "Filme não encontrado"

        # Extrair o ID do primeiro filme encontrado
        id_filme = filmes[0]['id']
        
        # Formar a URL da página do filme
        url_pagina_filme = f"https://wix.maxcine.top/public/filme/{id_filme}"

        # Acessar a página do filme para obter o link do play
        response = requests.get(url_pagina_filme, headers=headers)
        if response.status_code != 200:
            return None, f"Erro ao acessar a página do filme, status: {response.status_code}"

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
    
    except requests.RequestException as e:
        return None, f"Erro na requisição HTTP: {str(e)}"
    except Exception as e:
        return None, f"Erro inesperado: {str(e)}\n{traceback.format_exc()}"

@app.route('/api/pesquisar', methods=['GET'])
def pesquisar_filme():
    try:
        titulo = request.args.get('titulo')
        if not titulo:
            return jsonify({"erro": "Parâmetro 'titulo' é obrigatório"}), 400
        if not titulo.strip():
            return jsonify({"erro": "O título não pode ser vazio"}), 400

        link_play, erro = buscar_link_reproducao(titulo)
        if erro:
            return jsonify({"erro": erro}), 500

        return jsonify({"titulo": titulo, "link_play": link_play})
    
    except Exception as e:
        return jsonify({"erro": f"Erro no servidor: {str(e)}\n{traceback.format_exc()}"}), 500

# Este bloco permite rodar o servidor Flask localmente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
