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

# O relatório também circula como PDF, longe do repositório. Todo link para um
# arquivo do projeto tem de apontar para a URL pública do GitHub — um caminho
# relativo funciona no repositório e morre no PDF, e um caminho absoluto vaza o
# diretório de quem gerou o arquivo. `verificar_links_do_pdf()` recusa gerar o
# relatório se algum link local escapar.
REPOSITORIO = "https://github.com/DaviFPassos/Teste_comparativo_nuvem"
BLOB = f"{REPOSITORIO}/blob/main"

CAPA = f"""# Comparação de Serviços de Inteligência Artificial em Nuvem

## Etapa 1 — Análise Comparativa

**Disciplina:** Computação em Nuvem

**Programa:** Mestrado em Ciência da Computação — Universidade de Fortaleza (UNIFOR)

**Integrantes:**

{chr(10).join('- ' + n for n in INTEGRANTES)}

**Provedores analisados:** Amazon Web Services · Microsoft Azure · Google Cloud

**Região dos preços:** `us-east-1` (AWS) · `East US` (Azure) · global em NLP e visão e `us-central1` em fala (Google Cloud)

**Moeda:** USD · **Preços consultados em:** 23/09/2026

**Repositório público (código, dados, gráficos e capítulos completos):** https://github.com/DaviFPassos/Teste_comparativo_nuvem

---
"""


def promover_titulos(texto, nivel_base):
    """
    Reposiciona os títulos do capítulo na hierarquia do relatório.

    Cada capítulo é escrito para ser lido sozinho (começa em '# '). Dentro do
    relatório ele precisa virar uma seção numerada, então todos os níveis
    descem junto.

    Blocos de código são preservados: um comentário Python começa com '#' e não
    é título nenhum — promovê-lo transformaria `# comentário` em `## comentário`
    dentro do trecho citado.
    """
    linhas = []
    dentro_de_codigo = False
    for linha in texto.split("\n"):
        if linha.lstrip().startswith("```"):
            dentro_de_codigo = not dentro_de_codigo
            linhas.append(linha)
            continue
        m = None if dentro_de_codigo else re.match(r"^(#{1,6}) ", linha)
        if m:
            linha = "#" * min(6, len(m.group(1)) + nivel_base) + linha[m.end() - 1:]
        linhas.append(linha)
    return "\n".join(linhas)


# Seções de cada capítulo que entram no relatório.
#
# O relatório precisa ser compreensível ABERTO SOZINHO, fora do repositório —
# é assim que ele chega a quem avalia. Por isso a comparação técnica entra
# inteira: entradas, saídas, formas de acesso e autenticação, limites e avisos
# oficiais de encerramento. O que fica só nos capítulos de etapa1/ é o aparato
# de rastreabilidade (tabela de fontes por afirmação, pendências de verificação)
# e o bloco de reprodutibilidade, idêntico nos três e já presente na introdução.
#
# A seção 4 (exemplos de código) é exigência explícita da seção 3 do enunciado:
# "a análise de cada categoria deverá incluir também breves exemplos de código".
# No relatório ela entra com o TRECHO ESSENCIAL de cada exemplo e o link para o
# arquivo completo no GitHub — ver `exemplos_com_trecho()`.
SECOES_MANTIDAS = ("1.", "2.", "4.", "5.", "6.", "7.")
SUBSECOES_TECNICAS = ("Funcionalidades, entradas e saídas",
                      "Entradas: formatos e limites",
                      "Entradas: formatos e origem do áudio",
                      "Saídas",
                      "Suporte a português",
                      "Suporte ao português do Brasil",
                      "Formas de acesso, autenticação e configuração",
                      "Limites operacionais e de taxa",
                      "Latência de processamento e limites operacionais",
                      "Situação do serviço")


MARCA_INICIO = "# --- TRECHO CITADO NO RELATÓRIO (início) ---"
MARCA_FIM = "# --- TRECHO CITADO NO RELATÓRIO (fim) ---"


