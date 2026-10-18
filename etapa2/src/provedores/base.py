"""
Interface comum dos adaptadores.

Cada adaptador faz UMA chamada por `analisar(texto)`, sem novas tentativas
próprias: as tentativas são do executor, que mede e registra cada uma. Por isso
os adaptadores desligam explicitamente as novas tentativas embutidas nos SDKs —
o da Azure tenta de novo por padrão e o do Google repete por até 600 s em
DeadlineExceeded/ServiceUnavailable. Deixá-las ligadas esconderia falhas e
somaria esperas à latência medida.
"""

from dataclasses import dataclass, field

# Códigos de erro comuns. `transitorio` diz se vale tentar de novo.
TRANSITORIOS = {"limite", "timeout", "servidor", "rede"}
CODIGOS = TRANSITORIOS | {"autenticacao", "cota_esgotada", "entrada_invalida",
                          "resposta_invalida", "desconhecido"}
# Erros que tornam inútil continuar com o provedor nesta execução.
INTERROMPEM_PROVEDOR = {"autenticacao", "cota_esgotada"}


@dataclass
class Resposta:
    rotulo_original: str | None          # classe do serviço (Azure) ou None (Google)
    score: float | None = None           # score contínuo (Google) ou None
    magnitude: float | None = None       # só Google
    confiancas: dict | None = None       # só Azure: positive/neutral/negative
    idioma: str | None = None            # idioma informado na resposta, se houver
    versao_modelo: str | None = None     # quando o serviço informa
    bruta: dict = field(default_factory=dict)   # resposta original em JSON


class ErroProvedor(Exception):
    def __init__(self, codigo, mensagem, status_http=None, bruta=None):
        if codigo not in CODIGOS:
            codigo = "desconhecido"
        super().__init__(f"[{codigo}] {mensagem}")
        self.codigo = codigo
        self.mensagem = mensagem
        self.status_http = status_http
        self.bruta = bruta

    @property
    def transitorio(self):
        return self.codigo in TRANSITORIOS


class Provedor:
    nome = "base"
    servico = ""
    regiao = ""
    simulado = False

    def analisar(self, texto):              # pragma: no cover - interface
        raise NotImplementedError

    def descrever(self):
        """Configuração do adaptador, SEM segredos, gravada na execução."""
        return {"nome": self.nome, "servico": self.servico, "regiao": self.regiao,
                "simulado": self.simulado}
