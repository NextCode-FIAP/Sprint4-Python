"""Regras de negócio do SmartStudy, organizadas em uma classe."""
import difflib
import json
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from urllib.parse import urlparse


MATH_SUBJECTS = [
    "Algebra", "Arithmetic", "Calculus", "Combinatorics", "Differential Equations",
    "Discrete Mathematics", "Functions", "Geometry", "Logic", "Linear Algebra",
    "Number Theory", "Probability", "Statistics", "Set Theory", "Topology",
    "Trigonometry"
]


class SmartStudy:
    def __init__(self, storage):
        self.storage = storage
        self.data = storage.load()

    def persist(self):
        return self.storage.save(self.data)

    def save_gallery_item(self, item):
        item["id"] = self._next_id(self.data["gallery"])
        item["created_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.data["gallery"].append(item)
        return self.persist()

    def save_preference(self, subject, settings):
        self.data["preferences"][subject.casefold()] = settings
        return self.persist()

    def get_preference(self, subject):
        return self.data["preferences"].get(subject.casefold())

    def search_gallery(self, subject=""):
        if not subject:
            return self.data["gallery"]
        return [item for item in self.data["gallery"]
                if subject.casefold() in item.get("subject", "").casefold()]

    def reclassify_gallery_item(self, item_id, new_subject):
        for item in self.data["gallery"]:
            if item["id"] == item_id:
                item["subject"] = new_subject
                return self.persist()
        return False

    def add_class(self, subject, day, time):
        item = {"id": self._next_id(self.data["schedule"]),
                "subject": subject, "day": day, "time": time}
        self.data["schedule"].append(item)
        return self.persist()

    def remove_class(self, item_id):
        before = len(self.data["schedule"])
        self.data["schedule"] = [item for item in self.data["schedule"] if item["id"] != item_id]
        return len(self.data["schedule"]) < before and self.persist()

    def add_resource(self, subject, book):
        item = {"subject": subject, **book}
        self.data["resources"].append(item)
        return self.persist()

    def add_flashcard(self, subject, question, answer):
        item = {"id": self._next_id(self.data["flashcards"]),
                "subject": subject, "question": question, "answer": answer}
        self.data["flashcards"].append(item)
        return self.persist()

    def create_api_flashcards(self, subject, limit=10):
        """Gera flashcards pela API e os persiste.

        Retorna a quantidade de cartões efetivamente salvos. Se a gravação
        falhar, os cartões são removidos da memória e o retorno é 0, para que
        o programa nunca informe um sucesso que não aconteceu.
        """
        cards = self.generate_math_flashcards(subject, limit=limit)
        first_id = self._next_id(self.data["flashcards"])
        new_items = [
            {"id": first_id + offset, "subject": subject,
             "question": card["question"], "answer": card["answer"]}
            for offset, card in enumerate(cards)
        ]
        self.data["flashcards"].extend(new_items)
        if self.persist():
            return len(new_items)
        del self.data["flashcards"][len(self.data["flashcards"]) - len(new_items):]
        return 0

    @staticmethod
    def normalize_text(value):
        value = (value or "").casefold()
        value = re.sub(r"[àáâãäå]", "a", value)
        value = re.sub(r"[èéêë]", "e", value)
        value = re.sub(r"[ìíîï]", "i", value)
        value = re.sub(r"[òóôõö]", "o", value)
        value = re.sub(r"[ùúûü]", "u", value)
        value = re.sub(r"[ç]", "c", value)
        value = re.sub(r"[^a-z0-9\s]", " ", value)
        value = re.sub(r"\s+", " ", value).strip()
        return value

    @staticmethod
    def available_math_subjects():
        return list(MATH_SUBJECTS)

    @staticmethod
    def resolve_subject(subject):
        text = SmartStudy.normalize_text(subject)
        mapping = {SmartStudy.normalize_text(item): item for item in MATH_SUBJECTS}
        if text in mapping:
            return mapping[text]
        match = difflib.get_close_matches(text, list(mapping), n=1, cutoff=0.55)
        if match:
            return mapping[match[0]]
        raise ValueError(f"Matéria não encontrada: '{subject}'.")

    @staticmethod
    def _request_json(url):
        for attempt in range(4):
            try:
                request = urllib.request.Request(
                    url,
                    headers={"User-Agent": "NextCode-MathFlashcards/1.0", "Accept": "application/json"},
                )
                with urllib.request.urlopen(request, timeout=12) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as error:
                if error.code == 429 and attempt < 3:
                    time.sleep(2 ** attempt)
                    continue
                raise
            except Exception:
                if attempt < 3:
                    time.sleep(1)
                    continue
                raise
        raise RuntimeError("Não foi possível consultar a API externa.")

    @staticmethod
    def get_math_concept_data(term):
        if not term or not term.strip():
            raise ValueError("Informe uma matéria válida.")
        query = f"{term.strip()} mathematics"
        url = (
            "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch="
            f"{urllib.parse.quote(query)}&format=json&utf8=1&origin=*&srlimit=5"
        )
        data = SmartStudy._request_json(url)
        results = data.get("query", {}).get("search", [])
        if not results:
            url = (
                "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch="
                f"{urllib.parse.quote(term.strip())}&format=json&utf8=1&origin=*&srlimit=5"
            )
            data = SmartStudy._request_json(url)
            results = data.get("query", {}).get("search", [])
        if not results:
            raise ValueError(f"Nenhum conceito encontrado para: {term}")
        title = results[0].get("title")
        if not title:
            raise ValueError(f"Nenhum conceito encontrado para: {term}")
        safe_title = urllib.parse.quote(title)
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe_title}"
        summary = SmartStudy._request_json(summary_url)
        extract = (summary.get("extract") or "").strip()
        if not extract:
            raise ValueError(f"Nenhum resumo disponível para o conceito: {title}")
        return {
            "title": summary.get("title", title),
            "description": (summary.get("description") or "Conceito matemático").strip(),
            "extract": extract,
            "url": summary.get("content_urls", {}).get("desktop", {}).get("page", ""),
        }

    @staticmethod
    def randomize(items):
        shuffled = list(items)
        random.shuffle(shuffled)
        return shuffled

    @staticmethod
    def generate_math_flashcards(subject, limit=10):
        data = SmartStudy.get_math_concept_data(subject)
        title = data["title"]
        extract = data["extract"]
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", extract) if s.strip()]
        definition = sentences[0] if sentences else f"{title} é uma área da matemática que estuda padrões, estruturas e relações."
        second = sentences[1] if len(sentences) > 1 else "A área usa raciocínio lógico, fórmulas e provas para resolver problemas."
        third = sentences[2] if len(sentences) > 2 else "Ela é aplicada em ciência, engenharia, tecnologia e no cotidiano."
        key_idea = "Raciocínio lógico, padrões e resolução de problemas."
        if "numbers" in extract.lower() or "números" in extract.lower():
            key_idea = "Números, padrões e relações quantitativas."
        elif "geometry" in extract.lower() or "geometric" in extract.lower() or "formas" in extract.lower():
            key_idea = "Formas, espaço e propriedades geométricas."
        elif "functions" in extract.lower() or "funções" in extract.lower():
            key_idea = "Funções e dependências entre variáveis."
        elif "probability" in extract.lower() or "probabilidade" in extract.lower():
            key_idea = "Probabilidade e análise de incertezas."

        prompts = [
            f"O que é {title}?",
            f"Qual é o foco principal de {title}?",
            f"Qual tipo de raciocínio é usado em {title}?",
            f"Em que tipo de problema {title} ajuda a resolver?",
            f"Qual é a relação de {title} com a lógica?",
            f"Como {title} se aplica em ciência e tecnologia?",
            f"Qual é a importância da demonstração em {title}?",
            f"O que {title} estuda em termos gerais?",
            f"Qual conceito central merece atenção em {title}?",
            f"Qual frase resume melhor {title}?"
        ]
        answers = [
            definition,
            key_idea,
            "Uso de lógica, provas e fórmulas.",
            "Problemas modelados por estruturas, padrões e relações.",
            "Ela depende de raciocínio lógico e demonstrações rigorosas.",
            "Ela é aplicada em ciência, engenharia, tecnologia e pesquisa.",
            "A demonstração valida ideias e garante consistência dos resultados.",
            "Ela estuda padrões, relações, estruturas e fenômenos quantitativos.",
            "A abstração e a análise de relações são fundamentais.",
            third,
        ]

        cards = []
        for prompt, answer in zip(prompts, answers):
            cards.append({"question": prompt, "answer": answer})
        while len(cards) < limit:
            cards.append({
                "question": f"Flashcard extra sobre {title}",
                "answer": f"{title} é uma área da matemática que estuda padrões, relações e estruturas com rigor lógico.",
            })
        cards = cards[:limit]
        random.shuffle(cards)
        return cards

    @staticmethod
    def generate_math_quiz(subject, limit=10):
        concept = SmartStudy.get_math_concept_data(subject)
        title = concept["title"]
        extract = concept["extract"]
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", extract) if s.strip()]
        definition = sentences[0] if sentences else f"{title} é uma área da matemática que estuda padrões, estruturas e relações."
        secondary = sentences[1] if len(sentences) > 1 else "A área usa raciocínio lógico, fórmulas e provas para resolver problemas."
        tertiary = sentences[2] if len(sentences) > 2 else "Ela é aplicada em ciência, engenharia, tecnologia e no cotidiano."
        key_idea = "Raciocínio lógico, padrões e resolução de problemas."
        if "numbers" in extract.lower() or "números" in extract.lower():
            key_idea = "Números, padrões e relações quantitativas."
        elif "geometry" in extract.lower() or "geometric" in extract.lower() or "formas" in extract.lower():
            key_idea = "Formas, espaço e propriedades geométricas."
        elif "functions" in extract.lower() or "funções" in extract.lower():
            key_idea = "Funções e dependências entre variáveis."
        elif "probability" in extract.lower() or "probabilidade" in extract.lower():
            key_idea = "Probabilidade e análise de incertezas."

        questions = [
            {
                "question": f"Qual alternativa melhor descreve {title}?",
                "options": [definition, "Uma linguagem para criar páginas na web.", "Um sistema operacional usado para controlar hardware.", "Uma ferramenta para edição de imagens digitais."],
                "answer": definition,
                "explanation": f"A resposta está correta porque {definition}"
            },
            {
                "question": f"Qual é a principal ideia central de {title}?",
                "options": [key_idea, "Armazenar dados em banco de dados.", "Organizar arquivos em pastas.", "Criar animações de vídeo."],
                "answer": key_idea,
                "explanation": f"{title} está diretamente ligada a {key_idea.lower()}"
            },
            {
                "question": f"Qual abordagem é típica de {title}?",
                "options": ["Uso de lógica, prova e fórmulas.", "Criação de interfaces visuais apenas.", "Configuração de rede sem cálculo.", "Desenho de logotipos sem regra matemática."],
                "answer": "Uso de lógica, prova e fórmulas.",
                "explanation": f"{title} usa raciocínio lógico, provas e fórmulas para validar relações e resolver problemas."
            },
            {
                "question": f"Em qual contexto a área de {title} é mais aplicada?",
                "options": ["Ciência, tecnologia, engenharia e modelagem de problemas.", "Somente em escrita literária.", "Somente em troca de mensagens instantâneas.", "Somente em revisão de textos."],
                "answer": "Ciência, tecnologia, engenharia e modelagem de problemas.",
                "explanation": f"A área é amplamente aplicada em ciência, engenharia e tecnologia, conforme a própria descrição da API."
            },
            {
                "question": f"Qual frase melhor complementa o estudo de {title}?",
                "options": [secondary, "É uma área focada apenas em design gráfico.", "É um método de montagem de hardware.", "É usada somente para criar anúncios."],
                "answer": secondary,
                "explanation": f"{secondary}"
            },
            {
                "question": f"O que torna {title} importante em estudos acadêmicos?",
                "options": ["Porque permite modelar e resolver problemas com rigor lógico.", "Porque substitui completamente a escrita.", "Porque organiza apenas listas de tarefas.", "Porque é um tipo de linguagem de programação."],
                "answer": "Porque permite modelar e resolver problemas com rigor lógico.",
                "explanation": "A matemática se baseia em raciocínio lógico e demonstrações para modelar e resolver problemas de diversas áreas."
            },
            {
                "question": f"Qual alternativa melhor representa a natureza de {title}?",
                "options": ["Uma área formal que usa abstração, prova e padrões.", "Um software para editar vídeos.", "Um tipo de linguagem de marcação.", "Um método para criar planilhas sem lógica."],
                "answer": "Uma área formal que usa abstração, prova e padrões.",
                "explanation": f"{title} trabalha com abstração, padrões e demonstrações, conforme o conceito descrito pela API."
            },
            {
                "question": f"Qual frase resume melhor o papel de {title}?",
                "options": [tertiary, "Ela é usada apenas para armazenar textos.", "Ela apenas organiza arquivos em computador.", "Ela substitui todas as ferramentas de produtividade."],
                "answer": tertiary,
                "explanation": f"{tertiary}"
            },
            {
                "question": f"Qual é a melhor forma de entender {title}?",
                "options": ["Como uma área que estuda relações, padrões e modelos.", "Como uma lista de comandos de teclado.", "Como um banco de dados sem regras.", "Como um editor de texto sem comandos."],
                "answer": "Como uma área que estuda relações, padrões e modelos.",
                "explanation": f"{title} envolve relações, padrões e modelos matemáticos para compreender fenômenos e resolver problemas."
            },
            {
                "question": f"Qual frase de apoio representa melhor o conceito de {title}?",
                "options": [f"{title} é um campo de estudo que busca compreender estruturas e relações por meio de provas e fórmulas.", "É apenas um conjunto de regras de interface visual.", "É somente uma coleção de símbolos sem sentido.", "É um tipo de rede social para estudantes."],
                "answer": f"{title} é um campo de estudo que busca compreender estruturas e relações por meio de provas e fórmulas.",
                "explanation": f"{title} combina abstração, provas e fórmulas para analisar estruturas e relações complexas."
            }
        ]
        random.shuffle(questions)
        return questions[:limit]

    @staticmethod
    def safe_link(url):
        """Verifica formato e domínio permitido; não substitui serviço antiphishing."""
        parsed = urlparse(url.strip())
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            return False, "Endereço inválido ou sem HTTP/HTTPS."
        host = parsed.hostname.casefold().rstrip(".")
        trusted = (host.endswith(".edu") or host.endswith(".gov") or
                   host.endswith(".org") or host == "fiap.com.br" or
                   host.endswith(".fiap.com.br"))
        if trusted:
            return True, "Domínio dentro da lista permitida do projeto."
        return False, "Domínio fora da lista permitida. Não acesse sem verificar."

    @staticmethod
    def _next_id(items):
        return max((item.get("id", 0) for item in items), default=0) + 1

