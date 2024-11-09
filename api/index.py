import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import traceback

app = Flask(__name__)

def buscar_link_reproducao(titulo):
    try:
        # URL de pesquisa
        url_pesquisa = "https://wix.maxcine.top/public/pesquisa"
        params = {"search": titulo}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Faz a requisição de pesquisa
        response = requests.get(url_pesquisa, params=params, headers=headers)
        
        if response.status_code != 200:
            return None, None, f"Erro na pesquisa do filme, status: {response.status_code}"

        # Usar BeautifulSoup para encontrar o link da página do filme
        soup = BeautifulSoup(response.content, 'html.parser')
        link_pagina_filme = None
        titulo_filme_encontrado = None

        # Procurar o primeiro link que corresponde ao filme
        for link in soup.find_all('a', href=True):
            if "/public/filme/" in link['href']:
                # Captura o primeiro link do filme encontrado
                link_pagina_filme = link['href']
                titulo_filme_encontrado = link.get_text().strip()
                break

        if not link_pagina_filme:
            return None, None, "Filme específico não encontrado"

        # Formar a URL completa da página do filme, corrigindo a URL concatenada
        url_pagina_filme = f"https://wix.maxcine.top{link_pagina_filme}"
        
        # Acessar a página do filme para obter o link do play
        response = requests.get(url_pagina_filme, headers=headers)
        if response.status_code != 200:
            return None, None, f"Erro ao acessar a página do filme, status: {response.status_code}"

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
            return titulo_filme_encontrado, url_pagina_filme, link_video
        else:
            return titulo_filme_encontrado, url_pagina_filme, "Link de reprodução não encontrado"
    
    except Exception as e:
        return None, None, f"Erro inesperado: {str(e)}\n{traceback.format_exc()}"

@app.route('/api/pesquisar', methods=['GET'])
def pesquisar_filme():
    try:
        titulo = request.args.get('titulo')
        if not titulo:
            return jsonify({"erro": "Parâmetro 'titulo' é obrigatório"}), 400

        titulo_filme, link_filme, link_play = buscar_link_reproducao(titulo)
        
        if link_filme is None or link_play is None:
            return jsonify({"erro": link_play or "Erro desconhecido"}), 500

        return jsonify({"titulo": titulo_filme, "link_filme": link_filme, "link_play": link_play})
    
    except Exception as e:
        return jsonify({"erro": f"Erro no servidor: {str(e)}\n{traceback.format_exc()}"}), 500

# Este bloco permite rodar o servidor Flask localmente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
