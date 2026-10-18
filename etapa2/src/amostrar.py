# /// script
# requires-python = ">=3.10"
# ///
"""
Sorteia, de forma reprodutível, os textos candidatos da Etapa 2.

Fonte: B2W-Reviews01 (B2W Digital), CC BY-NC-SA 4.0 —
https://github.com/americanas-tech/b2w-reviews01

    uv run etapa2/src/amostrar.py                      # lote inicial: piloto + teste
    uv run etapa2/src/amostrar.py --lote extra --teste-por-estrela 20

O que este script garante, e por quê:

- **Mesma fonte para todos.** O CSV é baixado da URL oficial e conferido pelo
  SHA-256 registrado abaixo. Se o arquivo mudar, o script para — senão o mesmo
  comando sortearia outros textos sem ninguém perceber.
- **Mesmo sorteio para todos.** Semente fixa e ordem de leitura estável.
- **Nenhum dado pessoal sai daqui.** O dataset traz gênero, ano de nascimento,
  estado e um identificador do avaliador. Nenhum desses campos é copiado.
  Textos que contêm e-mail, telefone, CPF, código de rastreio ou número de
  protocolo/nota fiscal são EXCLUÍDOS (não editados): editar
  seria uma transformação a documentar e a aplicar igualmente a todos os
  provedores; excluir é mais simples e não altera o que os serviços recebem.
- **Estrelas são só estratificação.** Sorteia-se o mesmo número de textos por
  estrela para que o conjunto tenha variedade de opinião. As estrelas NÃO são o
  gabarito: o próprio artigo do dataset mostra que reduzir a escala de 5 pontos
  a 3 classes "pode levar a conclusões erradas". O gabarito vem de anotação
  humana (etapa2/src/anotacao.py), e as planilhas de anotação não mostram as
  estrelas, para não enviesar quem anota.
- **Só biblioteca padrão**, como o resto do cálculo do projeto.
"""

import argparse
import csv
import hashlib
import json
import random
import re
import sys
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "etapa2" / "dados"

FONTE_URL = ("https://raw.githubusercontent.com/americanas-tech/b2w-reviews01/"
             "main/B2W-Reviews01.csv")
# Conferido em 18/10/2026: 49.453.175 bytes, 132.373 avaliações.
FONTE_SHA256 = "821fb0bf9f7230b0fba4e4f9fadd75a66d1a9ff0b1657810791d33007eb2ab38"
CACHE = Path.home() / ".cache" / "teste_comparativo_nuvem" / "B2W-Reviews01.csv"

SEMENTE_PADRAO = 20261018
# Azure: 5.120 "text elements" por documento. len() conta pontos de código, que
# nunca são menos que text elements — então 5.000 por len() é uma margem segura.
MAX_CARACTERES = 5000

# Padrões de dado pessoal. Preferem errar para mais: um falso positivo só tira um
# texto do sorteio; um falso negativo publicaria um dado pessoal.
PADROES_PESSOAIS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "cpf": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    "telefone": re.compile(r"(?:\(?\b\d{2}\)?\s?)?\b9?\d{4}[-\s]?\d{4}\b"),
    # Rastreio dos Correios (ex.: PP075161001BR): identifica uma entrega e,
    # por ela, um destinatário. Achado na própria fonte.
    "codigo_de_rastreio": re.compile(r"\b[A-Z]{2}\d{9}[A-Z]{2}\b", re.IGNORECASE),
    # Sequência de 7+ dígitos: protocolo de atendimento, número de nota fiscal ou
    # de pedido — identificam uma compra específica. Achado na própria fonte.
    "numero_longo": re.compile(r"\d{7,}"),
}

CAMPOS_SAIDA = ["id", "texto", "estrelas", "categoria_produto", "linha_origem",
                "caracteres", "bytes_utf8"]


