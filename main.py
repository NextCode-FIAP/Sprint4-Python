"""NEXTCODE | SMARTSTUDY — Sprint 4."""
from src.storage import JsonStorage
from src.validators import read_text, read_option, read_yes_no, read_integer, valid_time
from src.system import SmartStudy
from src.api_crawler import OpenLibraryCrawler


DAYS = {
    "1": "Segunda-feira", "2": "Terça-feira", "3": "Quarta-feira",
    "4": "Quinta-feira", "5": "Sexta-feira", "6": "Sábado"
}

MAIN_OPTIONS = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]

# Erros esperados ao consultar uma API: dado inválido/ausente (ValueError,
# inclui JSON inválido), falha de rede (OSError, inclui URLError e HTTPError)
# e esgotamento das tentativas (RuntimeError).
API_ERRORS = (ValueError, OSError, RuntimeError)


def pause():
    """Aguarda Enter; uma entrada encerrada ou Ctrl+C apenas segue para o menu."""
    try:
        input("\nPressione Enter para voltar ao menu...")
    except (KeyboardInterrupt, EOFError):
        print()


def show_menu():
    print("\n" + "=" * 62)
    print("                 NEXTCODE | SMARTSTUDY")
    print("          Câmera acadêmica inteligente — Sprint 4")
    print("=" * 62)
    print("1. Modo Inteligente")
    print("2. Digitalizar documento (OCR simulado)")
    print("3. Galeria de estudos")
    print("4. Verificar link de QR Code")
    print("5. Grade de aulas")
    print("6. Buscar livros acadêmicos (API externa)")
    print("7. Criar e revisar flashcards")
    print("8. Quiz de múltipla escolha (API gratuita)")
    print("0. Encerrar")
    print("=" * 62)


def intelligent_mode(app):
    print("\n--- MODO INTELIGENTE ---")
    environment = read_option("Ambiente [1 Sala / 2 Biblioteca / 3 Externo]: ", ["1", "2", "3"])
    subject = read_text("Disciplina: ")
    settings = app.get_preference(subject)
    if settings:
        print("Preferência anterior encontrada.")
        if not read_yes_no("Usar configuração salva? (S/N): "):
            settings = None
    if not settings:
        settings = {
            "1": {"ISO": 400, "Foco": "Automático", "Anti-reflexo": "Ativado"},
            "2": {"ISO": 200, "Foco": "Silencioso", "Redução de ruído": "Ativada"},
            "3": {"ISO": 100, "Foco": "Infinito", "HDR": "Ativado"}
        }[environment]
    print("\nConfiguração aplicada:")
    for key, value in settings.items():
        print(f"  {key}: {value}")
    if read_yes_no("Salvar como preferência desta disciplina? (S/N): "):
        app.save_preference(subject, settings)
    if read_yes_no("Registrar uma captura simulada na galeria? (S/N): "):
        filename = read_text("Nome do arquivo (ex.: aula1.jpg): ")
        saved = app.save_gallery_item({
            "type": "Captura inteligente", "subject": subject,
            "filename": filename, "environment": {"1": "Sala de aula", "2": "Biblioteca", "3": "Externo"}[environment]
        })
        print("Registro salvo." if saved else "Não foi possível salvar.")
    pause()


def scan_document(app):
    print("\n--- DIGITALIZAÇÃO DE DOCUMENTO ---")
    print("Esta etapa registra uma digitalização simulada.")
    if not read_yes_no("O documento está alinhado e com bordas visíveis? (S/N): "):
        print("Ajuste o enquadramento antes de continuar.")
        pause()
        return
    title = read_text("Nome do documento: ")
    subject = read_text("Disciplina: ")
    extracted_text = input("Texto reconhecido (simulação de OCR): ").strip()
    filename = title.replace(" ", "_") + ".pdf"
    saved = app.save_gallery_item({
        "type": "Documento OCR simulado", "subject": subject,
        "filename": filename, "environment": "Digitalização",
        "recognized_text": extracted_text
    })
    print("Documento registrado na galeria." if saved else "Falha ao persistir documento.")
    print("Observação: não há processamento real de imagem/OCR.")
    pause()


