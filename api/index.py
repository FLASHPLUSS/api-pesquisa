import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import traceback

app = Flask(__name__)

# Função para buscar URL da página do filme no Maxcine (site principal)
def buscar_url_pagina_filme_maxcine(titulo):
    try:
        url_pesquisa = f"https://wix.maxcine.top/public/pesquisa-em-tempo-real?search={titulo}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url_pesquisa, headers=headers)
        if response.status_code != 200:
            return None, f"Erro na pesquisa do filme, status: {response.status_code}"

        soup = BeautifulSoup(response.content, 'html.parser')
        link_pagina_filme = None
        for link in soup.find_all('a', href=True):
            if "/public/filme/" in link['href']:
                link_pagina_filme = link['href']
                break

        if not link_pagina_filme:
            return None, "Filme não encontrado no site principal"

        url_pagina_filme = f"https://wix.maxcine.top{link_pagina_filme}" if link_pagina_filme.startswith('/') else link_pagina_filme

        return url_pagina_filme, None
    
    except Exception as e:
        return None, f"Erro inesperado: {str(e)}\n{traceback.format_exc()}"

# Função para buscar URL da página do filme no Visioncine (site secundário)
def buscar_url_pagina_filme_visioncine(titulo):
    try:
        url_pesquisa = f"https://www.visioncine-1.com.br/search.php?q={titulo}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "TE": "Trailers"
        }

        # Faz a requisição de pesquisa no Visioncine
        response = requests.get(url_pesquisa, headers=headers)
        if response.status_code != 200:
            return None, f"Erro na pesquisa do filme no Visioncine, status: {response.status_code}"

        soup = BeautifulSoup(response.content, 'html.parser')
        url_pagina_filme = None

        # Encontrar o link da página do filme dentro da página de resultado de pesquisa
        result = soup.find('a', {'class': 'btn free fw-bold', 'href': True})
        if result:
            url_pagina_filme = result['href']

        if not url_pagina_filme:
            return None, "Página do filme não encontrada no Visioncine"

        # Retorna a URL completa do filme
        if url_pagina_filme.startswith('/'):
            url_pagina_filme = f"https://www.visioncine-1.com.br{url_pagina_filme}"

        return url_pagina_filme, None

    except Exception as e:
        return None, f"Erro inesperado: {str(e)}\n{traceback.format_exc()}"

@app.route('/api/pesquisar', methods=['GET'])
def pesquisar_filme():
    try:
        titulo = request.args.get('titulo')

        if not titulo:
            return jsonify({"erro": "Parâmetro 'titulo' é obrigatório"}), 400

        # Primeiro, tenta buscar no site principal (Maxcine)
        url_pagina_filme, erro = buscar_url_pagina_filme_maxcine(titulo)

        # Se não encontrar no site principal, tenta buscar no site secundário (Visioncine)
        if not url_pagina_filme:
            url_pagina_filme, erro = buscar_url_pagina_filme_visioncine(titulo)

        if erro:
            return jsonify({"erro": erro}), 500

        return jsonify({"titulo": titulo, "url_pagina_filme": url_pagina_filme})
    
    except Exception as e:
        return jsonify({"erro": f"Erro no servidor: {str(e)}\n{traceback.format_exc()}"}), 500

# Este bloco permite rodar o servidor Flask localmente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