def sha256_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def obter_fonte(caminho=None):
    """Devolve o CSV da fonte, baixando para o cache do usuário se preciso."""
    caminho = Path(caminho) if caminho else CACHE
    if not caminho.exists():
        if caminho != CACHE:
            raise SystemExit(f"Arquivo não encontrado: {caminho}")
        print(f"Baixando a fonte (49 MB) para {CACHE} ...")
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(FONTE_URL, CACHE)
    obtido = sha256_arquivo(caminho)
    if obtido != FONTE_SHA256:
        raise SystemExit(
            f"SHA-256 da fonte não confere.\n  esperado {FONTE_SHA256}\n  obtido   {obtido}\n"
            "A fonte mudou: o sorteio não seria o mesmo. Não continue sem registrar isso.")
    return caminho


def ler_fonte(caminho):
    """Lê o CSV (o separador real é vírgula, apesar do README do dataset)."""
    csv.field_size_limit(10 ** 9)
    with open(caminho, encoding="utf-8", newline="") as f:
        for numero, linha in enumerate(csv.DictReader(f), start=1):
            yield numero, linha


def chave_de_duplicata(texto):
    return " ".join(texto.casefold().split())


def dado_pessoal(texto):
    """Nome do primeiro padrão de dado pessoal encontrado, ou None."""
    for nome, padrao in PADROES_PESSOAIS.items():
        if padrao.search(texto):
            return nome
    return None


def elegiveis(linhas):
    """
    Filtra a fonte e devolve (candidatos, motivos_de_exclusao).

    Duplicatas: todas as cópias de um texto repetido saem. Manter a "primeira"
    faria o resultado depender da ordem do arquivo, e um texto repetido muitas
    vezes (ex.: "Muito bom") não é uma avaliação independente.
    """
    linhas = list(linhas)
    contagem = Counter(chave_de_duplicata(l["review_text"]) for _, l in linhas)
    candidatos, motivos = [], Counter()
    for numero, l in linhas:
        texto = l["review_text"].strip()
        if not texto:
            motivos["texto vazio"] += 1
            continue
        if contagem[chave_de_duplicata(texto)] > 1:
            motivos["texto duplicado na fonte"] += 1
            continue
        if len(texto) > MAX_CARACTERES:
            motivos[f"mais de {MAX_CARACTERES} caracteres"] += 1
            continue
        if l["overall_rating"] not in {"1", "2", "3", "4", "5"}:
            motivos["estrelas ausentes ou inválidas"] += 1
            continue
        tipo = dado_pessoal(texto)
        if tipo:
            motivos[f"possível dado pessoal ({tipo})"] += 1
            continue
        candidatos.append({
            "texto": texto,
            "estrelas": int(l["overall_rating"]),
            "categoria_produto": l["site_category_lv1"].strip(),
            "linha_origem": numero,
            "caracteres": len(texto),
            "bytes_utf8": len(texto.encode("utf-8")),
        })
    return candidatos, motivos


def sortear(candidatos, por_estrela, rng, excluir_linhas=()):
    """Sorteia `por_estrela` textos de cada estrela, fora de `excluir_linhas`."""
    excluir = set(excluir_linhas)
    escolhidos = []
    for estrela in (1, 2, 3, 4, 5):
        grupo = [c for c in candidatos
                 if c["estrelas"] == estrela and c["linha_origem"] not in excluir]
        if len(grupo) < por_estrela:
            raise SystemExit(f"Só há {len(grupo)} candidatos com {estrela} estrela(s).")
        escolhidos += rng.sample(grupo, por_estrela)
    return escolhidos


def numerar(textos, prefixo, rng, inicio=1):
    """
    Embaralha antes de numerar. Se os IDs seguissem a ordem do sorteio, t001–t060
    seriam todos de 1 estrela — e quem anota poderia deduzir a nota pelo ID.
    """
    textos = list(textos)
    rng.shuffle(textos)
    return [{"id": f"{prefixo}{i:03d}", **t} for i, t in enumerate(textos, start=inicio)]


def gravar_csv(caminho, linhas):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_SAIDA)
        w.writeheader()
        w.writerows(linhas)