def gallery(app):
    print("\n--- GALERIA DE ESTUDOS ---")
    print("1. Listar todos | 2. Pesquisar disciplina | 3. Reclassificar")
    option = read_option("Escolha: ", ["1", "2", "3"])
    if option == "1":
        items = app.search_gallery()
    elif option == "2":
        items = app.search_gallery(read_text("Disciplina ou trecho: "))
    else:
        items = app.search_gallery()
        show_gallery_items(items)
        if not items:
            pause()
            return
        item_id = read_integer("ID do registro: ")
        subject = read_text("Nova disciplina: ")
        print("Registro atualizado." if app.reclassify_gallery_item(item_id, subject) else "ID não encontrado.")
        pause()
        return
    show_gallery_items(items)
    pause()


def show_gallery_items(items):
    if not items:
        print("Nenhum registro encontrado.")
        return
    for item in items:
        print(f"ID {item['id']} | {item['subject']} | {item['filename']} | {item['type']} | {item['created_at']}")


def qr_reader(app):
    print("\n--- VERIFICAÇÃO DE QR CODE ---")
    url = read_text("Informe o endereço identificado no QR Code: ")
    allowed, message = app.safe_link(url)
    print(("APROVADO — " if allowed else "ATENÇÃO — ") + message)
    print("Esta é uma lista de permissões simples, não uma análise antiphishing.")
    pause()


def schedule_menu(app):
    while True:
        print("\n--- GRADE DE AULAS ---")
        print("1. Cadastrar aula | 2. Visualizar | 3. Excluir | 0. Voltar")
        option = read_option("Escolha: ", ["0", "1", "2", "3"])
        if option == "0":
            return
        if option == "1":
            subject = read_text("Disciplina: ")
            day_option = read_option("Dia [1 Seg ... 6 Sáb]: ", list(DAYS))
            while True:
                time = read_text("Horário (HH:MM): ")
                if valid_time(time):
                    break
                print("Horário inválido. Exemplo válido: 19:00.")
            print("Aula cadastrada." if app.add_class(subject, DAYS[day_option], time) else "Falha ao salvar.")
        elif option == "2":
            classes = app.data["schedule"]
            if not classes:
                print("Nenhuma aula cadastrada.")
            for item in classes:
                print(f"ID {item['id']} | {item['day']} às {item['time']} — {item['subject']}")
        else:
            item_id = read_integer("ID da aula para excluir: ")
            print("Aula excluída." if app.remove_class(item_id) else "ID não encontrado.")
        pause()


def academic_search(app, crawler):
    print("\n--- BUSCA ACADÊMICA | OPEN LIBRARY ---")
    subject = read_text("Digite a disciplina ou tema: ")
    print("Consultando serviço externo...")
    result = crawler.search_books(subject)
    if not result["success"]:
        print(result["message"])
        print("Confira a conexão e tente novamente.")
        pause()
        return
    if not result["items"]:
        print("A API não encontrou livros para essa consulta.")
        pause()
        return
    for index, book in enumerate(result["items"], start=1):
        authors = ", ".join(book["authors"])
        print(f"{index}. {book['title']} — {authors} ({book['year']})")
    if read_yes_no("Salvar todos os resultados no acervo? (S/N): "):
        count = sum(1 for book in result["items"] if app.add_resource(subject, book))
        print(f"{count} referência(s) persistida(s).")
    pause()


def choose_math_subject(app):
    """Pede a matéria (nome ou número da lista). Retorna a matéria ou None se cancelar."""
    subjects = app.available_math_subjects()
    print("Matérias disponíveis:")
    for index, item in enumerate(subjects, start=1):
        print(f"  {index}. {item}")
    while True:
        raw_subject = input("Digite a matéria ou número (ou 'sair' para cancelar): ").strip()
        if raw_subject.lower() in {"sair", "0", "exit", "quit"}:
            print("Operação cancelada.")
            return None
        if raw_subject.isdecimal():
            number = int(raw_subject)
            if 1 <= number <= len(subjects):
                return subjects[number - 1]
            print(f"Número inválido. Escolha entre 1 e {len(subjects)}.")
            continue
        try:
            return app.resolve_subject(raw_subject)
        except ValueError as error:
            print(error)


def create_flashcards_from_api(app):
    subject = choose_math_subject(app)
    if subject is None:
        return
    while True:
        print(f"Consultando a API para {subject}...")
        try:
            created = app.create_api_flashcards(subject, limit=10)
        except API_ERRORS as error:
            print(f"Não foi possível gerar os flashcards: {error}")
            if read_yes_no("Tentar novamente? (S/N): "):
                continue
            return
        if created:
            print(f"{created} flashcards criados e salvos para {subject}.")
        else:
            print("Os flashcards foram gerados, mas não foi possível salvá-los. Nenhum cartão foi adicionado.")
        return


