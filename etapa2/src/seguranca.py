"""
Proteções de segurança da coleta real. Só biblioteca padrão.

Três regras, as mesmas de testes/rodar_testes.py e testes/conftest.py (que não
são importados aqui porque dependem do pytest):

1. Credencial só no .env local (ignorado pelo git) ou nas configurações das CLIs
   (`gcloud auth application-default login`), nunca em arquivo versionável.
2. Antes de chamar qualquer serviço, procurar chave em arquivo que o git
   publicaria — e abortar se achar.
3. Tudo o que é gravado em etapa2/resultados/ passa por `sanitizar`: o
   repositório é público, e endpoint de recurso ou ID de projeto identificam a
   conta de quem rodou, mesmo sem ser senha.
"""

import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[2]
ARQUIVO_ENV = RAIZ / ".env"

# Variáveis lidas pela coleta. Os VALORES nunca são impressos nem gravados.
VARIAVEIS = {
    "azure": ("AZURE_LANGUAGE_ENDPOINT", "AZURE_LANGUAGE_KEY"),
    "google": ("GOOGLE_CLOUD_PROJECT",),
}

# Padrões que exigem um VALOR de chave, para não acusar modelos com campos vazios.
_PADROES_DE_CHAVE = [
    r"-----BEGIN [A-Z ]*PRIVATE KEY",          # chave privada (ex.: JSON de conta de serviço)
    r"AKIA[0-9A-Z]{16}",                        # chave de acesso da AWS
    r"AZURE_\w*KEY\s*=\s*[A-Za-z0-9]{20,}",     # chave de recurso da Azure em KEY=valor
    r"\"private_key_id\"\s*:\s*\"[0-9a-f]{20,}",
]
# Extensões que não carregam texto: não há como uma chave estar "escrita" nelas.
_BINARIOS = {".png", ".jpg", ".jpeg", ".pdf", ".flac", ".lock", ".gif", ".webp"}


def carregar_env(caminho=ARQUIVO_ENV):
    """Lê KEY=VALOR do .env sem sobrescrever o ambiente e sem imprimir valores."""
    lidas = []
    if not caminho.exists():
        return lidas
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        nome, valor = linha.split("=", 1)
        valor = valor.strip().strip('"').strip("'")
        if valor:
            os.environ.setdefault(nome.strip(), valor)
            lidas.append(nome.strip())
    return lidas


def faltando(provedor):
    """Variáveis obrigatórias ausentes para o provedor (lista de nomes)."""
    return [v for v in VARIAVEIS[provedor] if not os.environ.get(v)]


def chaves_soltas_no_repositorio(raiz=RAIZ):
    """Arquivos que o git publicaria (versionados ou novos) e contêm cara de chave."""
    try:
        saida = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=raiz, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        raise SystemExit("Não foi possível listar os arquivos do git; a checagem de "
                         "credenciais não pode ser feita, e a coleta não continua sem ela.")
    padrao = re.compile("|".join(_PADROES_DE_CHAVE))
    suspeitos = []
    for nome in saida.splitlines():
        caminho = raiz / nome
        if caminho.suffix.lower() in _BINARIOS or not caminho.is_file():
            continue
        try:
            if padrao.search(caminho.read_text(encoding="utf-8", errors="ignore")):
                suspeitos.append(nome)
        except OSError:
            continue
    return suspeitos


def identificadores_da_conta():
    """Valores que, sem ser senha, identificam a conta de quem rodou."""
    valores = [os.environ.get("GOOGLE_CLOUD_PROJECT")]
    endpoint = os.environ.get("AZURE_LANGUAGE_ENDPOINT")
    if endpoint:
        host = urlparse(endpoint).hostname or ""
        valores += [host, host.split(".")[0]]
    return sorted({v for v in valores if v}, key=len, reverse=True)


_PADROES_DE_CONTA = [
    (re.compile(r"projects/[^/\s\"]+"), "projects/<removido: projeto>"),
    (re.compile(r"[a-z0-9-]+\.cognitiveservices\.azure\.com"),
     "<removido: recurso>.cognitiveservices.azure.com"),
    (re.compile(r"[a-z0-9-]+\.api\.cognitive\.microsoft\.com"),
     "<removido: recurso>.api.cognitive.microsoft.com"),
]


def sanitizar(objeto, identificadores=None):
    """Remove de uma estrutura JSON tudo o que identifica a conta ou dá acesso."""
    if identificadores is None:
        identificadores = identificadores_da_conta()
    if isinstance(objeto, dict):
        return {sanitizar(k, identificadores): sanitizar(v, identificadores)
                for k, v in objeto.items()}
    if isinstance(objeto, list):
        return [sanitizar(v, identificadores) for v in objeto]
    if isinstance(objeto, str):
        if re.match(r"https?://", objeto) and "?" in objeto:
            objeto = objeto.split("?", 1)[0] + "?<removido: parâmetros>"
        for valor in identificadores:
            objeto = objeto.replace(valor, "<removido: identificador da conta>")
        for padrao, troca in _PADROES_DE_CONTA:
            objeto = padrao.sub(troca, objeto)
        # a chave em si nunca deveria aparecer numa resposta; se aparecer, sai
        chave = os.environ.get("AZURE_LANGUAGE_KEY")
        if chave and len(chave) >= 16:
            objeto = objeto.replace(chave, "<removido: chave>")
    return objeto
