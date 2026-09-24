# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright"]
# ///
"""
Converte o relatório HTML da Etapa 1 em PDF, gravando em pdfs/.

    uv run relatorio/gerar_pdf.py

Usa o Chromium do Playwright — o mesmo motor de renderização de um navegador —
então o CSS de impressão embutido no HTML (que evita quebra de página no meio
de tabelas e figuras) é respeitado exatamente como em Ctrl+P → Salvar como PDF.

Na primeira execução o Chromium é baixado para ~/.cache/ms-playwright (cerca de
150 MB). Não exige sudo nem instalação no sistema.

Opções:
    --sem-regerar     não remonta o HTML antes de converter
    --resolver-libs   em Debian/Ubuntu, baixa para o diretório do usuário as
                      bibliotecas de sistema que faltarem ao Chromium

Nota sobre WSL e imagens enxutas de Ubuntu: o Chromium é ligado à libasound
(áudio), que não é necessária para gerar PDF mas precisa existir para ele
iniciar. Se faltar, --resolver-libs baixa o pacote e extrai em
~/.local/lib/chromium-deps, sem sudo e sem alterar o sistema.
"""

import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).parent.parent
HTML = RAIZ / "relatorio" / "relatorio_etapa1.html"
SAIDA = RAIZ / "pdfs" / "relatorio_etapa1.pdf"
DIR_LIBS = Path.home() / ".local" / "lib" / "chromium-deps"

FORMATO = "A4"
MARGENS = {"top": "18mm", "bottom": "18mm", "left": "16mm", "right": "16mm"}


def preparar_ambiente():
    """Coloca as bibliotecas locais no caminho de busca, se existirem."""
    if DIR_LIBS.is_dir():
        atual = os.environ.get("LD_LIBRARY_PATH", "")
        os.environ["LD_LIBRARY_PATH"] = f"{DIR_LIBS}:{atual}" if atual else str(DIR_LIBS)


def regerar_html():
    """Remonta o HTML a partir dos capítulos, para o PDF não sair defasado."""
    print("Regerando o HTML a partir dos capítulos...")
    r = subprocess.run(["uv", "run", str(RAIZ / "relatorio" / "montar_relatorio.py"), "--html"],
                       cwd=RAIZ, capture_output=True, text=True)
    saida = (r.stdout if r.returncode == 0 else (r.stderr or r.stdout)).strip()
    prefixo = "  " if r.returncode == 0 else "  [falhou, seguindo com o HTML existente] "
    for linha in saida.splitlines():
        print(prefixo + linha)


def bibliotecas_faltando():
    """Devolve a lista de bibliotecas de sistema que o Chromium não encontra."""
    cache = Path.home() / ".cache" / "ms-playwright"
    binarios = list(cache.glob("**/chrome-headless-shell")) + list(cache.glob("**/chrome"))
    if not binarios:
        return []
    r = subprocess.run(["ldd", str(binarios[0])], capture_output=True, text=True)
    return sorted({l.split("=>")[0].strip() for l in r.stdout.splitlines() if "not found" in l})


def resolver_libs(faltando):
    """Baixa e extrai as bibliotecas ausentes no diretório do usuário (sem sudo)."""
    pacotes = {"libasound.so.2": "libasound2"}
    alvos = [pacotes[l] for l in faltando if l in pacotes]
    if not alvos:
        print(f"  não sei qual pacote fornece: {', '.join(faltando)}")
        return False

    DIR_LIBS.mkdir(parents=True, exist_ok=True)
    tmp = Path("/tmp/chromium-deps-download")
    tmp.mkdir(exist_ok=True)

    for pacote in alvos:
        print(f"  baixando {pacote}...")
        if subprocess.run(["apt-get", "download", pacote], cwd=tmp,
                          capture_output=True, text=True).returncode != 0:
            print(f"  não foi possível baixar {pacote} com 'apt-get download'")
            return False
        deb = next(tmp.glob(f"{pacote}_*.deb"), None)
        if not deb:
            return False
        subprocess.run(["dpkg-deb", "-x", str(deb), str(tmp / "extraido")], check=True)

    for so in (tmp / "extraido").rglob("lib*.so.*"):
        destino = DIR_LIBS / so.name
        if not destino.exists():
            destino.write_bytes(so.read_bytes()) if so.is_file() else None
    # recria o link sem versão (libasound.so.2 -> libasound.so.2.0.0)
    for so in DIR_LIBS.glob("*.so.*.*"):
        link = DIR_LIBS / ".".join(so.name.split(".")[:3])
        if not link.exists():
            link.symlink_to(so.name)

    print(f"  bibliotecas extraídas em {DIR_LIBS}")
    preparar_ambiente()
    return True


def garantir_chromium():
    from playwright.sync_api import sync_playwright

    def sobe():
        try:
            with sync_playwright() as p:
                p.chromium.launch().close()
            return True
        except Exception:
            return False

    if sobe():
        return True

    if not (Path.home() / ".cache" / "ms-playwright").exists():
        print("Baixando o Chromium (~150 MB, só desta vez)...")
        r = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("  falhou: " + (r.stderr or r.stdout).strip()[:300])
            return False
        if sobe():
            return True

    faltando = bibliotecas_faltando()
    if faltando:
        print(f"O Chromium não inicia: falta {', '.join(faltando)} no sistema.")
        if "--resolver-libs" in sys.argv:
            print("Resolvendo sem sudo...")
            if resolver_libs(faltando) and sobe():
                return True
        else:
            print("Rode novamente com --resolver-libs para baixar isso no seu diretório,")
            print("sem sudo e sem alterar o sistema:")
            print("    uv run relatorio/gerar_pdf.py --resolver-libs")
    return False


def converter():
    from playwright.sync_api import sync_playwright

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page()
        # As imagens estão embutidas em base64, então o file:// basta.
        pagina.goto(HTML.resolve().as_uri(), wait_until="networkidle")
        pagina.pdf(path=str(SAIDA), format=FORMATO, margin=MARGENS,
                   print_background=True, prefer_css_page_size=False)
        navegador.close()


def main():
    if not HTML.exists():
        print(f"ERRO: {HTML.relative_to(RAIZ)} não existe.")
        print("Gere-o antes com: uv run relatorio/montar_relatorio.py --html")
        sys.exit(1)

    preparar_ambiente()

    if "--sem-regerar" not in sys.argv:
        regerar_html()

    if not garantir_chromium():
        print("\nAlternativa: abra o HTML no navegador e use Ctrl+P → Salvar como PDF.")
        sys.exit(1)

    print("Convertendo para PDF...")
    converter()
    print(f"\ngerado: {SAIDA.relative_to(RAIZ)}  ({SAIDA.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
