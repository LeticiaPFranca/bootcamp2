"""
MedControl – serviço de integração com Google Maps.

Abre o navegador padrão do sistema apontando para a localização
do idoso usando a API pública de busca do Google Maps.
Usa apenas a biblioteca nativa `webbrowser` — sem dependências extras.
"""

import webbrowser
from urllib.parse import quote_plus
from src.database.db import get_endereco_str, get_perfil


def _montar_query(logradouro: str, bairro: str, cidade: str, estado: str = "") -> str:
    """Concatena os campos em uma string de busca normalizada."""
    partes = [logradouro, bairro, cidade]
    if estado:
        partes.append(estado)
    return " ".join(p for p in partes if p)


def abrir_rota_no_maps() -> tuple[bool, str]:
    """
    Lê o endereço do banco e abre o Google Maps no navegador padrão.

    Retorna
    -------
    (sucesso: bool, mensagem: str)
        sucesso=True  → navegador aberto com sucesso.
        sucesso=False → mensagem explica o motivo da falha.
    """
    perfil = get_perfil()

    if perfil is None:
        return False, "Nenhum perfil cadastrado. Salve o perfil antes de traçar a rota."

    logradouro = perfil["logradouro"] or ""
    bairro     = perfil["bairro"]     or ""
    cidade     = perfil["cidade"]     or ""
    estado     = perfil["estado"]     or ""

    if not any([logradouro, bairro, cidade]):
        return False, (
            "Endereço incompleto. Busque o CEP e salve o perfil antes de traçar a rota."
        )

    query = _montar_query(logradouro, bairro, cidade, estado)
    url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(query)}"

    try:
        webbrowser.open(url)
        return True, f"Google Maps aberto para: {query}"
    except Exception as exc:
        return False, f"Não foi possível abrir o navegador: {exc}"


def get_maps_url_from_str(endereco_str: str) -> str:
    """
    Utilitário para futuros módulos de alerta:
    recebe a string retornada por get_endereco_str() e devolve a URL pronta.

    Exemplo de uso em alertas de inatividade:
        endereco = get_endereco_str()
        url = get_maps_url_from_str(endereco)
        enviar_notificacao(body=f"Localização: {url}")
    """
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(endereco_str)}"