def trecho_do_exemplo(caminho_relativo):
    """
    Extrai de um exemplo o trecho entre as marcas TRECHO CITADO NO RELATÓRIO.

    O trecho não é copiado à mão para o relatório: sai do arquivo que o
    repositório entrega, de modo que não possa divergir dele. A indentação
    comum é removida para o bloco caber na largura da página A4.
    """
    linhas = (RAIZ / caminho_relativo).read_text(encoding="utf-8").split("\n")
    try:
        ini = next(i for i, l in enumerate(linhas) if MARCA_INICIO in l)
        fim = next(i for i, l in enumerate(linhas) if MARCA_FIM in l)
    except StopIteration:
        raise SystemExit(
            f"{caminho_relativo}: faltam as marcas de trecho para o relatório. "
            f"Envolva o trecho essencial com:\n  {MARCA_INICIO}\n  ...\n  {MARCA_FIM}")

    corpo = [l for l in linhas[ini + 1:fim] if l.strip()]
    recuo = min((len(l) - len(l.lstrip()) for l in corpo), default=0)
    return "\n".join(l[recuo:] for l in linhas[ini + 1:fim]).strip("\n")


def exemplos_com_trecho(caminho_relativo):
    """
    Transforma o item de lista de um exemplo no bloco que vai para o relatório:
    título com link para o GitHub + trecho de código essencial.
    """
    return ["", f"**[`{caminho_relativo}`]({BLOB}/{caminho_relativo})** — trecho "
                f"essencial. O arquivo completo, no link, traz a autenticação por "
                f"variável de ambiente, o tratamento de erro, os limites do serviço "
                f"e a fonte da adaptação:", "",
            "```python", trecho_do_exemplo(caminho_relativo), "```", ""]


def condensar_capitulo(texto, arquivo_origem):
    """
    Reduz um capítulo ao que o relatório precisa mostrar.

    Mantém objetivo, serviços comparados, comparação técnica, cobrança, custo
    e síntese — tudo o que é preciso para ler o relatório sozinho. Descarta a
    tabela de fontes por afirmação, as pendências de verificação e o bloco de
    reprodutibilidade (idêntico nos três capítulos e já presente na introdução),
    que ficam no capítulo completo, cujo link no GitHub entra no lugar.

    Na seção 4, cada caminho de exemplo vira link para o GitHub mais o trecho
    essencial do código, extraído do próprio arquivo.
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
                    "As tabelas abaixo comparam entradas, saídas, formas de acesso, "
                    "autenticação, limites e avisos oficiais dos três serviços. O "
                    "capítulo completo — com a fonte oficial de cada afirmação e as "
                    "pendências de verificação — está em "
                    f"[`{arquivo_origem}`]({BLOB}/{arquivo_origem}).", "",
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

        # Na seção de exemplos, o caminho do arquivo vira link + trecho de código.
        exemplo = re.match(r"^- `(exemplos/[^`]+\.py)`$", linha)
        if exemplo and manter_secao and manter_sub:
            saida += exemplos_com_trecho(exemplo.group(1))
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
/* white-space:pre-wrap (em vez de pre puro) é o que faz a diferença no PDF:
   overflow-x:auto rola na tela, mas o PDF não tem scroll, e uma linha de
   código mais longa que a caixa simplesmente era cortada na borda. Com
   pre-wrap a linha quebra e o recuo (indentação) é preservado; overflow-wrap
   cobre o caso raro de um único token (uma URL, por exemplo) mais largo que
   a própria caixa. */
pre { background:var(--codigo-fundo); padding:.9rem 1.1rem; border-radius:6px;
      overflow-x:auto; border:1px solid var(--linha);
      white-space:pre-wrap; overflow-wrap:anywhere; }
pre code { background:none; padding:0; font-size:.84rem; white-space:inherit; }
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


def verificar_links_do_pdf(md):
    """
    Recusa gerar o relatório se algum link não funcionar fora do repositório.

    O PDF é lido longe dos arquivos: link relativo (`../etapa1/nlp.md`) quebra,
    e `file:///home/...` — que é no que um link relativo se transforma quando o
    navegador exporta o PDF — além de quebrar, publica o diretório de quem
    gerou o arquivo. Os dois casos são erro, não aviso.

    Imagens (`![...](...)`) ficam de fora da checagem: os gráficos entram no
    HTML embutidos em base64, então o caminho relativo nunca chega ao PDF.
    """
    problemas = []
    for imagem, alvo in re.findall(r"(!?)\[[^\]]*\]\(([^)]+)\)", md):
        if imagem == "!" or alvo.startswith(("http://", "https://", "#", "data:")):
            continue
        problemas.append(alvo)

    if problemas:
        raise SystemExit(
            "Links que não funcionam fora do repositório (use a URL do GitHub, "
            f"{BLOB}/...):\n  " + "\n  ".join(sorted(set(problemas))))


def main():
    md = montar()
    verificar_links_do_pdf(md)
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
