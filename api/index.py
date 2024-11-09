import aiohttp
import asyncio
from bs4 import BeautifulSoup

async def buscar_id_do_filme(titulo):
    try:
        url_pesquisa = "https://wix.maxcine.top/public/pesquisa"
        params = {"search": titulo}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Realiza a requisição assíncrona
        async with aiohttp.ClientSession() as session:
            async with session.get(url_pesquisa, params=params, headers=headers) as response:
                if response.status != 200:
                    return None, f"Erro ao realizar a pesquisa. Status: {response.status}"

                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                link_pagina_filme = None

                # Procura pelo link do filme
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
        return None, f"Erro inesperado: {str(e)}"

async def main():
    titulo = "Vênus"
    filme_id, erro = await buscar_id_do_filme(titulo)
    print(f"Filme ID: {filme_id}, Erro: {erro}")

# Executando a função assíncrona
asyncio.run(main())
