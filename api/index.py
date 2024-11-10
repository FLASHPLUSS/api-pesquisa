import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import traceback

app = Flask(__name__)

def buscar_link_filme(titulo):
    try:
        # Nova URL de pesquisa em tempo real
        url_pesquisa = f"https://wix.maxcine.top/public/pesquisa-em-tempo-real?search={titulo}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Faz a requisição de pesquisa com timeout
        response = requests.get(url_pesquisa, headers=headers, timeout=10)  # Timeout de 10 segundos

        if response.status_code != 200:
            return None, f"Erro na pesquisa do filme, status: {response.status_code}"

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
        url_pagina_filme = f"https://wix.maxcine.top{link_pagina_filme}" if link_pagina_filme.startswith('/') else link_pagina_filme

        # Agora que temos o link da página do filme, vamos buscar o link de reprodução
        link_reproducao, erro = buscar_link_reproducao(url_pagina_filme)
        if erro:
            return None, erro

        return url_pagina_filme, link_reproducao, None

    except requests.exceptions.Timeout:
        return None, None, "O tempo de resposta do servidor de pesquisa foi excedido. Tente novamente mais tarde."

    except Exception as e:
        return None, None, f"Erro inesperado: {str(e)}\n{traceback.format_exc()}"

def buscar_link_reproducao(url_filme):
    try:
        # Faz a requisição para a página do filme
        response = requests.get(url_filme, timeout=10)

        if response.status_code != 200:
            return None, f"Erro ao acessar a página do filme, status: {response.status_code}"

        # Usar BeautifulSoup para fazer o parsing da página do filme
        soup = BeautifulSoup(response.content, 'html.parser')

        # Procurar o link de reprodução dentro da div 'player-options'
        div_player = soup.find('div', class_='player-options')
        if div_player:
            # Encontrar todos os links de reprodução (servidores)
            for option in div_player.find_all('div', class_='option', data_link=True):
                link_reproducao = option['data-link']
                return link_reproducao, None
        return None, "Link de reprodução não encontrado."

    except requests.exceptions.Timeout:
        return None, "O tempo de resposta para acessar o filme foi excedido. Tente novamente mais tarde."

    except Exception as e:
        return None, f"Erro inesperado ao acessar o link de reprodução: {str(e)}\n{traceback.format_exc()}"

@app.route('/api/pesquisar', methods=['GET'])
def pesquisar_filme():
    try:
        titulo = request.args.get('titulo')
        if not titulo:
            return jsonify({"erro": "Parâmetro 'titulo' é obrigatório"}), 400

        link_filme, link_reproducao, erro = buscar_link_filme(titulo)
        if erro:
            return jsonify({"erro": erro}), 500

        return jsonify({
            "titulo": titulo,
            "link_filme": link_filme,
            "link_reproducao": link_reproducao
        })

    except Exception as e:
        return jsonify({"erro": f"Erro no servidor: {str(e)}\n{traceback.format_exc()}"}), 500

# Este bloco permite rodar o servidor Flask localmente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
