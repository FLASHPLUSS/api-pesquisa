import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import traceback

app = Flask(__name__)

def buscar_id_do_filme(titulo):
    try:
        # URL de pesquisa do site
        url_pesquisa = "https://wix.maxcine.top/public/pesquisa"
        params = {"search": titulo}  # Envia o título do filme como parâmetro de pesquisa
        
        # Cabeçalhos para simular um navegador
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Realiza a requisição de pesquisa
        response = requests.get(url_pesquisa, params=params, headers=headers)
        
        if response.status_code != 200:
            return None, f"Erro ao realizar a pesquisa. Status: {response.status_code}"

        # Processa o conteúdo da página de resultados com BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        link_pagina_filme = None
        
        # Procura pelo link do filme que contém "/public/filme/"
        for link in soup.find_all('a', href=True):
            if "/public/filme/" in link['href']:
                link_pagina_filme = link['href']
                break

        if not link_pagina_filme:
            return None, "Filme não encontrado"
        
        # Extrai o ID do filme da URL
        filme_id = link_pagina_filme.split('/filme/')[1]
        return filme_id, None

    except Exception as e:
        return None, f"Erro inesperado: {str(e)}\n{traceback.format_exc()}"

@app.route('/api/pesquisar', methods=['GET'])
def pesquisar_filme():
    try:
        titulo = request.args.get('titulo')
        if not titulo:
            return jsonify({"erro": "Parâmetro 'titulo' é obrigatório"}), 400

        filme_id, erro = buscar_id_do_filme(titulo)
        if erro:
            return jsonify({"erro": erro}), 500

        # URL completa do filme
        url_filme = f"https://wix.maxcine.top/public/filme/{filme_id}"
        
        return jsonify({"titulo": titulo, "filme_id": filme_id, "url_filme": url_filme})

    except Exception as e:
        return jsonify({"erro": f"Erro no servidor: {str(e)}\n{traceback.format_exc()}"}), 500

# Este bloco permite rodar o servidor Flask localmente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
