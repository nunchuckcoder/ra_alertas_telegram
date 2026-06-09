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
