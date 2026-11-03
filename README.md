<<<<<<< HEAD
# Sprint4-Python
=======
# NEXTCODE | SMARTSTUDY

## Visão geral
SmartStudy é um protótipo acadêmico em Python orientado a estudo, organização de materiais e revisão de conteúdo. A proposta foi evoluir o fluxo de um ambiente acadêmico inteligente para registrar documentos, manter grade de aulas, validar links, consultar referências externas e estudar por flashcards e quizzes.

## Objetivo do projeto
O objetivo principal é fornecer um ambiente conceitual para:
- organizar materiais e documentos de estudo;
- manter preferências por disciplina;
- registrar e consultar itens da galeria de estudos;
- validar endereços de links seguros por domínio;
- manter agenda de aulas;
- consultar referências bibliográficas externas;
- criar flashcards e quizzes a partir de conceitos matemáticos por API gratuita.

## Motivação e justificativa
A Sprint 4 resolve uma limitação da versão anterior: a perda de dados ao encerrar o programa. Com isso, a solução passou a gerenciar dados em JSON local e a separar regras de negócio, validações e armazenamento em módulos distintos. O projeto também se aproxima do conceito de um ambiente acadêmico inteligente, mantendo foco em prototipagem funcional, sem depender de câmera física, OCR real ou serviços de segurança externos.

## Tecnologias utilizadas
- Python 3.10+
- Biblioteca padrão do Python
- JSON para persistência local
- urllib para consumo da API pública Open Library
- Wikipedia REST API para conceitos matemáticos gratuitos
- Estrutura modular em orientação a objetos

## Funcionalidades principais
- Modo Inteligente: ajustes simulados por ambiente e disciplina
- Digitalização simulada de documento com OCR informado manualmente
- Galeria de estudos com listagem, pesquisa e reclassificação
- Validação simples de QR Code/URL por domínio permitido
- Grade de aulas com cadastro, visualização e exclusão
- Busca de livros acadêmicos na Open Library
- Criação de flashcards manuais e automáticos por conceito matemático
- Quiz de múltipla escolha com retorno e explicação da resposta correta

## Estrutura do projeto
- `main.py`: menu principal e navegação
- `src/system.py`: regras de negócio e integrações de API
- `src/storage.py`: persistência em JSON local
- `src/validators.py`: validações reutilizáveis de entrada
- `src/api_crawler.py`: leitura da Open Library
- `data/smartstudy.json`: armazenamento persistente dos dados

## Requisitos e execução
### Requisitos
- Python 3.10 ou superior
- Conexão com a internet somente quando necessário para consultar API externa
- Nenhuma dependência externa obrigatória

### Execução
No terminal, dentro da pasta do projeto:

```bash
python main.py
```

## Resultados esperados
O sistema consegue:
- manter registros persistentes após reinicialização;
- validar entradas e horários de aula;
- preservar informações localmente em JSON;
- gerar flashcards e quiz a partir de conceitos matemáticos públicos e gratuitos;
- manter a proposta de ferramenta acadêmica em terminal, com navegação simples e orientação a objetos.

## Integrantes do grupo
- Kaick Lima Silva — RM 574060
- Gustavo Basso — RM 572623
- Guilherme Sales — RM 572933
- Pedro Feltrin Geraldes — RM 569038
- Guilherme Kozikoski Failla — RM 571611

## Observações de escopo
- A câmera e o OCR são simulados;
- o texto reconhecido é informado manualmente pelo usuário;
- a validação de links é baseada em uma lista permitida e não substitui análise antiphishing real;
- a consulta externa de livros usa Open Library e a geração de flashcards por conceito usa a Wikipedia REST API;
- os dados locais continuam armazenados em arquivos JSON do projeto.
>>>>>>> 87215cf (Sprint4-Python)