def review_flashcards(app):
    subject = input("Filtrar disciplina (Enter para todos): ").strip()
    cards = [card for card in app.data["flashcards"]
             if not subject or subject.casefold() in card["subject"].casefold()]
    if not cards:
        print("Nenhum flashcard encontrado.")
        return
    for card in SmartStudy.randomize(cards):
        print(f"\n[{card['subject']}] {card['question']}")
        input("Pressione Enter para revelar a resposta...")
        print(f"Resposta: {card['answer']}")


def flashcards_menu(app):
    while True:
        print("\n--- FLASHCARDS ---")
        print("1. Criar manualmente | 2. Revisar | 3. Criar com conceito matemático (API gratuita) | 0. Voltar")
        option = read_option("Escolha: ", ["0", "1", "2", "3"])
        if option == "0":
            return
        if option == "1":
            subject = read_text("Disciplina: ")
            question = read_text("Pergunta/frente do cartão: ")
            answer = read_text("Resposta/verso do cartão: ")
            print("Flashcard salvo." if app.add_flashcard(subject, question, answer) else "Falha ao salvar.")
        elif option == "2":
            review_flashcards(app)
        else:
            create_flashcards_from_api(app)
        pause()


def run_quiz(questions):
    """Aplica as questões no terminal e retorna a quantidade de acertos."""
    score = 0
    for number, question in enumerate(questions, start=1):
        options = SmartStudy.randomize(question["options"])
        print(f"\nQuestão {number}/{len(questions)}: {question['question']}")
        for index, text in enumerate(options, start=1):
            print(f"  {index}. {text}")
        choice = read_option(f"Sua resposta [1-{len(options)}]: ",
                             [str(index) for index in range(1, len(options) + 1)])
        if options[int(choice) - 1] == question["answer"]:
            score += 1
            print("Correto!")
        else:
            print(f"Incorreto. Resposta certa: {question['answer']}")
        print(f"Explicação: {question['explanation']}")
    return score


def quiz_menu(app):
    print("\n--- QUIZ DE MÚLTIPLA ESCOLHA ---")
    print("As questões são montadas a partir de resumos da Wikipedia (API gratuita).")
    subject = choose_math_subject(app)
    if subject is None:
        return
    total = read_integer("Quantas questões deseja responder (1 a 10)? ", maximum=10)
    while True:
        print(f"Consultando a API para {subject}...")
        try:
            questions = app.generate_math_quiz(subject, limit=total)
            break
        except API_ERRORS as error:
            print(f"Não foi possível montar o quiz: {error}")
            if not read_yes_no("Tentar novamente? (S/N): "):
                return
    score = run_quiz(questions)
    print(f"\nResultado: {score} de {len(questions)} questões corretas "
          f"({round(100 * score / len(questions))}%).")
    pause()


def main():
    app = SmartStudy(JsonStorage())
    crawler = OpenLibraryCrawler()
    actions = {
        "1": lambda: intelligent_mode(app),
        "2": lambda: scan_document(app),
        "3": lambda: gallery(app),
        "4": lambda: qr_reader(app),
        "5": lambda: schedule_menu(app),
        "6": lambda: academic_search(app, crawler),
        "7": lambda: flashcards_menu(app),
        "8": lambda: quiz_menu(app)
    }
    print("Dados carregados. Alterações serão salvas em data/smartstudy.json.")
    while True:
        show_menu()
        try:
            option = read_option("Selecione uma funcionalidade: ", MAIN_OPTIONS)
        except (KeyboardInterrupt, EOFError):
            print("\nExecução interrompida. Seus dados permanecem salvos.")
            break
        if option == "0":
            print("\nSmartStudy encerrado. Seus dados permanecem salvos.")
            break
        try:
            actions[option]()
        except (KeyboardInterrupt, EOFError):
            print("\nOperação interrompida pelo usuário.")
        except Exception as error:
            print(f"\nNão foi possível concluir a operação: {error}")
            print("Os dados anteriores permanecem preservados.")
            pause()


if __name__ == "__main__":
    main()
