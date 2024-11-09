import requests
from flask import Flask, jsonify, request
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

        # Tentar extrair o link de reprodução diretamente da resposta
        try:
            # Espera-se que a resposta contenha o link diretamente em JSON
            data = response.json()
            print("Resposta JSON:", data)  # Verifique o conteúdo do JSON para depuração

            link_video = data.get('link', None)

            if link_video:
                return link_video, None
            else:
                return None, "Link de reprodução não encontrado na resposta"

        except ValueError:
            return None, f"Erro ao processar a resposta JSON. Conteúdo recebido: {response.text}"

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
