"""
MedControl – camada de acesso ao banco de dados.

Responsabilidades:
  • Criar / migrar o schema do SQLite (incluindo novos campos de endereço).
  • Expor funções limpas de leitura e escrita para perfil, medicamentos e histórico.
  • Fornecer get_endereco_str() para que futuros módulos de alerta possam
    recuperar o endereço completo como string sem conhecer os detalhes do schema.
"""

import sqlite3
from pathlib import Path
from typing import Optional

# Localização padrão do banco – raiz do projeto (medcontrol.db)
# __file__ aqui é src/database/db.py → .parent = database → .parent = src → .parent = raiz
DB_PATH = Path(__file__).parent.parent.parent / "medcontrol.db"


# ---------------------------------------------------------------------------
# Conexão
# ---------------------------------------------------------------------------

def get_connection(path: Path = DB_PATH) -> sqlite3.Connection:
    """Retorna uma conexão com row_factory configurada."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Inicialização / Migração
# ---------------------------------------------------------------------------

def init_db(path: Path = DB_PATH) -> None:
    """
    Cria as tabelas necessárias caso não existam e executa migrações
    incrementais (adiciona colunas novas sem destruir dados existentes).
    """
    conn = get_connection(path)
    cur = conn.cursor()

    # -- Tabela perfil -------------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS perfil (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nome       TEXT,
            idade      INTEGER,
            cuidadores TEXT
        )
    """)

    # -- Migração: campos de endereço ----------------------------------------
    _ensure_column(cur, "perfil", "cep",        "TEXT DEFAULT ''")
    _ensure_column(cur, "perfil", "logradouro", "TEXT DEFAULT ''")
    _ensure_column(cur, "perfil", "bairro",     "TEXT DEFAULT ''")
    _ensure_column(cur, "perfil", "cidade",     "TEXT DEFAULT ''")
    _ensure_column(cur, "perfil", "estado",     "TEXT DEFAULT ''")

    # -- Tabela medicamentos --------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS medicamentos (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nome            TEXT,
            dose            TEXT,
            tipo            TEXT,
            quantidade      REAL,
            via             TEXT,
            intervalo_horas INTEGER,
            horario_inicio  TEXT
        )
    """)

    # -- Tabela historico -----------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            id_medicamento  INTEGER,
            data_hora       TEXT,
            status          TEXT,
            justificativa   TEXT
        )
    """)

    conn.commit()
    conn.close()


def _ensure_column(cur: sqlite3.Cursor, table: str, column: str, definition: str) -> None:
    """Adiciona `column` à `table` somente se ainda não existir."""
    cur.execute(f"PRAGMA table_info({table})")
    existing = {row["name"] for row in cur.fetchall()}
    if column not in existing:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


# ---------------------------------------------------------------------------
# Perfil – leitura
# ---------------------------------------------------------------------------

def get_perfil(path: Path = DB_PATH) -> Optional[sqlite3.Row]:
    """Retorna a primeira linha da tabela perfil ou None."""
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM perfil LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row


def get_endereco_str(path: Path = DB_PATH) -> str:
    """
    Retorna o endereço completo do idoso como string formatada.
    Retorna string vazia se nenhum perfil estiver cadastrado.
    """
    perfil = get_perfil(path)
    if not perfil:
        return ""

    partes = [
        perfil["logradouro"],
        perfil["bairro"],
        perfil["cidade"],
        perfil["estado"],
        perfil["cep"],
    ]
    return ", ".join(p for p in partes if p)


# ---------------------------------------------------------------------------
# Perfil – escrita
# ---------------------------------------------------------------------------

def salvar_perfil(
    nome: str,
    idade: int,
    cuidadores: str,
    cep: str = "",
    logradouro: str = "",
    bairro: str = "",
    cidade: str = "",
    estado: str = "",
    path: Path = DB_PATH,
) -> None:
    """
    Insere ou atualiza (upsert) o perfil do idoso.
    O sistema mantém apenas um perfil (id = 1).
    """
    conn = get_connection(path)
    cur = conn.cursor()

    cur.execute("SELECT id FROM perfil LIMIT 1")
    row = cur.fetchone()

    if row:
        cur.execute("""
            UPDATE perfil
               SET nome=?, idade=?, cuidadores=?,
                   cep=?, logradouro=?, bairro=?, cidade=?, estado=?
             WHERE id=?
        """, (nome, idade, cuidadores, cep, logradouro, bairro, cidade, estado, row["id"]))
    else:
        cur.execute("""
            INSERT INTO perfil (nome, idade, cuidadores, cep, logradouro, bairro, cidade, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, idade, cuidadores, cep, logradouro, bairro, cidade, estado))

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Medicamentos
# ---------------------------------------------------------------------------

def get_medicamentos(path: Path = DB_PATH) -> list:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM medicamentos")
    rows = cur.fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------------------------
# Histórico
# ---------------------------------------------------------------------------

def registrar_historico(
    id_medicamento: int,
    data_hora: str,
    status: str,
    justificativa: str = "",
    path: Path = DB_PATH,
) -> None:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO historico (id_medicamento, data_hora, status, justificativa)
        VALUES (?, ?, ?, ?)
    """, (id_medicamento, data_hora, status, justificativa))
    conn.commit()
    conn.close()


def get_historico(path: Path = DB_PATH) -> list:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute("""
        SELECT h.*, m.nome AS nome_medicamento
          FROM historico h
          LEFT JOIN medicamentos m ON h.id_medicamento = m.id
         ORDER BY h.data_hora DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows
