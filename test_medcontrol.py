"""
MedControl – Testes automatizados (pytest)

Cobertura:
  • src/services/viacep.py  – validação de CEP, parsing, erros de rede
  • src/database/db.py      – migração, upsert de perfil, get_endereco_str
"""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_temp_db() -> Path:
    """Cria um banco temporário e retorna seu Path."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    return Path(tmp.name)


# ---------------------------------------------------------------------------
# Testes: src/services/viacep.py
# ---------------------------------------------------------------------------

from src.services.viacep import (
    buscar_endereco,
    CEPInvalidoError,
    CEPNaoEncontradoError,
    CEPConexaoError,
    _normalizar_cep,
)


class TestNormalizarCEP:
    def test_cep_valido_sem_traco(self):
        assert _normalizar_cep("01310100") == "01310100"

    def test_cep_valido_com_traco(self):
        assert _normalizar_cep("01310-100") == "01310100"

    def test_cep_com_espacos(self):
        assert _normalizar_cep("01310 100") == "01310100"

    def test_cep_curto_levanta_erro(self):
        with pytest.raises(CEPInvalidoError):
            _normalizar_cep("1234")

    def test_cep_longo_levanta_erro(self):
        with pytest.raises(CEPInvalidoError):
            _normalizar_cep("013101001")

    def test_cep_letras_levanta_erro(self):
        with pytest.raises(CEPInvalidoError):
            _normalizar_cep("ABCD-EFG")


class TestBuscarEndereco:
    def _mock_resposta(self, dados: dict, status_code: int = 200):
        mock = MagicMock()
        mock.status_code = status_code
        mock.json.return_value = dados
        mock.raise_for_status = MagicMock()
        return mock

    @patch("src.services.viacep.requests.get")
    def test_busca_valida_retorna_endereco(self, mock_get):
        mock_get.return_value = self._mock_resposta({
            "cep": "01310-100",
            "logradouro": "Avenida Paulista",
            "bairro": "Bela Vista",
            "localidade": "São Paulo",
            "uf": "SP",
        })
        end = buscar_endereco("01310100")
        assert end.logradouro == "Avenida Paulista"
        assert end.cidade == "São Paulo"
        assert end.estado == "SP"

    @patch("src.services.viacep.requests.get")
    def test_cep_inexistente_levanta_erro(self, mock_get):
        mock_get.return_value = self._mock_resposta({"erro": True})
        with pytest.raises(CEPNaoEncontradoError):
            buscar_endereco("00000000")

    @patch("src.services.viacep.requests.get")
    def test_timeout_levanta_conexao_error(self, mock_get):
        import requests as req
        mock_get.side_effect = req.exceptions.Timeout()
        with pytest.raises(CEPConexaoError):
            buscar_endereco("01310100")

    @patch("src.services.viacep.requests.get")
    def test_sem_internet_levanta_conexao_error(self, mock_get):
        import requests as req
        mock_get.side_effect = req.exceptions.ConnectionError()
        with pytest.raises(CEPConexaoError):
            buscar_endereco("01310100")


# ---------------------------------------------------------------------------
# Testes: src/database/db.py
# ---------------------------------------------------------------------------

from src.database.db import init_db, salvar_perfil, get_perfil, get_endereco_str


class TestInitDB:
    def test_cria_tabelas(self):
        db = _make_temp_db()
        init_db(db)
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = {r[0] for r in cur.fetchall()}
        conn.close()
        assert {"perfil", "medicamentos", "historico"}.issubset(tabelas)

    def test_colunas_endereco_criadas(self):
        db = _make_temp_db()
        init_db(db)
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(perfil)")
        colunas = {r[1] for r in cur.fetchall()}
        conn.close()
        for col in ("cep", "logradouro", "bairro", "cidade", "estado"):
            assert col in colunas, f"Coluna '{col}' não encontrada em perfil"

    def test_idempotente(self):
        """Chamar init_db duas vezes não deve levantar exceção."""
        db = _make_temp_db()
        init_db(db)
        init_db(db)  # segunda chamada — sem erro


class TestSalvarPerfil:
    def test_insert_e_update(self):
        db = _make_temp_db()
        init_db(db)

        salvar_perfil("Maria", 72, "João", cep="01310-100",
                      logradouro="Av. Paulista", bairro="Bela Vista",
                      cidade="São Paulo", estado="SP", path=db)

        perfil = get_perfil(db)
        assert perfil["nome"] == "Maria"
        assert perfil["logradouro"] == "Av. Paulista"

        # Update
        salvar_perfil("Maria Silva", 73, "João", path=db)
        perfil = get_perfil(db)
        assert perfil["nome"] == "Maria Silva"
        assert perfil["idade"] == 73

    def test_apenas_um_perfil(self):
        db = _make_temp_db()
        init_db(db)
        salvar_perfil("A", 60, "", path=db)
        salvar_perfil("B", 70, "", path=db)

        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM perfil")
        count = cur.fetchone()[0]
        conn.close()
        assert count == 1


class TestGetEnderecoStr:
    def test_sem_perfil_retorna_vazio(self):
        db = _make_temp_db()
        init_db(db)
        assert get_endereco_str(db) == ""

    def test_retorna_string_formatada(self):
        db = _make_temp_db()
        init_db(db)
        salvar_perfil("Ana", 65, "", logradouro="Rua das Flores",
                      bairro="Centro", cidade="Campinas", estado="SP", path=db)
        result = get_endereco_str(db)
        assert "Rua das Flores" in result
        assert "Campinas" in result

    def test_campos_vazios_ignorados(self):
        db = _make_temp_db()
        init_db(db)
        salvar_perfil("Ana", 65, "", cidade="Campinas", path=db)
        result = get_endereco_str(db)
        # não deve ter vírgulas duplas ou espaços extras
        assert ",," not in result
        assert "Campinas" in result
