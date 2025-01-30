import requests

def buscar_wikipedia(termo):
    """Busca o primeiro resultado da Wikipedia e retorna o título e o link."""
    url = "https://pt.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": termo
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "query" in data and "search" in data["query"]:
        titulo_pagina = data["query"]["search"][0]["title"]
        link = f"https://pt.wikipedia.org/wiki/{titulo_pagina.replace(' ', '_')}"
        return titulo_pagina, link
    else:
        return None, None

def obter_primeiro_paragrafo_wikipedia(titulo_pagina):
    """Obtém o primeiro parágrafo do artigo da Wikipedia."""
    url = "https://pt.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,  # Apenas texto puro
        "exintro": True,  # Obtém apenas a introdução (geralmente o primeiro parágrafo)
        "titles": titulo_pagina
    }

    response = requests.get(url, params=params)
    data = response.json()

    pages = data.get("query", {}).get("pages", {})
    for page_id, page_data in pages.items():
        if "extract" in page_data:
            return page_data["extract"]

    return "Texto não encontrado."

# Teste com um termo de pesquisa
termo_pesquisa = "mako tubarao"
titulo, link = buscar_wikipedia(termo_pesquisa)

if titulo:
    print(f"Página encontrada: {link}\n")
    primeiro_paragrafo = obter_primeiro_paragrafo_wikipedia(titulo)
    print(primeiro_paragrafo)  # Exibir o primeiro parágrafo
else:
    print("Nenhum resultado encontrado.")
