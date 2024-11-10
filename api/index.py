import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import traceback

app = Flask(__name__)

# Função para buscar o título, ID do filme, o link da página e o link de reprodução
def buscar_link_filme(titulo):
    try:
        # Nova URL de pesquisa em tempo real
        url_pesquisa = f"https://wix.maxcine.top/public/pesquisa-em-tempo-real?search={titulo}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Faz a requisição de pesquisa
        response = requests.get(url_pesquisa, headers=headers)
        
        if response.status_code != 200:
            return None, None, None, f"Erro na pesquisa do filme, status: {response.status_code}"

        # Usar BeautifulSoup para encontrar o link da página do filme
        soup = BeautifulSoup(response.content, 'html.parser')
        link_pagina_filme = None
        filme_id = None
        for link in soup.find_all('a', href=True):
            if "/public/filme/" in link['href']:
                link_pagina_filme = link['href']
                break

        if not link_pagina_filme:
            return None, None, None, "Filme não encontrado"

        # Formar a URL completa da página do filme
        url_pagina_filme = f"https://wix.maxcine.top{link_pagina_filme}" if link_pagina_filme.startswith('/') else link_pagina_filme

        # Agora, vamos pegar o título do filme e o ID
        titulo_filme = soup.find('h1', class_='movie-title').get_text() if soup.find('h1', class_='movie-title') else "Título não encontrado"
        filme_id = link_pagina_filme.split("/")[-1]  # ID do filme da URL da página

        # Agora, vamos pegar o link de reprodução a partir da página do filme
        link_reproducao = buscar_link_reproducao(url_pagina_filme)
        if not link_reproducao:
            return None, None, None, "Link de reprodução não encontrado"

        return titulo_filme, filme_id, url_pagina_filme, link_reproducao
    
    except Exception as e:
        return None, None, None, f"Erro inesperado: {str(e)}"

# Função para obter o link de reprodução
def buscar_link_reproducao(url_pagina_filme):
    try:
        # Faz a requisição para a página do filme
        response = requests.get(url_pagina_filme)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrar o link de reprodução no HTML da página do filme
        link_reproducao = None
        # Procurar pela div com a classe 'option' que contém o atributo 'data-link'
        option_div = soup.find('div', class_='option', attrs={'data-link': True})
        
        if option_div:
            link_reproducao = option_div['data-link']  # Extrair o valor de 'data-link'

        return link_reproducao
    
    except Exception as e:
        return None

@app.route('/api/pesquisar', methods=['GET'])
def pesquisar_filme():
    try:
        # Recebe o título do filme pela query string
        titulo = request.args.get('titulo')
        if not titulo:
            return jsonify({"erro": "Parâmetro 'titulo' é obrigatório"}), 400

        # Busca o título, ID, link da página e o link de reprodução
        titulo_filme, filme_id, link_filme, link_reproducao, erro = buscar_link_filme(titulo)
        if erro:
            return jsonify({"erro": erro}), 500

        # Retorna as informações encontradas na resposta JSON
        return jsonify({
            "titulo": titulo_filme,
            "id_filme": filme_id,
            "link_filme": link_filme,
            "link_reproducao": link_reproducao
        })
    
    except Exception as e:
        return jsonify({"erro": f"Erro no servidor: {str(e)}\n{traceback.format_exc()}"}), 500

# Este bloco permite rodar o servidor Flask localmente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
