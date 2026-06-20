# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Osvaldo Cipriano (github.com/nunchuckcoder)

"""Lógica partilhada dos alertas sísmicos.

Os dois tipos de alerta (magnitude grave e qualquer sismo em Portugal) só
diferem nos parâmetros do pedido, no título e no filtro. Tudo o resto —
obter dados, evitar duplicados e enviar para os canais — vive aqui.
"""

import html
import json
import logging
from pathlib import Path
from typing import Callable, Optional

from telegram import LinkPreviewOptions
from telegram.ext import ContextTypes

from config import DATA_DIR, CANAIS_ALERTA_SISMOS, SISMOS_API
from http_session import get_session

logger = logging.getLogger(__name__)


# ---------------------- PERSISTÊNCIA DE ESTADO ----------------------------


def _carregar(path: Path) -> set:
    try:
        with path.open("r", encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def _guardar(path: Path, ids: set) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(list(ids), f, ensure_ascii=False, indent=2)


# ---------------------- PROCESSAMENTO DE ALERTAS --------------------------


async def processar_sismos(
    context: ContextTypes.DEFAULT_TYPE,
    *,
    ficheiro_estado: str,
    params: dict,
    titulo: str,
    incluir: Optional[Callable[[str], bool]] = None,
    transformar_lugar: Optional[Callable[[str], str]] = None,
) -> None:
    """Obtém sismos, filtra, evita duplicados e envia para os canais.

    Args:
        ficheiro_estado: nome do ficheiro JSON onde se guardam os IDs já
            notificados (ancorado ao diretório do projeto).
        params: parâmetros do pedido à API SeismicPortal.
        titulo: primeira linha da mensagem (já em HTML).
        incluir: função opcional que decide se um sismo entra (pela região).
        transformar_lugar: função opcional para formatar o nome do local.
    """
    bot = context.bot
    estado_path = DATA_DIR / ficheiro_estado
    notificados = _carregar(estado_path)
    houve_novos = False

    try:
        session = get_session()
        async with session.get(SISMOS_API, params=params) as resposta:
            if resposta.status != 200:
                logger.warning("HTTP %s ao obter sismos (%s)", resposta.status, titulo)
                return
            dados = await resposta.json()
    except Exception:
        logger.exception("Erro ao obter sismos (%s)", titulo)
        return

    for sismo in dados.get("features", []):
        props = sismo.get("properties", {})
        geo = sismo.get("geometry", {})

        lugar_raw = props.get("flynn_region", "") or ""
        if incluir is not None and not incluir(lugar_raw):
            continue

        sismo_id = props.get("unid")
        if not sismo_id or sismo_id in notificados:
            continue

        mag = props.get("mag", 0)
        magtype = props.get("magtype", "?")
        profundidade = props.get("depth", "?")
        datahora = props.get("time", "")[:16].replace("T", " ")

        coords = geo.get("coordinates") or [None, None]
        longitude, latitude = (coords + [None, None])[:2]

        lugar = transformar_lugar(lugar_raw) if transformar_lugar else lugar_raw

        if latitude and longitude:
            link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
            mapa_texto = f'🗺️ <a href="{html.escape(link)}">Ver no mapa</a>'
        else:
            mapa_texto = "🗺️ Localização desconhecida"

        mensagem = (
            f"{titulo}\n\n"
            f"📍 <b>{html.escape(str(lugar))}</b>\n"
            f"🕒 Hora: {html.escape(datahora)} UTC\n"
            f"💥 Magnitude: {html.escape(str(magtype))} <b>{html.escape(str(mag))}</b>\n"
            f"📏 Profundidade: {html.escape(str(profundidade))} Km\n"
            f"{mapa_texto}\n"
        )

        for canal_id in CANAIS_ALERTA_SISMOS:
            try:
                await bot.send_message(
                    chat_id=canal_id,
                    text=mensagem,
                    parse_mode="HTML",
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            except Exception:
                logger.exception("Erro ao enviar alerta para canal %s", canal_id)

        notificados.add(sismo_id)
        houve_novos = True

    if houve_novos:
        _guardar(estado_path, notificados)
