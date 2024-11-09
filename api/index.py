import requests
from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import traceback

app = Flask(__name__)

def buscar_link_reproducao(titulo):
    try:
        # Montar a URL de pesquisa direta
        url_pesquisa = f"https://wix.maxcine.top/public/pesquisa-em-tempo-real?search={titulo}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Faz a requisição de pesquisa
        response = requests.get(url_pesquisa, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None, f"Erro na pesquisa do filme, status: {response.status_code}"

        # Depuração: Verificar o conteúdo da resposta
        print("Resposta recebida:", response.text)

        # Usar BeautifulSoup para parsear o HTML e encontrar o link do filme
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procurar o link do filme nos resultados
        link_video = None
        for link in soup.find_all('a', href=True):
            if "/public/filme/" in link['href']:
                link_video = link['href']
                break

        if link_video:
            # Retornar o link completo
            link_video = f"https://wix.maxcine.top{link_video}"
            return link_video, None
        else:
            return None, "Filme não encontrado ou link de reprodução não encontrado"

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
