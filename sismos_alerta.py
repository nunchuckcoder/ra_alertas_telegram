# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Osvaldo Cipriano (github.com/nunchuckcoder)

"""Alerta de sismos de grande magnitude (em qualquer parte do mundo)."""

from datetime import datetime, timezone

from telegram.ext import ContextTypes

from alertas_core import processar_sismos
from config import MIN_MAGNITUDE_ALERTA

ARQUIVO_SISMOS = "sismos_notificados.json"


async def verificar_sismos_graves(context: ContextTypes.DEFAULT_TYPE) -> None:
    params = {
        "format": "json",
        "minmag": str(MIN_MAGNITUDE_ALERTA),
        "limit": "10",
        "orderby": "time",
        "end": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
    }

    await processar_sismos(
        context,
        ficheiro_estado=ARQUIVO_SISMOS,
        params=params,
        titulo="🚨 <b>Sismo de Grande Magnitude Detetado!</b>",
    )
