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


# Seções de cada capítulo que entram no relatório. O detalhamento técnico
# completo (limites numéricos, cotas, formatos aceitos, autenticação) continua
# nos arquivos etapa1/*.md, que o relatório referencia — a intenção é que o
# relatório caiba em uma leitura, não que ele substitua os capítulos.
# A seção 4 (exemplos de código) é exigência explícita da seção 3 do
# enunciado: "a análise de cada categoria deverá incluir também breves
# exemplos de código". No relatório ela entra de forma curta, apontando
# os arquivos e declarando que não foram executados.
SECOES_MANTIDAS = ("1.", "2.", "4.", "5.", "6.", "7.")
SUBSECOES_TECNICAS = ("Funcionalidades, entradas e saídas", "Entradas: formatos e limites",
                      "Entradas: formatos e origem do áudio", "Situação do serviço")


def condensar_capitulo(texto, arquivo_origem):
    """
    Reduz um capítulo ao que o relatório precisa mostrar.

    Mantém objetivo, serviços comparados, cobrança, custo e síntese. Da
    comparação técnica mantém a tabela principal e os avisos oficiais de
    encerramento, que são decisivos para a escolha. Descarta o bloco de
    reprodutibilidade, idêntico nos três capítulos e já presente uma vez na
    introdução do relatório. O restante fica no capítulo completo, cujo link
    entra no lugar.
    """
    saida = []
    secao = None           # número da seção "##" corrente
    manter_secao = True    # a seção corrente entra no relatório?
    manter_sub = True      # a subseção "###" corrente entra?

    for linha in texto.split("\n"):
        cab2 = re.match(r"^## (\d+)\.", linha)
        cab3 = re.match(r"^### (?:[\d.]+ )?(.+)$", linha)

        if cab2:
            secao = cab2.group(1) + "."
            manter_secao = secao in SECOES_MANTIDAS or secao == "3."
            manter_sub = True
            if secao == "3.":
                saida += [
                    "## 3. Comparação técnica", "",
                    "As tabelas abaixo trazem a comparação que mais pesa na escolha. "
                    "O detalhamento completo — limites numéricos, cotas, formatos aceitos, "
                    f"autenticação e configuração — está em [`{arquivo_origem}`]"
                    f"(../{arquivo_origem}).", "",
                ]
            elif manter_secao:
                saida.append(linha)
            continue

        if cab3:
            titulo = cab3.group(1)
            if not manter_secao:
                manter_sub = False
            elif secao == "3.":
                manter_sub = any(s in titulo for s in SUBSECOES_TECNICAS)
            else:
                manter_sub = "Reprodutibilidade" not in titulo
            if manter_sub:
                saida.append(linha)
            continue

        if manter_secao and manter_sub:
            saida.append(linha)

    return "\n".join(saida)


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
        texto = condensar_capitulo(texto, f"etapa1/{caminho.name}")
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
table { border-collapse:collapse; width:100%; max-width:100%; margin:1.2rem 0;
        font-size:.88rem; table-layout:auto; }
th, td { border:1px solid var(--linha); padding:.5rem .65rem; text-align:left;
         vertical-align:top; }
/* Só o que de fato não quebra sozinho ganha quebra forçada: URLs e
   identificadores longos de API. Aplicar isso ao texto corrido inteiro
   quebraria palavras comuns no meio e inflaria o documento. */
td a, th a, td code, th code { overflow-wrap:anywhere; }
/* Fontes de referência. No Markdown elas são uma tabela de 6 colunas, que
   funciona bem no GitHub (onde há rolagem horizontal). Em A4 retrato, porém,
   6 colunas com URLs longas não cabem: ou a tabela é cortada, ou as colunas
   ficam tão estreitas que até o identificador quebra em três linhas. Por isso
   cada fonte vira uma ficha, que usa a largura inteira da página. */
/* As fichas de fonte são entradas curtas; em uma coluna só desperdiçam a
   largura da página. Duas colunas cortam pela metade o espaço da seção. */
.fontes-grupo { column-count:2; column-gap:1.4rem; }
.fonte { border-left:2px solid var(--linha); padding:.05rem 0 .05rem .6rem;
         margin:0 0 .5rem; page-break-inside:avoid; break-inside:avoid; }
.fonte-cabecalho { font-size:.76rem; color:var(--fraca); margin-bottom:.1rem; }
.fonte-id { font-weight:700; color:var(--tinta); font-family:ui-monospace,Menlo,Consolas,monospace; }
.fonte-estado { text-transform:uppercase; letter-spacing:.04em; font-size:.72rem; }
.fonte-titulo { font-size:.8rem; margin:.05rem 0; }
.fonte-titulo a { word-break:break-all; }
.fonte-sustenta { font-size:.78rem; margin-top:.1rem; line-height:1.45; }
.fonte-sustenta::before { content:"Sustenta: "; color:var(--fraca); font-weight:600; }
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
  body { max-width:none; padding:0; font-size:9.6pt; line-height:1.5; }
  h2 { page-break-after:avoid; } h3 { page-break-after:avoid; }
  /* Figuras e blocos de código não devem ser partidos. Tabelas SIM: proibir a
     quebra de uma tabela longa não a faz caber — apenas a empurra inteira para
     a página seguinte, deixando um vazio enorme atrás. Em vez disso, permite-se
     partir a tabela entre linhas, repetindo o cabeçalho em cada página. */
  pre, img { page-break-inside:avoid; }
  thead { display:table-header-group; }
  tr { page-break-inside:avoid; }
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


def _eh_tabela_de_fontes(cabecalho):
    """Reconhece a tabela de fontes pelo conjunto de colunas."""
    esperado = {"id", "título e url", "afirmação sustentada", "estado"}
    return esperado <= {c.strip().lower() for c in cabecalho}


def _fontes_como_fichas(linhas):
    """
    Converte as linhas da tabela de fontes em fichas legíveis em A4.

    A tabela tem 6 colunas (ID, provedor/serviço, título e URL, data de acesso,
    afirmação sustentada, estado). Em papel retrato elas não cabem lado a lado,
    então cada fonte é reescrita como um bloco que ocupa a largura inteira.
    """
    saida = []
    for linha in linhas:
        if len(linha) < 6:
            continue
        ident, provedor, titulo_url, data, sustenta, estado = linha[:6]

        # separa "Título — https://..." em título e link
        partes = re.split(r"\s+—\s+(?=https?://)", titulo_url, maxsplit=1)
        if len(partes) == 2:
            titulo, url = partes
            titulo_html = f'{inline(titulo)} — <a href="{url.strip()}">{url.strip()}</a>'
        else:
            titulo_html = inline(titulo_url)

        saida.append(
            '<div class="fonte">'
            f'<div class="fonte-cabecalho">'
            f'<span class="fonte-id">{inline(ident)}</span> · {inline(provedor)} · '
            f'consultado em {inline(data)} · '
            f'<span class="fonte-estado">{inline(estado)}</span></div>'
            f'<div class="fonte-titulo">{titulo_html}</div>'
            '</div>'
        )
    return '<div class="fontes-grupo">' + "\n".join(saida) + "</div>"


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
            if _eh_tabela_de_fontes(cabecalho):
                saida.append(_fontes_como_fichas(corpo))
                continue

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
