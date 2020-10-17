# FTX Funding Alerter

Robo que usa um cliente HTTPS para fazer queries periódicas de funding rates na API da FTX e posta os resultados via telegram ou stdout.

## Instalação

Fazemos uso do [poetry](https://python-poetry.org/docs/#installation) para gerenciamento de dependências.

Uma vez que o poetry estiver instalado na sua maquina, abra o diretório do projeto FTX-Funding-Alerter e execute o comando:
```bash
poetry install
```

## Configuração
Fazemos uso de um arquivo .env para configuração do robo.

#### FTX API
Modifique o arquivo .env para fazer uso das suas proprias credenciais para comunicação com a API da FTX.
```bash
FTX_KEY = 29kj-641Ku1rAE0zHyw0YFfopYXkcr-BTz46SB2C
FTX_SECRET = cZ4MWnPI-mQUvCB9G0O8NQQqkcGyXMHdBKxjz22E
```

#### Telegram API
Modifique o arquivo .env para que o seu telegram bot poste as menssagens nos chats especificados pelo TELEGRAM_CHAT_ID.
```bash
TELEGRAM_TOKEN=1354102047:AAGrKzig003lHCNjvTuE38jPUPT4H4prn28
TELEGRAM_CHAT_ID=-415257929
```

#### Parametros de reportagem
É possivel também modificar o arquivo .env para configurar a lista de instrumentos pesquisados, a frequência da pesquisa, o número de instrumentos reportados, e o valor mínimo dos funding rates reportados.
```bash
LIST_OF_FUTURES=all
UPDATE_DELAY=3600
OUTPUT_NUMBER=3
OUTPUT_THRESHOLD=0
```

## Uso

```bash
poetry run python bot.py
```