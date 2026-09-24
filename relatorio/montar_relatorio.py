# /// script
# requires-python = ">=3.10"
# ///
"""
Monta relatorio/relatorio_etapa1.md a partir das fontes já existentes.

O relatório NÃO é digitado à parte: ele é montado dos mesmos arquivos que o
repositório entrega, para que não exista divergência entre o capítulo e o
relatório. As partes exclusivas do relatório (introdução, seleção, síntese
geral e limitações) ficam em relatorio/partes/.

    uv run relatorio/montar_relatorio.py          # gera o .md
    uv run relatorio/montar_relatorio.py --html   # gera também o .html

O HTML existe para ser exportado em PDF pelo navegador (Ctrl+P → Salvar como
PDF), evitando instalar LaTeX. Ele embute as imagens dos gráficos em base64,
de modo que o arquivo abre sozinho, sem depender de caminhos relativos.
"""

import base64
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).parent.parent
PARTES = RAIZ / "relatorio" / "partes"
SAIDA_MD = RAIZ / "relatorio" / "relatorio_etapa1.md"
SAIDA_HTML = RAIZ / "relatorio" / "relatorio_etapa1.html"

INTEGRANTES = ["Davi Fonseca Passos", "Rafael Fonseca Pessoa", "Lucca Melo Nunes"]

CAPA = f"""# Comparação de Serviços de Inteligência Artificial em Nuvem

## Etapa 1 — Análise Comparativa

**Disciplina:** Computação em Nuvem

**Programa:** Mestrado em Ciência da Computação — Universidade de Fortaleza (UNIFOR)

**Integrantes:**

{chr(10).join('- ' + n for n in INTEGRANTES)}

**Provedores analisados:** Amazon Web Services · Microsoft Azure · Google Cloud

**Região de referência:** US East · **Moeda:** USD · **Preços consultados em:** 23/09/2026

---
"""


def promover_titulos(texto, nivel_base):
    """
    Reposiciona os títulos do capítulo na hierarquia do relatório.

    Cada capítulo é escrito para ser lido sozinho (começa em '# '). Dentro do
    relatório ele precisa virar uma seção numerada, então todos os níveis
    descem junto.
    """
    linhas = []
    for linha in texto.split("\n"):
        m = re.match(r"^(#{1,6}) ", linha)
        if m:
            linha = "#" * min(6, len(m.group(1)) + nivel_base) + linha[m.end() - 1:]
        linhas.append(linha)
    return "\n".join(linhas)


def montar():
    partes = [CAPA, (PARTES / "01_introducao.md").read_text(encoding="utf-8"),
              (PARTES / "02_selecao.md").read_text(encoding="utf-8")]

    capitulos = [
        ("3", RAIZ / "etapa1" / "nlp.md"),
        ("4", RAIZ / "etapa1" / "visao.md"),
        ("5", RAIZ / "etapa1" / "fala.md"),
    ]
    for numero, caminho in capitulos:
        texto = caminho.read_text(encoding="utf-8")
        # o '# Categoria N — ...' do capítulo vira '## N. ...' do relatório
        texto = re.sub(r"^# Categoria \d+ — ", f"# {numero}. ", texto, count=1)
        partes.append(promover_titulos(texto, 1))

    partes.append((PARTES / "03_sintese_geral.md").read_text(encoding="utf-8"))
    partes.append((PARTES / "04_limitacoes.md").read_text(encoding="utf-8"))

    fontes = (RAIZ / "referencias" / "fontes.md").read_text(encoding="utf-8")
    # promove primeiro (as seções internas descem para '###'), depois renomeia o
    # título do arquivo para a seção numerada do relatório
    fontes = promover_titulos(fontes, 1)
    fontes = re.sub(r"^## Fontes consultadas", "## 8. Referências", fontes, count=1)
    partes.append(fontes)

    partes.append(
        f"\n---\n\n*Relatório montado automaticamente a partir dos arquivos do "
        f"repositório em {date.today().strftime('%d/%m/%Y')} por "
        f"`relatorio/montar_relatorio.py`. Para regerar: "
        f"`uv run relatorio/montar_relatorio.py --html`.*\n"
    )
    return "\n\n".join(partes)


# --------------------------------------------------------------------------
# Conversão Markdown -> HTML. Cobre o subconjunto usado no relatório
# (títulos, tabelas, listas, código, imagens, negrito, itálico e links).
# --------------------------------------------------------------------------

