<<<<<<< HEAD
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Osvaldo Cipriano (github.com/nunchuckcoder)

import logging

from config import FOGOS_API
from http_session import get_session

# ------------------------- CONFIGURAÇÃO DE LOGS ---------------------------

logger = logging.getLogger(__name__)

# ------------------------- OBTER FOGOS DO API -----------------------------


async def obter_fogos_ativos():
    try:
        session = get_session()
        async with session.get(FOGOS_API) as response:
            if response.status != 200:
                logger.warning("Erro ao obter dados dos fogos: HTTP %d", response.status)
                return []

            dados = await response.json()
            return dados.get("data", [])
    except Exception:
        logger.exception("Erro ao obter dados dos fogos")
        return []
=======
# ================================================================================ #
#                                                                                  #
# Ficheiro:      fogos.py                                                          #
# Autor:         NunchuckCoder                                                     #
# Versão:        1.0                                                               #
# Data:          Julho 2025                                                        #
# Descrição:     Módulo para obter dados de fogos ativos através de uma API        #
#                externa. Usa aiohttp para requisições assíncronas.                #
# Licença:       MIT License                                                       #
#                                                                                  #
# ================================================================================ #

import os
import aiohttp
import logging
from dotenv import load_dotenv

# ================================================================================ #
# ----------------------------- CONFIGURAÇÃO DE LOGS ----------------------------- #
# ================================================================================ #

logger = logging.getLogger(__name__)

# ================================================================================ #
# ------------------------ CARREGAR VARIÁVEIS DE AMBIENTE ------------------------ #
# ================================================================================ #

load_dotenv()

FOGOS_API = os.getenv("FOGOS_API")

# ================================================================================ #
# ------------------------------ OBTER FOGOS DO API ------------------------------ #
# ================================================================================ #

async def obter_fogos_ativos():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(FOGOS_API) as response:
                if response.status != 200:
                    logger.warning("Erro ao obter dados dos fogos: HTTP %d", response.status)
                    return []

                dados = await response.json()
                return dados.get("data", [])
    except Exception as e:
        logger.exception("Erro ao obter dados dos fogos")
        return []
>>>>>>> 30a5fad083727b992bdfba0aa3648b41f19df41a
