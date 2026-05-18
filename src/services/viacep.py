"""
MedControl – serviço de consulta ao ViaCEP.

Isola toda a lógica de rede num módulo separado para facilitar
testes unitários (basta fazer mock de `requests.get`).
"""

import re
import requests
from dataclasses import dataclass
from typing import Optional


@dataclass
class Endereco:
    cep: str
    logradouro: str
    bairro: str
    cidade: str
    estado: str

    def __str__(self) -> str:
        return f"{self.logradouro}, {self.bairro} – {self.cidade}/{self.estado}"


class CEPInvalidoError(ValueError):
    """CEP com formato incorreto (não são 8 dígitos)."""


class CEPNaoEncontradoError(LookupError):
    """CEP válido mas não localizado na base do ViaCEP."""


class CEPConexaoError(ConnectionError):
    """Falha de rede ao consultar o ViaCEP."""


def _normalizar_cep(cep: str) -> str:
    """Remove traços/espaços e valida que restam exatamente 8 dígitos."""
    limpo = re.sub(r"\D", "", cep)
    if len(limpo) != 8:
        raise CEPInvalidoError(
            f"CEP deve conter 8 dígitos numéricos. Recebido: '{cep}'"
        )
    return limpo


def buscar_endereco(cep: str, timeout: int = 5) -> Endereco:
    """
    Consulta a API pública do ViaCEP e retorna um objeto Endereco.

    Parâmetros
    ----------
    cep     : string com o CEP (com ou sem traço/espaço).
    timeout : segundos de espera pela resposta HTTP.

    Exceções
    --------
    CEPInvalidoError      – formato inválido (não são 8 dígitos).
    CEPNaoEncontradoError – CEP não existe na base do ViaCEP.
    CEPConexaoError       – erro de rede / timeout.
    """
    cep_limpo = _normalizar_cep(cep)
    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"

    try:
        resposta = requests.get(url, timeout=timeout)
        resposta.raise_for_status()
    except requests.exceptions.Timeout:
        raise CEPConexaoError("Tempo limite excedido ao consultar o ViaCEP.")
    except requests.exceptions.ConnectionError:
        raise CEPConexaoError(
            "Sem conexão com a internet. Verifique sua rede e tente novamente."
        )
    except requests.exceptions.RequestException as exc:
        raise CEPConexaoError(f"Erro ao acessar o ViaCEP: {exc}")

    dados = resposta.json()

    if dados.get("erro"):
        raise CEPNaoEncontradoError(
            f"CEP {cep_limpo} não encontrado. Verifique o número e tente novamente."
        )

    return Endereco(
        cep=dados.get("cep", cep_limpo),
        logradouro=dados.get("logradouro", ""),
        bairro=dados.get("bairro", ""),
        cidade=dados.get("localidade", ""),
        estado=dados.get("uf", ""),
    )
