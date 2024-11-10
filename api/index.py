import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import traceback

app = Flask(__name__)

# Função para buscar link de filme no Maxcine (site principal)
def buscar_link_filme_maxcine(titulo):
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
        
        response = requests.get(url_pagina_filme, headers=headers)
        if response.status_code != 200:
            return None, f"Erro ao acessar a página do filme no site principal, status: {response.status_code}"

        soup = BeautifulSoup(response.content, 'html.parser')
        link_video = None

        # Extrair link de reprodução
        button = soup.find('button', {'class': 'webvideocast'})
        if button and 'onclick' in button.attrs:
            onclick_value = button['onclick']
            link_video = onclick_value.split("encodeURIComponent('")[1].split("'))")[0]

        if not link_video:
            option = soup.find('div', {'class': 'option', 'data-link': True})
            if option:
                link_video = option['data-link']

        if link_video:
            return link_video, None
        else:
            return None, "Link de reprodução não encontrado no site principal"
    
    except Exception as e:
        return None, f"Erro inesperado: {str(e)}\n{traceback.format_exc()}"

# Função para buscar link de filme no Visioncine (site secundário)
def buscar_link_filme_visioncine(titulo):
    try:
        url_pesquisa = f"https://www.visioncine-1.com.br/search.php?q={titulo}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Faz a requisição de pesquisa no Visioncine
        response = requests.get(url_pesquisa, headers=headers)
        if response.status_code != 200:
            return None, f"Erro na pesquisa do filme no Visioncine, status: {response.status_code}"

        soup = BeautifulSoup(response.content, 'html.parser')
        video_url = None

        # Encontrar o link de reprodução (video_url) dentro da página de resultado de pesquisa
        video_url_element = soup.find('a', {'class': 'btn free fw-bold', 'href': True})
        if video_url_element:
            video_url = video_url_element['href']

        if not video_url:
            return None, "Link de reprodução não encontrado no Visioncine"

        # Verificando se existe a classe 'info', que pode conter mais informações
        info_div = soup.find('div', {'class': 'info col-12 col-md-8 col-lg-7 px-4 px-lg-5 text-center text-md-start align-items-center align-items-md-start'})
        if info_div:
            # Você pode adicionar qualquer outra lógica que precise extrair mais detalhes dessa div
            pass

        return video_url, None

    except Exception as e:
        return None, f"Erro inesperado: {str(e)}\n{traceback.format_exc()}"

@app.route('/api/pesquisar', methods=['GET'])
def pesquisar_filme():
    try:
        titulo = request.args.get('titulo')

        if not titulo:
            return jsonify({"erro": "Parâmetro 'titulo' é obrigatório"}), 400

        # Primeiro, tenta buscar no site principal (Maxcine)
        link_filme, erro = buscar_link_filme_maxcine(titulo)

        # Se não encontrar no site principal, tenta buscar no site secundário (Visioncine)
        if not link_filme:
            link_filme, erro = buscar_link_filme_visioncine(titulo)

        if erro:
            return jsonify({"erro": erro}), 500

        return jsonify({"titulo": titulo, "link_filme": link_filme})
    
    except Exception as e:
        return jsonify({"erro": f"Erro no servidor: {str(e)}\n{traceback.format_exc()}"}), 500

# Este bloco permite rodar o servidor Flask localmente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
