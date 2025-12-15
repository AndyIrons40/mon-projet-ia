# web_tools.py
import requests
import os

# -----------------------------------------------
# 1) DuckDuckGo Instant Answer API (gratuit)
# -----------------------------------------------
def search_duckduckgo(query: str):
    url = "https://api.duckduckgo.com"
    params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}

    try:
        r = requests.get(url, params=params, timeout=8)
        data = r.json()

        abstract = data.get("AbstractText")
        related = [t.get("Text") for t in data.get("RelatedTopics", []) if t.get("Text")]

        if abstract:
            return f"{abstract}"
        elif related:
            return "\n".join(related[:5])
        else:
            return "Aucun résultat utile."
    except Exception as e:
        return f"Erreur DuckDuckGo : {e}"


# -----------------------------------------------
# 2) Wikipedia Search API (gratuit)
# -----------------------------------------------
import requests
import time

def search_wikipedia(query: str):
    # Fonction interne pour sécuriser les appels
    def safe_json(response):
        try:
            return response.json()
        except:
            return None

    # 1) API de recherche Wikipedia (Wikimedia API)
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query
    }

    # Plusieurs tentatives (pour contourner les réponses vides)
    for attempt in range(3):
        try:
            r = requests.get(search_url, params=params, timeout=8)
            
            # Si la réponse est du HTML → Wikipedia bloque
            if r.headers.get("Content-Type","").startswith("text/html"):
                time.sleep(0.8)
                continue

            data = safe_json(r)
            if data is None:
                time.sleep(0.8)
                continue

            results = data.get("query", {}).get("search", [])
            if not results:
                return "[Wikipedia] Aucun résultat."

            title = results[0]["title"]

            # 2) Tentative 1 : API REST moderne
            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
            s = requests.get(summary_url, timeout=8)
            if s.headers.get("Content-Type","").startswith("text/html"):
                pass  # on ira au fallback
            else:
                json_sum = safe_json(s)
                if json_sum and "extract" in json_sum:
                    return f"[Wikipedia] {json_sum['extract']}"

            # 3) Fallback : ancienne API extracts
            extract_url = "https://en.wikipedia.org/w/api.php"
            extract_params = {
                "action": "query",
                "format": "json",
                "prop": "extracts",
                "explaintext": True,
                "titles": title
            }
            ex = requests.get(extract_url, params=extract_params, timeout=8)
            ex_json = safe_json(ex)

            if ex_json:
                pages = ex_json.get("query", {}).get("pages", {})
                if pages:
                    first_page = next(iter(pages.values()))
                    extract = first_page.get("extract")
                    if extract:
                        return f"[Wikipedia] {extract[:800]}..."

        except Exception:
            time.sleep(0.8)  # attendre et retenter

    # Si vraiment rien ne marche
    return "[Wikipedia] Erreur : toutes les tentatives ont échoué (probable blocage Wikipédia)."


# -----------------------------------------------
# 3) Google Search Serper
# -----------------------------------------------
def search_google_serper(query: str):
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "❌ SERPER_API_KEY manquante."

    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key}
    payload = {"q": query}

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=8)
        data = r.json()

        results = data.get("organic", [])
        if not results:
            return "Aucun résultat Google."

        return "\n".join(
            f"- {item['title']} : {item.get('snippet','')}"
            for item in results[:5]
        )
    except Exception as e:
        return f"Erreur Google : {e}"


# -----------------------------------------------
# Fonction unifiée utilisée par interface_agent.py
# -----------------------------------------------
def web_search(query: str, engines: list):
    results = {}

    if "google" in engines:
        results["google"] = search_google_serper(query)

    if "duckduckgo" in engines:
        results["duckduckgo"] = search_duckduckgo(query)

    if "wikipedia" in engines:
        results["wikipedia"] = search_wikipedia(query)

    return results
