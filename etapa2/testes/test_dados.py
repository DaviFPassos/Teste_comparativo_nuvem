"""
Amostragem e anotação, com um CSV fictício no formato do B2W-Reviews01.

Os rótulos aqui são FICTÍCIOS, preenchidos pelo teste no papel dos anotadores.
"""

import csv
import json
import random

import pytest

import amostrar
import anotacao

CAMPOS_B2W = ["submission_date", "reviewer_id", "product_id", "product_name", "product_brand",
              "site_category_lv1", "site_category_lv2", "review_title", "overall_rating",
              "recommend_to_a_friend", "review_text", "reviewer_birth_year", "reviewer_gender",
              "reviewer_state"]


def _fonte(caminho, textos):
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_B2W)
        w.writeheader()
        for i, (estrelas, texto) in enumerate(textos):
            w.writerow({"review_text": texto, "overall_rating": estrelas, "site_category_lv1": "Casa",
                        "reviewer_id": f"segredo{i}", "reviewer_gender": "F", "reviewer_state": "CE",
                        "reviewer_birth_year": "1990"})


def test_filtros_excluem_vazio_duplicata_e_dado_pessoal(tmp_path):
    fonte = tmp_path / "b2w.csv"
    _fonte(fonte, [("5", "Ótimo produto"), ("1", "   "), ("4", "Muito bom"), ("3", "muito  BOM"),
                   ("2", "liguem 85 98765-4321"), ("1", "rastreio PP075161001BR"),
                   ("2", "NF 1762472 errada"), ("3", "email a@b.com"), ("4", "Chegou rápido")])
    cand, motivos = amostrar.elegiveis(amostrar.ler_fonte(fonte))
    assert sorted(c["texto"] for c in cand) == ["Chegou rápido", "Ótimo produto"]
    assert motivos["texto vazio"] == 1
    assert motivos["texto duplicado na fonte"] == 2          # as DUAS cópias saem
    assert sum(v for k, v in motivos.items() if "dado pessoal" in k) == 4


def test_nenhum_campo_pessoal_chega_aos_candidatos(tmp_path):
    fonte = tmp_path / "b2w.csv"
    _fonte(fonte, [(str(1 + k % 5), f"texto número {chr(65 + k)}{chr(65 + k)}") for k in range(20)])
    cand, _ = amostrar.elegiveis(amostrar.ler_fonte(fonte))
    escolhidos = amostrar.sortear(cand, 2, random.Random(1))
    linhas = amostrar.numerar(escolhidos, "t", random.Random(1))
    amostrar.gravar_csv(tmp_path / "c.csv", linhas)
    cabecalho = (tmp_path / "c.csv").read_text(encoding="utf-8").splitlines()[0].split(",")
    assert cabecalho == amostrar.CAMPOS_SAIDA
    conteudo = (tmp_path / "c.csv").read_text(encoding="utf-8")
    assert "segredo" not in conteudo and "1990" not in conteudo


def test_sorteio_estratificado_e_reprodutivel_e_ids_nao_revelam_estrela(tmp_path):
    cand = [{"texto": f"t{k}", "estrelas": 1 + k % 5, "linha_origem": k, "categoria_produto": "",
             "caracteres": 2, "bytes_utf8": 2} for k in range(500)]
    a = amostrar.numerar(amostrar.sortear(cand, 10, random.Random(3)), "t", random.Random(3))
    b = amostrar.numerar(amostrar.sortear(cand, 10, random.Random(3)), "t", random.Random(3))
    assert a == b
    assert sorted(x["estrelas"] for x in a) == sorted([1, 2, 3, 4, 5] * 10)
    primeiros = [x["estrelas"] for x in a[:10]]
    assert len(set(primeiros)) > 1                             # IDs iniciais não são todos 1 estrela


def _preparar_candidatos(dados, n_teste=12):
    dados.mkdir(parents=True, exist_ok=True)
    linhas = [{"id": f"t{k:03d}", "texto": f"texto {k}", "estrelas": 3, "categoria_produto": "Casa",
               "linha_origem": k, "caracteres": 7, "bytes_utf8": 7} for k in range(1, n_teste + 1)]
    linhas.append({"id": "p001", "texto": "piloto", "estrelas": 5, "categoria_produto": "Casa",
                   "linha_origem": 999, "caracteres": 6, "bytes_utf8": 6})
    amostrar.gravar_csv(dados / "candidatos_teste.csv", linhas[:-1])
    amostrar.gravar_csv(dados / "candidatos_piloto.csv", linhas[-1:])


