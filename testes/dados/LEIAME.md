# Dados de teste

Três entradas reais, uma por categoria, cada uma com **resultado esperado conhecido** em [`gabarito.json`](gabarito.json). A frase do texto e a do áudio são a mesma, de propósito: o mesmo conteúdo atravessa as três categorias.

| Arquivo | Conteúdo | Resultado esperado |
|---|---|---|
| `frase.txt` | "O atendimento foi excelente." | Sentimento **positivo** |
| `cachorro.jpg` | Fotografia de um labrador chocolate sentado na grama | Rótulo **dog** entre os devolvidos |
| `frase.flac` | A mesma frase, falada em pt-BR | Transcrição contendo **atendimento** e **excelente** |

## Origem e licença

### `cachorro.jpg`

- **Obra:** "Official Portrait of Buddy the Dog", 22/04/1998
- **Autor:** White House Photograph Office (gestão Clinton, 1993–2001)
- **Licença:** domínio público (obra do governo federal dos EUA)
- **Fonte:** https://commons.wikimedia.org/wiki/File:Official_Portrait_of_Buddy_the_Dog_-_DPLA_-_8bb24feae78ce1f060addb5682fc48e6.jpg
- **Versão usada:** miniatura de 1280×1680 px gerada pelo Wikimedia Commons (o original tem 2400×3150), JPEG, 690 KB

### `frase.flac`

- **Gerado por síntese de voz**, localmente, com o [Piper](https://github.com/OHF-Voice/piper1-gpl) (`piper-tts` 1.8.0) e a voz `pt_BR-faber-medium`, treinada sobre conjunto de dados com licença **CC0**
- Meio segundo de silêncio antes e depois da fala, como em uma gravação natural
- FLAC, PCM 16 bits, 22.050 Hz, mono, 2,52 s
- **Conferência independente:** transcrito localmente pelo Whisper (`faster-whisper`, modelo `base`), sem nenhum serviço de nuvem, resultou exatamente em "O atendimento foi excelente."

A voz sintetizada foi escolhida porque o texto falado é conhecido com exatidão. O arquivo pode ser substituído por uma gravação de voz humana da mesma frase, com o mesmo nome: os testes de formato seguem valendo se ele respeitar os limites (FLAC, até 2 canais, entre 16.000 e 48.000 Hz).

## Integridade

As evidências dos testes reais registram o SHA-256 da entrada usada, para provar que foi este arquivo, e não outro, que cada serviço recebeu.

```
cd0dcd39dee24e00b84be63ab7b63d7ef3401726d68d02a855ec0ed970f632db  frase.txt
06127a61576cb3d33657ca220e190e6ad88135a52b8c1f2a2487b37a6fac2c82  cachorro.jpg
94a03a9bf1f7b37b384027e2ce9c237aa2ce39ce9d91435c04b8ba395bed95ee  frase.flac
```
