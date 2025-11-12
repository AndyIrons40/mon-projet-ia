# web_tools.py
import requests, json

SERPER_API_KEY = "sk-serper-e1b6fdb8b22ffbc91d4b6407de9a5b0f88b80f16"

def web_search(query):
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = json.dumps({"q": query})
    response = requests.post("https://google.serper.dev/search", headers=headers, data=payload)

    if response.status_code != 200:
        return f"[Erreur API Serper] {response.status_code} - {response.text}"

    data = response.json()
    results = data.get("organic", [])[:3]
    formatted = "\n".join([f"- {r['title']} 🔗 {r['link']}" for r in results])
    return "🌍 Résultats Google :\n" + formatted
