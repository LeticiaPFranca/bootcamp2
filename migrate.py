"""
MedControl – Script de migração / inicialização.

Execute UMA VEZ após baixar o projeto:
    python migrate.py

O script:
  1. Detecta o banco existente (medcontrol.db na raiz do projeto).
  2. Cria todas as tabelas e adiciona colunas de endereço se necessário.
  3. Não apaga nem sobrescreve dados existentes.
"""

import sys
from pathlib import Path

# Garante que o import de src.database funciona ao executar da raiz do projeto
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from src.database.db import init_db, DB_PATH


def main():
    print(f"🔧 Migrando banco de dados: {DB_PATH}")

    if not DB_PATH.exists():
        print("   Banco não encontrado – será criado do zero.")

    init_db()

    print("✅ Migração concluída com sucesso!")
    print("   Tabelas garantidas: perfil, medicamentos, historico")
    print("   Colunas de endereço: cep, logradouro, bairro, cidade, estado")


if __name__ == "__main__":
    main()