def _preencher(dados, quem, rotulos, separador=","):
    """Simula o anotador salvando a planilha — inclusive como o Excel pt-BR (;)."""
    caminho = dados / "anotacao" / f"planilha_{quem}.csv"
    linhas = anotacao.ler_csv(caminho)
    for l in linhas:
        l["rotulo"] = rotulos[l["id"]]
    with open(caminho, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=anotacao.CAMPOS_PLANILHA, delimiter=separador)
        w.writeheader()
        w.writerows(linhas)


def test_fluxo_completo_de_anotacao(tmp_path):
    dados = tmp_path / "dados"
    _preparar_candidatos(dados)
    anotacao.main(["--dados", str(dados), "planilhas"])
    a_ids = [l["id"] for l in anotacao.ler_csv(dados / "anotacao" / "planilha_A.csv")]
    b_ids = [l["id"] for l in anotacao.ler_csv(dados / "anotacao" / "planilha_B.csv")]
    assert sorted(a_ids) == sorted(b_ids) and a_ids != b_ids          # ordens diferentes
    assert "estrelas" not in (dados / "anotacao" / "planilha_A.csv").read_text(encoding="utf-8-sig")

    # sem nomes, não consolida
    with pytest.raises(SystemExit, match="nomes"):
        anotacao.main(["--dados", str(dados), "consolidar"])
    (dados / "anotacao" / "anotadores.json").write_text(json.dumps({"A": "Ana", "B": "Beto"}))

    classes = ["positivo"] * 4 + ["negativo"] * 4 + ["neutro"] * 2 + ["misto"] * 2
    rot_a = {f"t{k:03d}": c for k, c in enumerate(classes, start=1)} | {"p001": "positivo"}
    rot_b = dict(rot_a) | {"t001": "neutro", "t005": "misto"}      # duas divergências
    _preencher(dados, "A", rot_a)
    _preencher(dados, "B", rot_b, separador=";")                    # salvo pelo Excel pt-BR
    anotacao.main(["--dados", str(dados), "consolidar"])
    conc = json.loads((dados / "anotacao" / "concordancia.json").read_text())
    assert conc["divergencias"] == 2 and conc["pendentes"] == 2
    assert conc["concordancia_bruta"] == pytest.approx(11 / 13, abs=1e-4)   # gravado com 4 casas

    with pytest.raises(SystemExit, match="sem decisão"):
        anotacao.main(["--dados", str(dados), "montar"])

    # os anotadores discutem e registram a decisão
    div = anotacao.ler_csv(dados / "anotacao" / "divergencias.csv")
    for d in div:
        d["rotulo_final"] = "positivo" if d["id"] == "t001" else "negativo"
        d["justificativa"] = "discutido em reunião"
    anotacao.gravar_csv(dados / "anotacao" / "divergencias.csv", anotacao.CAMPOS_DIVERGENCIA, div,
                        para_humanos=True)
    anotacao.main(["--dados", str(dados), "consolidar"])
    anotacao.main(["--dados", str(dados), "montar", "--max-por-classe", "3"])

    teste = anotacao.ler_csv(dados / "teste.csv")
    contagem = {c: sum(1 for l in teste if l["rotulo_referencia"] == c) for c in anotacao.CLASSES_PRINCIPAIS}
    assert contagem == {"positivo": 3, "negativo": 3, "neutro": 2}  # teto 3; só 2 neutros
    assert {l["subconjunto"] for l in teste} == {"teste"}
    misto = anotacao.ler_csv(dados / "exploratorio_misto.csv")
    assert [l["id"] for l in misto] == ["t011", "t012"]            # mistos separados ANTES das APIs
    assert len(anotacao.ler_csv(dados / "piloto.csv")) == 1
    t001 = next(l for l in anotacao.ler_csv(dados / "anotacoes.csv") if l["id"] == "t001")
    assert t001["decisao"] == "discussao" and t001["rotulo_final"] == "positivo"

    with pytest.raises(SystemExit, match="congelado"):
        anotacao.main(["--dados", str(dados), "montar"])           # não remonta por cima


def test_rotulo_invalido_na_planilha_e_apontado(tmp_path):
    dados = tmp_path / "dados"
    _preparar_candidatos(dados, n_teste=2)
    anotacao.main(["--dados", str(dados), "planilhas"])
    (dados / "anotacao" / "anotadores.json").write_text(json.dumps({"A": "Ana", "B": "Beto"}))
    _preencher(dados, "A", {"t001": "positivo", "t002": "Positivo ", "p001": "bom"})
    _preencher(dados, "B", {"t001": "positivo", "t002": "", "p001": "neutro"})
    with pytest.raises(SystemExit, match="inválidos"):
        anotacao.main(["--dados", str(dados), "consolidar"])
