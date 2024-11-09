from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/buscar-filme', methods=['GET'])
def buscar_filme():
    # Pega o título do filme da query string
    titulo = request.args.get('titulo')
    
    if not titulo:
        return jsonify({"erro": "O título do filme é obrigatório."}), 400
    
    # URL de pesquisa
    url = f"https://wix.maxcine.top/public/pesquisa-em-tempo-real?search={titulo}"
    
    # Faz a requisição para o site
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta exceções para status de erro HTTP
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": str(e)}), 500
    
    # Faz o parsing do HTML usando BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Encontra o primeiro resultado do filme
    result_card = soup.find('div', class_='result-card')
    if result_card:
        # Pega o título do filme
        title = result_card.find('a').get('title', 'Título não disponível')
        
        # Pega o link para a página do filme
        film_url = result_card.find('a', href=True)['href']
        
        # Dentro do 'result-card', encontra a div 'player-options' e pega o 'data-link' do play
        player_options = result_card.find('div', class_='player-options')
        if player_options:
            option = player_options.find('div', class_='option', attrs={'data-link': True})
            if option:
                play_url = option['data-link']
                return jsonify({
                    "titulo": title,
                    "link_filme": film_url,
                    "url_do_play": play_url
                }), 200
    
    return jsonify({"erro": "Filme não encontrado ou URL de play não disponível."}), 404

# Código para rodar o servidor no host '0.0.0.0' e na porta 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