def ler_csv(caminho):
    with open(caminho, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--fonte", help="CSV local do B2W (padrão: baixar para o cache)")
    p.add_argument("--semente", type=int, default=SEMENTE_PADRAO)
    p.add_argument("--lote", choices=("inicial", "extra"), default="inicial")
    p.add_argument("--piloto-por-estrela", type=int, default=6)
    p.add_argument("--teste-por-estrela", type=int, default=60)
    p.add_argument("--saida", type=Path, default=DADOS)
    a = p.parse_args(argv)

    fonte = obter_fonte(a.fonte)
    candidatos, motivos = elegiveis(ler_fonte(fonte))
    manifesto_caminho = a.saida / "manifesto_amostragem.json"

    if a.lote == "inicial":
        for nome in ("candidatos_piloto.csv", "candidatos_teste.csv"):
            if (a.saida / nome).exists():
                raise SystemExit(
                    f"{nome} já existe. O lote inicial é sorteado uma única vez; "
                    "para ampliar o conjunto use --lote extra.")
        rng = random.Random(a.semente)
        piloto = sortear(candidatos, a.piloto_por_estrela, rng)
        teste = sortear(candidatos, a.teste_por_estrela, rng,
                        excluir_linhas=[c["linha_origem"] for c in piloto])
        arquivos = {"candidatos_piloto.csv": numerar(piloto, "p", rng),
                    "candidatos_teste.csv": numerar(teste, "t", rng)}
        manifesto = {"lotes": []}
    else:
        if not manifesto_caminho.exists():
            raise SystemExit("Rode o lote inicial antes de um lote extra.")
        manifesto = json.loads(manifesto_caminho.read_text(encoding="utf-8"))
        usados, maior_id = set(), 0
        for arq in a.saida.glob("candidatos_*.csv"):
            for l in ler_csv(arq):
                usados.add(int(l["linha_origem"]))
                if l["id"].startswith("t"):
                    maior_id = max(maior_id, int(l["id"][1:]))
        n = len(manifesto["lotes"])
        # semente derivada: cada lote extra é reprodutível e diferente do anterior
        rng = random.Random(a.semente + n)
        extra = sortear(candidatos, a.teste_por_estrela, rng, excluir_linhas=usados)
        arquivos = {f"candidatos_teste_extra{n}.csv": numerar(extra, "t", rng, maior_id + 1)}

    for nome, linhas in arquivos.items():
        gravar_csv(a.saida / nome, linhas)
        print(f"gravado: {(a.saida / nome).relative_to(RAIZ) if a.saida.is_relative_to(RAIZ) else a.saida / nome}"
              f"  ({len(linhas)} textos)")

    manifesto.update({
        "fonte": {"nome": "B2W-Reviews01", "autoria": "B2W Digital",
                  "licenca": "CC BY-NC-SA 4.0", "url": FONTE_URL, "sha256": FONTE_SHA256},
        "filtros": {"max_caracteres": MAX_CARACTERES,
                    "duplicatas": "todas as cópias de um texto repetido são excluídas",
                    "dados_pessoais": sorted(PADROES_PESSOAIS),
                    "campos_descartados": ["reviewer_id", "reviewer_birth_year",
                                           "reviewer_gender", "reviewer_state",
                                           "product_name", "product_brand", "review_title"]},
        "elegiveis": len(candidatos),
        "excluidos_por_motivo": dict(sorted(motivos.items())),
    })
    manifesto["lotes"].append({
        "lote": a.lote, "data": date.today().isoformat(), "semente": a.semente,
        "por_estrela": {"piloto": a.piloto_por_estrela, "teste": a.teste_por_estrela}
        if a.lote == "inicial" else {"teste": a.teste_por_estrela},
        "arquivos": {nome: {"textos": len(l), "sha256": sha256_arquivo(a.saida / nome)}
                     for nome, l in arquivos.items()},
    })
    manifesto_caminho.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n",
                                 encoding="utf-8")
    print(f"elegíveis: {len(candidatos)} de {sum(motivos.values()) + len(candidatos)}")
    for motivo, n in sorted(motivos.items()):
        print(f"  excluídos — {motivo}: {n}")


if __name__ == "__main__":
    sys.exit(main())
