import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import traceback

app = Flask(__name__)

def buscar_link_filme(titulo):
    try:
        # Nova URL de pesquisa
        url_pesquisa = f"https://www.assistir.biz/busca?q={titulo}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Faz a requisição de pesquisa
        response = requests.get(url_pesquisa, headers=headers)
        
        if response.status_code != 200:
            return None, f"Erro na pesquisa do filme, status: {response.status_code}"

        # Usar BeautifulSoup para analisar o HTML da resposta
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Procurar o primeiro link de filme
        link_pagina_filme = None
        for link in soup.find_all('a', href=True):
            if "/filme/" in link['href']:  # Ajuste na busca pelo link
                link_pagina_filme = link['href']
                break
        
        if not link_pagina_filme:
            return None, "Filme não encontrado"

        # Formar a URL completa da página do filme
        url_pagina_filme = f"https://www.assistir.biz{link_pagina_filme}" if link_pagina_filme.startswith('/') else link_pagina_filme
        
        return url_pagina_filme, None
    
    except Exception as e:
        return None, f"Erro inesperado: {str(e)}\n{traceback.format_exc()}"

@app.route('/api/pesquisar', methods=['GET'])
def pesquisar_filme():
    try:
        titulo = request.args.get('titulo')
        if not titulo:
            return jsonify({"erro": "Parâmetro 'titulo' é obrigatório"}), 400

        # Chama a função de busca do filme
        link_filme, erro = buscar_link_filme(titulo)
        if erro:
            return jsonify({"erro": erro}), 500

        # Retorna o resultado com o link do filme encontrado
        return jsonify({"titulo": titulo, "link_filme": link_filme})
    
    except Exception as e:
        return jsonify({"erro": f"Erro no servidor: {str(e)}\n{traceback.format_exc()}"}), 500

# Este bloco permite rodar o servidor Flask localmente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
