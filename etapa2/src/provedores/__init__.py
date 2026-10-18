"""Adaptadores: a mesma interface para cada serviço de sentimento."""

from .base import ErroProvedor, Provedor, Resposta  # noqa: F401


def criar(nome, configuracao):
    """Instancia o adaptador pelo nome. Importa o SDK só do provedor pedido."""
    if nome == "azure":
        from .azure import ProvedorAzure
        return ProvedorAzure(**configuracao)
    if nome == "google":
        from .google import ProvedorGoogle
        return ProvedorGoogle(**configuracao)
    if nome == "simulado":
        from .simulado import ProvedorSimulado
        return ProvedorSimulado(**configuracao)
    raise ValueError(f"provedor desconhecido: {nome}")
