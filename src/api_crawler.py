"""Crawler simples para consulta de livros na API pública Open Library."""
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class OpenLibraryCrawler:
    """Consulta livros relacionados a uma disciplina, sem exigir chave de API."""

    BASE_URL = "https://openlibrary.org/search.json"

    def search_books(self, subject, limit=5):
        params = urlencode({"q": subject, "limit": limit, "fields": "title,author_name,first_publish_year,key"})
        request = Request(
            f"{self.BASE_URL}?{params}",
            headers={"User-Agent": "NextCode-SmartStudy/1.0 (academic project)"}
        )
        try:
            with urlopen(request, timeout=8) as response:
                payload = json.loads(response.read().decode("utf-8"))
            books = []
            for item in payload.get("docs", []):
                books.append({
                    "title": item.get("title", "Título não informado"),
                    "authors": item.get("author_name", ["Autor não informado"])[:3],
                    "year": item.get("first_publish_year", "Ano não informado"),
                    "key": item.get("key", "")
                })
            return {"success": True, "items": books, "message": ""}
        except HTTPError as error:
            return {"success": False, "items": [], "message": f"API respondeu com HTTP {error.code}."}
        except (URLError, TimeoutError, json.JSONDecodeError, OSError) as error:
            return {"success": False, "items": [], "message": f"Falha de conexão ou resposta: {error}"}
