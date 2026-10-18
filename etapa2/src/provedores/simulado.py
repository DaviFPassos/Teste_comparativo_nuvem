"""
Provedor SIMULADO — só para verificações locais do programa.

Responde sem rede e sem custo, para conferir o executor, o registro e as
métricas. Toda resposta e todo registro saem marcados `simulado: true`, e o
executor se recusa a gravar execuções simuladas em etapa2/resultados/ (onde só
entram coletas reais). Nada que sai daqui é evidência de execução.
"""

from .base import ErroProvedor, Provedor, Resposta


class ProvedorSimulado(Provedor):
    nome = "simulado"
    servico = "SIMULADO — sem chamada a serviço real"
    regiao = "local"
    simulado = True

    def __init__(self, respostas=None, falhas=None, padrao="neutro"):
        """
        respostas: {texto: rótulo} — o rótulo devolvido para cada texto.
        falhas:    {texto: [codigo, codigo, ...]} — erros a levantar, em ordem,
                   nas primeiras tentativas desse texto (depois responde).
        """
        self.respostas = dict(respostas or {})
        self.falhas = {t: list(c) for t, c in (falhas or {}).items()}
        self.padrao = padrao
        self.chamadas = []

    def analisar(self, texto):
        self.chamadas.append(texto)
        pendentes = self.falhas.get(texto)
        if pendentes:
            codigo = pendentes.pop(0)
            raise ErroProvedor(codigo, f"falha simulada ({codigo})")
        rotulo = self.respostas.get(texto, self.padrao)
        return Resposta(rotulo_original=rotulo, bruta={"simulado": True, "rotulo": rotulo})
