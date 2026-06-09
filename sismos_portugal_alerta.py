# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Osvaldo Cipriano (github.com/nunchuckcoder)

"""Alerta de qualquer sismo em Portugal (continente, Açores e Madeira)."""

from datetime import datetime, timezone

from telegram.ext import ContextTypes

from alertas_core import processar_sismos

ARQUIVO_SISMOS_PT = "sismos_portugal_notificados.json"

# Termos (em inglês, como vêm da API SeismicPortal) que identificam Portugal.
_REGIOES_PT = ("portugal", "azores", "madeira")


def _e_portugal(lugar: str) -> bool:
    lugar = lugar.lower()
    return any(regiao in lugar for regiao in _REGIOES_PT)


async def verificar_sismos_portugal(context: ContextTypes.DEFAULT_TYPE) -> None:
    params = {
        "format": "json",
        "limit": "30",  # obtém mais eventos para melhor cobertura
        "orderby": "time",
        "end": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
    }

    await processar_sismos(
        context,
        ficheiro_estado=ARQUIVO_SISMOS_PT,
        params=params,
        titulo="📢 <b>Sismo Detetado em Portugal!</b>",
        incluir=_e_portugal,
        transformar_lugar=lambda lugar: lugar.title(),
    )
