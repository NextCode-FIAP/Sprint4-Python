"""Funções reutilizáveis para validação de entradas."""
import re


def read_text(message):
    while True:
        value = input(message).strip()
        if value:
            return value
        print("Campo obrigatório. Tente novamente.")


def read_option(message, allowed):
    while True:
        value = input(message).strip()
        if value in allowed:
            return value
        print(f"Opção inválida. Escolha: {', '.join(allowed)}.")


def read_yes_no(message):
    while True:
        value = input(message).strip().lower()
        if value in ("s", "sim"):
            return True
        if value in ("n", "nao", "não"):
            return False
        print("Resposta inválida. Digite S ou N.")


def read_integer(message, minimum=1, maximum=None):
    while True:
        try:
            value = int(input(message).strip())
            if value < minimum or (maximum is not None and value > maximum):
                limit = f" entre {minimum} e {maximum}" if maximum is not None else f" maior ou igual a {minimum}"
                print(f"Informe um número{limit}.")
                continue
            return value
        except ValueError:
            print("Digite um número inteiro válido.")


def valid_time(value):
    return bool(re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value))
