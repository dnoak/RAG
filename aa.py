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

def obter_texto_wikipedia(titulo_pagina):
    """Obtém o texto completo do artigo da Wikipedia."""
    url = "https://pt.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,  # Apenas texto puro
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
    texto_completo = obter_texto_wikipedia(titulo)
    print(texto_completo[:1000])  # Exibir apenas os primeiros 1000 caracteres para evitar muito texto
else:
    print("Nenhum resultado encontrado.")
