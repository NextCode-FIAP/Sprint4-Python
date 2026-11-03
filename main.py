"""NEXTCODE | SMARTSTUDY — Sprint 4."""
from src.storage import JsonStorage
from src.validators import read_text, read_option, read_yes_no, read_integer, valid_time
from src.system import SmartStudy
from src.api_crawler import OpenLibraryCrawler


DAYS = {
    "1": "Segunda-feira", "2": "Terça-feira", "3": "Quarta-feira",
    "4": "Quinta-feira", "5": "Sexta-feira", "6": "Sábado"
}


def pause():
    input("\nPressione Enter para voltar ao menu...")


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
        elif option == "3":
            subjects = app.available_math_subjects()
            print("Matérias disponíveis:")
            for index, item in enumerate(subjects, start=1):
                print(f"  {index}. {item}")
            while True:
                raw_subject = input("Digite a matéria ou número (ou 'sair' para cancelar): ").strip()
                if raw_subject.lower() in {"sair", "0", "exit", "quit"}:
                    print("Operação cancelada.")
                    break
                try:
                    if raw_subject.isdigit():
                        subject = subjects[int(raw_subject) - 1]
                    else:
                        subject = app.resolve_subject(raw_subject)
                    created = app.create_api_flashcards(subject, limit=10)
                    print(f"10 flashcards criados para {subject} via API gratuita.")
                    break
                except Exception as error:
                    print(f"Não foi possível gerar os flashcards: {error}")
                    retry = input("Tentar novamente? (S/N): ").strip().lower()
                    if retry in {"n", "nao", "não", "0"}:
                        break
        else:
            subject = input("Filtrar disciplina (Enter para todos): ").strip()
            cards = [card for card in app.data["flashcards"]
                     if not subject or subject.casefold() in card["subject"].casefold()]
            if not cards:
                print("Nenhum flashcard encontrado.")
                pause()
                continue
            random_cards = cards[:]
            import random
            random.shuffle(random_cards)
            for card in random_cards:
                print(f"\n[{card['subject']}] {card['question']}")
                input("Pressione Enter para revelar a resposta...")
                print(f"Resposta: {card['answer']}")
        pause()


def main():
    app = SmartStudy(JsonStorage())
    crawler = OpenLibraryCrawler()
    print("Dados carregados. Alterações serão salvas em data/smartstudy.json.")
    while True:
        show_menu()
        option = read_option("Selecione uma funcionalidade: ", ["0", "1", "2", "3", "4", "5", "6", "7"])
        actions = {
            "1": lambda: intelligent_mode(app),
            "2": lambda: scan_document(app),
            "3": lambda: gallery(app),
            "4": lambda: qr_reader(app),
            "5": lambda: schedule_menu(app),
            "6": lambda: academic_search(app, crawler),
            "7": lambda: flashcards_menu(app)
        }
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
