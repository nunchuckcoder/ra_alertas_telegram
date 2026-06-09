# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Osvaldo Cipriano (github.com/nunchuckcoder)

"""Fonte única de configuração do bot.

Lê as variáveis do ficheiro `.env`, aplica defaults sensatos e valida o que
é obrigatório. Todos os outros módulos devem importar daqui em vez de
voltarem a ler `os.getenv` por conta própria.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Diretório base do projeto (independente do working directory de quem corre).
BASE_DIR = Path(__file__).resolve().parent

# Carregar variáveis do .env
load_dotenv(BASE_DIR / ".env")

# ------------------------- TELEGRAM ---------------------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ------------------------- CONFIGURAÇÕES DOS SISMOS -----------------------

SEISMIC_LIMIT = int(os.getenv("SEISMIC_LIMIT", "10"))
SEISMIC_START = os.getenv("SEISMIC_START", "2025-01-01")
SEISMIC_END = os.getenv("SEISMIC_END")  # Opcional (pode ser None)
SEISMIC_FORMAT = os.getenv("SEISMIC_FORMAT", "json")
SEISMIC_MINMAG = float(os.getenv("SEISMIC_MINMAG", "2"))

# ------------------------- CANAIS DE ALERTA -------------------------------

ALERTA_SISMOS_CHANNEL_IDS = os.getenv("ALERTA_SISMOS_CHANNEL_IDS", "")
# Lista de IDs (int) já validada — usada por todos os módulos de alerta.
CANAIS_ALERTA_SISMOS = [
    int(canal.strip())
    for canal in ALERTA_SISMOS_CHANNEL_IDS.split(",")
    if canal.strip()
]

MIN_MAGNITUDE_ALERTA = float(os.getenv("MIN_MAGNITUDE_ALERTA", "6"))
INTERVALO_VERIFICACAO = int(os.getenv("INTERVALO_VERIFICACAO", "600"))  # segundos

# ------------------------- ENDPOINTS DAS APIS -----------------------------

IPMA_API = os.getenv("IPMA_API")
FOGOS_API = os.getenv("FOGOS_API")
SISMOS_API = os.getenv("SISMOS_API")

# ------------------------- VALIDAÇÕES DE SEGURANÇA ------------------------

if not BOT_TOKEN:
    raise EnvironmentError("BOT_TOKEN não definido no ficheiro .env")
if not CANAIS_ALERTA_SISMOS:
    raise EnvironmentError(
        "ALERTA_SISMOS_CHANNEL_IDS não definido (ou inválido) no ficheiro .env"
    )
if not IPMA_API:
    raise EnvironmentError("IPMA_API não definido no ficheiro .env")
if not FOGOS_API:
    raise EnvironmentError("FOGOS_API não definido no ficheiro .env")
if not SISMOS_API:
    raise EnvironmentError("SISMOS_API não definido no ficheiro .env")
