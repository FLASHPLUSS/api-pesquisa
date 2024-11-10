import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import traceback

app = Flask(__name__)

def buscar_link_filme(titulo):
    try:
        # URL de pesquisa com o título do filme
        url_pesquisa = f"https://www.assistir.biz/busca?q={titulo}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Faz a requisição para a pesquisa
        response = requests.get(url_pesquisa, headers=headers)
        
        if response.status_code != 200:
            return None, f"Erro na pesquisa do filme, status: {response.status_code}"

        # Usar BeautifulSoup para analisar o HTML da página de pesquisa
        soup = BeautifulSoup(response.content, 'html.parser')

        # Buscar o link da página do filme
        link_pagina_filme = None
        for link in soup.find_all('a', href=True):
            if "/filme/" in link['href']:  # Procurar link para a página do filme
                link_pagina_filme = link['href']
                break

        if not link_pagina_filme:
            return None, "Filme não encontrado"

        # Formar a URL completa para a página do filme
        url_pagina_filme = f"https://www.assistir.biz{link_pagina_filme}" if link_pagina_filme.startswith('/') else link_pagina_filme

        # Agora, vamos buscar o link de reprodução
        response = requests.get(url_pagina_filme, headers=headers)
        if response.status_code != 200:
            return None, f"Erro ao acessar a página do filme, status: {response.status_code}"

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Procurar links de iframe para os players
        iframe_link = None
        players = soup.find_all('div', class_='tab-pane')  # Encontrar todas as opções de player

        for player in players:
            iframe = player.find('iframe', src=True)
            if iframe:
                iframe_link = iframe['src']
                break  # Caso encontre um player, quebra o loop e retorna o link

        if iframe_link:
            return iframe_link, None
        else:
            return None, "Nenhum link de reprodução encontrado"

    except Exception as e:
        return None, f"Erro inesperado: {str(e)}\n{traceback.format_exc()}"

@app.route('/api/pesquisar', methods=['GET'])
def pesquisar_filme():
    try:
        titulo = request.args.get('titulo')
        if not titulo:
            return jsonify({"erro": "Parâmetro 'titulo' é obrigatório"}), 400

        # Chama a função que busca o link do filme
        link_filme, erro = buscar_link_filme(titulo)
        if erro:
            return jsonify({"erro": erro}), 500

        # Retorna o link do filme ou erro
        return jsonify({"titulo": titulo, "link_filme": link_filme})
    
    except Exception as e:
        return jsonify({"erro": f"Erro no servidor: {str(e)}\n{traceback.format_exc()}"}), 500

# Este bloco permite rodar o servidor Flask localmente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
