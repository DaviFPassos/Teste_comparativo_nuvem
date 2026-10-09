"""
Confere as entradas de teste contra os limites documentados de cada provedor.

Cada limite cita a fonte registrada em referencias/fontes.md. Se alguém trocar
um arquivo de testes/dados/ por outro que algum serviço recusaria — formato
errado, grande demais, canais demais —, estes testes falham antes de qualquer
chamada à nuvem.
"""

import soundfile as sf
from PIL import Image

from conftest import AUDIO, FRASE, GABARITO, IMAGEM

MB = 1024 * 1024


# ------------------------------------------------------------------- texto

def test_frase_e_utf8_e_bate_com_o_gabarito():
    texto = FRASE.read_bytes().decode("utf-8")          # falha se não for UTF-8
    assert texto == GABARITO["texto"]["conteudo"]


def test_frase_cabe_nos_limites_dos_tres_provedores():
    texto = FRASE.read_text(encoding="utf-8")
    assert len(texto.encode("utf-8")) <= 5 * 1024       # AWS Comprehend: 5 KB (NLP-AWS-02)
    assert len(texto) <= 5120                           # Azure Language: 5.120 caracteres (NLP-AZ-02)
    assert len(texto.encode("utf-8")) <= 1_000_000      # Google NL: 1.000.000 bytes (NLP-GC-03)


def test_exemplos_de_nlp_usam_a_frase_de_teste(carregar_exemplo):
    """Os três exemplos analisam exatamente a frase de testes/dados/frase.txt."""
    frase = FRASE.read_text(encoding="utf-8")
    for arquivo, ambiente in (
        ("exemplos/nlp/aws_comprehend.py", {}),
        ("exemplos/nlp/azure_language.py", {}),
        ("exemplos/nlp/google_natural_language.py", {}),
    ):
        assert carregar_exemplo(arquivo, **ambiente).TEXTO == frase, arquivo


# ------------------------------------------------------------------ imagem

def test_imagem_e_jpeg_valido():
    with Image.open(IMAGEM) as img:
        assert img.format == "JPEG"                     # aceito pelos três (VIS-AWS-02, VIS-AZ-01, VIS-GC-02)
        # Decodifica a imagem inteira. verify() só confere o cabeçalho e deixaria
        # passar um arquivo cortado no meio.
        img.load()


def test_imagem_cabe_nos_limites_dos_tres_provedores():
    tamanho = IMAGEM.stat().st_size
    with Image.open(IMAGEM) as img:
        largura, altura = img.size
    # AWS Rekognition (VIS-AWS-02): até 5 MB enviada como bytes; de 80 a 10.000 px
    assert tamanho <= 5 * MB
    assert 80 <= min(largura, altura) and max(largura, altura) <= 10_000
    # Azure Image Analysis 4.0 (VIS-AZ-01): menos de 20 MB; de 50 a 16.000 px
    assert tamanho < 20 * MB
    assert 50 <= min(largura, altura) and max(largura, altura) <= 16_000
    # Google Cloud Vision (VIS-GC-02): até 20 MB por imagem
    assert tamanho <= 20 * MB


def test_imagem_tem_resolucao_util_para_rotulos():
    """O Google recomenda 640x480 para LABEL_DETECTION (VIS-GC-02)."""
    with Image.open(IMAGEM) as img:
        assert img.size[0] >= 640 and img.size[1] >= 480


# ------------------------------------------------------------------- áudio

def test_audio_e_flac_valido():
    info = sf.info(AUDIO)                               # falha se o arquivo estiver corrompido
    assert info.format == "FLAC"                        # AWS (FAL-AWS-02) e Azure (FAL-AZ-02) aceitam FLAC
    assert info.subtype == "PCM_16"                     # AWS recomenda FLAC ou WAV PCM 16 bits


def test_audio_cabe_nos_limites_da_aws():
    info = sf.info(AUDIO)
    assert info.channels <= 2                           # mais de 2 canais não é suportado (FAL-AWS-02)
    # alta fidelidade: de 16.000 a 48.000 Hz (FAL-AWS-02)
    assert 16_000 <= info.samplerate <= 48_000


def test_audio_tem_fala_e_nao_e_silencio():
    dados, taxa = sf.read(AUDIO, dtype="float32")
    assert 1.0 <= len(dados) / taxa <= 60.0             # duração plausível para uma frase
    assert abs(dados).max() > 0.1                       # há sinal de fala, não só silêncio


def test_exemplo_da_aws_declara_o_formato_real_do_audio(carregar_exemplo):
    """O Transcribe recebe MediaFormat explícito; tem de bater com o arquivo."""
    import inspect
    exemplo = carregar_exemplo("exemplos/fala/aws_transcribe.py")
    assert 'MediaFormat="flac"' in inspect.getsource(exemplo.iniciar_job)
    assert sf.info(AUDIO).format == "FLAC"


def test_palavras_chave_do_gabarito_estao_na_frase():
    frase = GABARITO["audio"]["transcricao_de_referencia"].lower()
    for palavra in GABARITO["audio"]["palavras_chave"]:
        assert palavra in frase
    assert GABARITO["audio"]["transcricao_de_referencia"] == FRASE.read_text(encoding="utf-8")
