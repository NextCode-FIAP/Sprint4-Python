"""Persistência local dos dados do SmartStudy em JSON."""
import json
import os
from pathlib import Path


class JsonStorage:
    """Centraliza leitura e gravação segura do arquivo JSON."""

    def __init__(self, file_path="data/smartstudy.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self):
        """Carrega os dados; cria a estrutura inicial se necessário."""
        if not self.file_path.exists():
            return self.default_data()

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError("A estrutura principal do JSON deve ser um objeto.")
            return self._complete_data(data)
        except (json.JSONDecodeError, OSError, ValueError) as error:
            print(f"[AVISO] Não foi possível ler os dados: {error}")
            print("[AVISO] Um arquivo de segurança será criado.")
            backup = self.file_path.with_suffix(".corrompido.json")
            try:
                os.replace(self.file_path, backup)
            except OSError:
                pass
            return self.default_data()

    def save(self, data):
        """Grava primeiro em arquivo temporário e depois substitui o original."""
        temporary = self.file_path.with_suffix(".tmp")
        try:
            with temporary.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            os.replace(temporary, self.file_path)
            return True
        except OSError as error:
            print(f"[ERRO] Não foi possível salvar os dados: {error}")
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            return False

    @staticmethod
    def default_data():
        return {
            "gallery": [],
            "preferences": {},
            "schedule": [],
            "resources": [],
            "flashcards": []
        }

    def _complete_data(self, data):
        """Adiciona chaves ausentes sem apagar informações existentes."""
        defaults = self.default_data()
        for key, value in defaults.items():
            data.setdefault(key, value)
        return data