CSS = """
:root { --tinta:#1a1a18; --fraca:#5c5b55; --linha:#e0dfd9; --fundo:#fff;
        --destaque:#2a78d6; --codigo-fundo:#f6f6f4; }
* { box-sizing:border-box; }
body { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
       line-height:1.65; color:var(--tinta); background:var(--fundo);
       max-width:52rem; margin:0 auto; padding:3rem 2rem 5rem; font-size:15px; }
h1 { font-size:2rem; line-height:1.2; margin:0 0 .4rem; letter-spacing:-.02em; }
h2 { font-size:1.45rem; margin:2.8rem 0 .9rem; padding-bottom:.35rem;
     border-bottom:2px solid var(--linha); letter-spacing:-.01em; }
h3 { font-size:1.15rem; margin:2rem 0 .6rem; }
h4 { font-size:1rem; margin:1.5rem 0 .5rem; color:var(--fraca); }
p, li { margin:.6rem 0; }
table { border-collapse:collapse; width:100%; margin:1.2rem 0; font-size:.88rem; }
th, td { border:1px solid var(--linha); padding:.5rem .65rem; text-align:left;
         vertical-align:top; }
th { background:var(--codigo-fundo); font-weight:600; }
tr:nth-child(even) td { background:#fafaf8; }
code { background:var(--codigo-fundo); padding:.12em .35em; border-radius:3px;
       font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace; font-size:.86em; }
pre { background:var(--codigo-fundo); padding:.9rem 1.1rem; border-radius:6px;
      overflow-x:auto; border:1px solid var(--linha); }
pre code { background:none; padding:0; font-size:.84rem; }
img { max-width:100%; height:auto; display:block; margin:1.4rem auto;
      border:1px solid var(--linha); border-radius:6px; }
blockquote { border-left:3px solid var(--destaque); margin:1rem 0; padding:.2rem 0 .2rem 1rem;
             color:var(--fraca); }
hr { border:none; border-top:1px solid var(--linha); margin:2.5rem 0; }
a { color:var(--destaque); }
@media print {
  body { max-width:none; padding:0; font-size:10.5pt; }
  h2 { page-break-after:avoid; } h3 { page-break-after:avoid; }
  table, pre, img { page-break-inside:avoid; }
  a { color:var(--tinta); text-decoration:none; }
}
"""


def embutir_imagem(caminho_rel):
    caminho = (RAIZ / "relatorio" / caminho_rel).resolve()
    if not caminho.exists():
        return None
    dados = base64.b64encode(caminho.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{dados}"


def inline(texto):
    texto = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",
                   lambda m: f'<img alt="{m.group(1)}" src="{embutir_imagem(m.group(2)) or m.group(2)}">',
                   texto)
    texto = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', texto)
    texto = re.sub(r"`([^`]+)`", r"<code>\1</code>", texto)
    texto = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", texto)
    texto = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", texto)
    return texto


def md_para_html(md):
    saida, linhas, i = [], md.split("\n"), 0
    while i < len(linhas):
        linha = linhas[i]

        if linha.startswith("```"):
            bloco = []
            i += 1
            while i < len(linhas) and not linhas[i].startswith("```"):
                bloco.append(linhas[i].replace("&", "&amp;").replace("<", "&lt;"))
                i += 1
            saida.append("<pre><code>" + "\n".join(bloco) + "</code></pre>")
            i += 1
            continue

        if linha.startswith("|") and i + 1 < len(linhas) and re.match(r"^\|[\s:|-]+\|$", linhas[i + 1]):
            cabecalho = [c.strip() for c in linha.strip("|").split("|")]
            i += 2
            corpo = []
            while i < len(linhas) and linhas[i].startswith("|"):
                corpo.append([c.strip() for c in linhas[i].strip("|").split("|")])
                i += 1
            html = ["<table><thead><tr>"]
            html += [f"<th>{inline(c)}</th>" for c in cabecalho]
            html.append("</tr></thead><tbody>")
            for linha_corpo in corpo:
                html.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in linha_corpo) + "</tr>")
            html.append("</tbody></table>")
            saida.append("".join(html))
            continue

        m = re.match(r"^(#{1,6}) (.+)$", linha)
        if m:
            n = len(m.group(1))
            saida.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
            i += 1
            continue

        if re.match(r"^[-*] ", linha):
            itens = []
            while i < len(linhas) and re.match(r"^[-*] ", linhas[i]):
                itens.append(f"<li>{inline(linhas[i][2:])}</li>")
                i += 1
            saida.append("<ul>" + "".join(itens) + "</ul>")
            continue

        if re.match(r"^\d+\. ", linha):
            itens = []
            while i < len(linhas) and re.match(r"^\d+\. ", linhas[i]):
                itens.append(f"<li>{inline(re.sub(r'^\d+\. ', '', linhas[i]))}</li>")
                i += 1
            saida.append("<ol>" + "".join(itens) + "</ol>")
            continue

        if linha.startswith("> "):
            saida.append(f"<blockquote>{inline(linha[2:])}</blockquote>")
            i += 1
            continue

        if linha.strip() == "---":
            saida.append("<hr>")
            i += 1
            continue

        if linha.strip():
            paragrafo = [linha]
            i += 1
            while i < len(linhas) and linhas[i].strip() and not re.match(
                    r"^(#{1,6} |\||[-*] |\d+\. |> |```|---$)", linhas[i]):
                paragrafo.append(linhas[i])
                i += 1
            saida.append(f"<p>{inline(' '.join(paragrafo))}</p>")
            continue

        i += 1

    return "\n".join(saida)


def main():
    md = montar()
    SAIDA_MD.write_text(md, encoding="utf-8")
    print(f"gerado: {SAIDA_MD.relative_to(RAIZ)}  ({len(md.splitlines())} linhas)")

    if "--html" in sys.argv:
        html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Etapa 1 — Comparação de Serviços de IA em Nuvem</title>
<style>{CSS}</style>
</head>
<body>
{md_para_html(md)}
</body>
</html>"""
        SAIDA_HTML.write_text(html, encoding="utf-8")
        print(f"gerado: {SAIDA_HTML.relative_to(RAIZ)}  "
              f"({len(html) / 1024:.0f} KB, com gráficos embutidos)")
        print("\nPara o PDF: uv run relatorio/gerar_pdf.py  (ou Ctrl+P no navegador).")


if __name__ == "__main__":
    main()
