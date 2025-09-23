# ================================================================================ #
#                                                                                  #
# Ficheiro:      config.py                                                         #
# Autor:         NunchuckCoder                                                     #
# Versão:        1.0                                                               #
# Data:          Julho 2025                                                        #
# Descrição:     Carrega e valida variáveis de ambiente do bot Telegram para       #
#                alertas meteorológicos, incêndios e sismos.                       #
# Licença:       MIT License                                                       #
#                                                                                  #
# ================================================================================ #

import os
from dotenv import load_dotenv

# ================================================================================ #
# ------------------------ CARREGAR VARIÁVEIS DE AMBIENTE ------------------------ #
# ================================================================================ #

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Configurações dos sismos
SEISMIC_LIMIT = int(os.getenv("SEISMIC_LIMIT", "10"))
SEISMIC_START = os.getenv("SEISMIC_START", "2025-01-01")
SEISMIC_END = os.getenv("SEISMIC_END") or None  # Pode ser None (opcional)
SEISMIC_FORMAT = os.getenv("SEISMIC_FORMAT", "json")
SEISMIC_MINMAG = float(os.getenv("SEISMIC_MINMAG", "2"))

# Canal para alertas sismos e configurações de alerta
ALERTA_SISMOS_CHANNEL_IDS = os.getenv("ALERTA_SISMOS_CHANNEL_IDS", "")
CANAIS_ALERTA_SISMOS = [int(canal.strip()) for canal in ALERTA_SISMOS_CHANNEL_IDS.split(",") if canal.strip()]

MIN_MAGNITUDE_ALERTA = float(os.getenv("MIN_MAGNITUDE_ALERTA", "6"))
INTERVALO_VERIFICACAO = int(os.getenv("INTERVALO_VERIFICACAO", "1800"))  # 30 minutos

# Endpoints das APIs (se quiseres usar diretamente no código)
IPMA_API = os.getenv("IPMA_API")
FOGOS_API = os.getenv("FOGOS_API")
SISMOS_API = os.getenv("SISMOS_API")
    
# ================================================================================ #
# --------------------------- VERIFICAÇÕES DE SEGURANÇA -------------------------- #
# ================================================================================ #

if not BOT_TOKEN:
    raise EnvironmentError("BOT_TOKEN não definido no ficheiro .env")
if not ALERTA_SISMOS_CHANNEL_IDS:
    raise EnvironmentError("ALERTA_SISMOS_CHANNEL_IDS não definido no ficheiro .env")
if not IPMA_API:
    raise EnvironmentError("IPMA_API não definido no ficheiro .env")
if not FOGOS_API:
    raise EnvironmentError("FOGOS_API não definido no ficheiro .env")
if not SISMOS_API:
    raise EnvironmentError("SISMOS_API não definido no ficheiro .env")
