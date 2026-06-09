<<<<<<< HEAD
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Osvaldo Cipriano (github.com/nunchuckcoder)

import html
import logging

from telegram import LinkPreviewOptions, Update
from telegram.ext import ContextTypes

from config import (
    SEISMIC_FORMAT,
    SEISMIC_LIMIT,
    SEISMIC_MINMAG,
    SEISMIC_START,
    SEISMIC_END,
    SISMOS_API,
)
from http_session import get_session

logger = logging.getLogger(__name__)

# ------------------------- CONFIGURAÇÕES DA MAGNITUDE ----------------------


def cor_magnitude(mag: float) -> str:
    if mag >= 6:
        return "🔴"  # Vermelho
    elif mag >= 5:
        return "🟠"  # Laranja
    elif mag >= 2:
        return "🟢"  # Verde
    else:
        return "⚪"  # Neutro (abaixo de 2)


# ------------------------- COMANDOS DO BOT --------------------------------


async def sismos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    params = {
        "start": SEISMIC_START,
        "format": SEISMIC_FORMAT,
        "minmag": str(SEISMIC_MINMAG),
        "limit": str(SEISMIC_LIMIT),
    }
    if SEISMIC_END:
        params["end"] = SEISMIC_END

    try:
        session = get_session()
        async with session.get(SISMOS_API, params=params) as response:
            data = await response.json()

        eventos = data.get("features", [])
        if not eventos:
            await _responder(update, "❌ Não foram encontrados sismos com os critérios definidos.")
            return

        mensagem = "🌍 <b>Últimos Sismos:</b>\n\n"
        for evento in eventos:
            props = evento.get("properties", {})
            geo = evento.get("geometry", {})

            mag = props.get("mag", "?")
            magtype = props.get("magtype", "?")
            profundidade = props.get("depth", "?")
            lugar = props.get("flynn_region", "Região desconhecida")
            datahora = props.get("time", "").replace("T", " ").split(".")[0]

            coords = geo.get("coordinates") or [None, None]
            longitude, latitude = (coords + [None, None])[:2]

            if latitude and longitude:
                link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
                mapa_texto = f'🗺️ <a href="{html.escape(link)}">Ver no mapa</a>'
            else:
                mapa_texto = "🗺️ Localização desconhecida"

            try:
                mag_valor = float(mag)
            except (ValueError, TypeError):
                mag_valor = 0
            cor = cor_magnitude(mag_valor)

            mensagem += (
                f"📍 <b>{html.escape(str(lugar))}</b>\n"
                f"🕒 {html.escape(datahora)}\n"
                f"💥️ Magnitude: {cor} {html.escape(str(magtype))} {html.escape(str(mag))}\n"
                f"📏 Profundidade: {html.escape(str(profundidade))} Km\n"
                f"{mapa_texto}\n\n"
            )

        await _responder(update, mensagem.strip(), com_links=True)

    except Exception as erro:
        logger.exception("Erro ao obter dados sísmicos")
        await _responder(update, f"⚠️ Erro ao obter dados sísmicos: {html.escape(str(erro))}")


async def magnitude_sismica(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explica os diferentes tipos de magnitude sísmica."""
    mensagem = (
        "📊 <b>Tipos de Magnitude Sísmica:</b>\n\n"
        "🔸 <b>ML (Magnitude Local ou de Richter)</b>:\n"
        "Baseia-se na amplitude das ondas sísmicas registadas por sismógrafos próximos. "
        "É usada principalmente para sismos locais.\n\n"
        "🔸 <b>mb (Magnitude de Ondas de Corpo)</b>:\n"
        "Calculada a partir das ondas que atravessam o interior da Terra (ondas P e S). "
        "É usada em sismos maiores e mais distantes.\n\n"
        "🔸 <b>Mw (Magnitude de Momento)</b>:\n"
        "É a escala mais moderna e precisa. Baseia-se nas características físicas da falha "
        "(como área de ruptura e deslocamento). É especialmente fiável para grandes sismos, "
        "pois não perde precisão como as outras escalas."
    )
    await _responder(update, mensagem)


# ------------------------- AUXILIAR ---------------------------------------


async def _responder(update: Update, texto: str, com_links: bool = False) -> None:
    """Responde tanto a comandos diretos como a callbacks de menu, em HTML."""
    preview = LinkPreviewOptions(is_disabled=True) if com_links else None
    if update.message:
        await update.message.reply_text(texto, parse_mode="HTML", link_preview_options=preview)
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            texto, parse_mode="HTML", link_preview_options=preview
        )
=======
# ================================================================================ #
#                                                                                  #
# Ficheiro:      sismos.py                                                         #
# Autor:         NunchuckCoder                                                     #
# Versão:        1.0                                                               #
# Data:          Julho 2025                                                        #
# Descrição:     Funções utilitárias para obter e formatar dados sísmicos usando   #
#                uma API de sismos e enviar para o Telegram.                       #
# Licença:       MIT License                                                       #
#                                                                                  #
# ================================================================================ #

import os
import aiohttp
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

# ================================================================================ #
# ------------------------ CARREGAR VARIÁVEIS DE AMBIENTE ------------------------ #
# ================================================================================ #

load_dotenv()

SISMOS_API = os.getenv("SISMOS_API")

# ================================================================================ #
# -------------------------- CONFIGURAÇÕES DA MAGNITUDE -------------------------- #
# ================================================================================ #

def cor_magnitude(mag: float) -> str:
    if mag >= 6:
        return "🔴"  # Vermelho
    elif mag >= 5:
        return "🟠"  # Laranja
    elif mag >= 2:
        return "🟢"  # Verde
    else:
        return "⚪"  # Neutro (abaixo de 2)

# ================================================================================ #
# -------------------------------- COMANDOS DO BOT ------------------------------- #
# ================================================================================ #

async def sismos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    params = {
        "start": os.getenv("SEISMIC_START"),
        "format": os.getenv("SEISMIC_FORMAT", "json"),
        "minmag": os.getenv("SEISMIC_MINMAG", "2"),
        "limit": os.getenv("SEISMIC_LIMIT", "10")
    }

    seismic_end = os.getenv("SEISMIC_END")
    if seismic_end:
        params["end"] = seismic_end

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SISMOS_API, params=params) as response:
                data = await response.json()

        eventos = data.get("features", [])
        if not eventos:
            await update.message.reply_text("❌ Não foram encontrados sismos com os critérios definidos.")
            return

        mensagem = "🌍 *Últimos Sismos:*\n\n"
        for evento in eventos:
            props = evento.get("properties", {})
            geo = evento.get("geometry", {})

            mag = props.get("mag", "?")
            magtype = props.get("magtype", "?")
            profundidade = props.get("depth", "?")
            lugar = props.get("flynn_region", "Região desconhecida")
            datahora = props.get("time", "").replace("T", " ").split(".")[0]

            latitude = geo.get("coordinates", [None, None])[1]
            longitude = geo.get("coordinates", [None, None])[0]

            if latitude and longitude:
                link_mapa = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
                mapa_texto = f"🗺️ [Ver no mapa]({link_mapa})"
            else:
                mapa_texto = "🗺️ Localização desconhecida"

            # Cor de acordo com magnitude
            try:
                mag_valor = float(mag)
            except:
                mag_valor = 0
            cor = cor_magnitude(mag_valor)

            mensagem += (
                f"📍 *{lugar}*\n"
                f"🕒 {datahora}\n"
                f"💥️ Magnitude: {cor} {magtype} {mag}\n"
                f"📏 Profundidade: {profundidade} Km\n"
                f"{mapa_texto}\n\n"
            )

        if update.message:
            await update.message.reply_text(mensagem.strip(), parse_mode="Markdown")
        elif update.callback_query:
            await update.callback_query.message.reply_text(mensagem.strip(), parse_mode="Markdown")

    except Exception as e:
        erro_msg = f"⚠️ Erro ao obter dados sísmicos: {e}"
        if update.message:
            await update.message.reply_text(erro_msg)
        elif update.callback_query:
            await update.callback_query.message.reply_text(erro_msg)

async def magnitude_sismica(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explica os diferentes tipos de magnitude sísmica."""
    mensagem = (
        "📊 *Tipos de Magnitude Sísmica:*\n\n"
        "🔸 *ML (Magnitude Local ou de Richter)*:\n"
        "Baseia-se na amplitude das ondas sísmicas registadas por sismógrafos próximos. É usada principalmente para sismos locais.\n\n"
        "🔸 *mb (Magnitude de Ondas de Corpo)*:\n"
        "Calculada a partir das ondas que atravessam o interior da Terra (ondas P e S). É usada em sismos maiores e mais distantes.\n\n"
        "🔸 *Mw (Magnitude de Momento)*:\n"
        "É a escala mais moderna e precisa. Baseia-se nas características físicas da falha (como área de ruptura e deslocamento). "
        "É especialmente fiável para grandes sismos, pois não perde precisão como as outras escalas."
    )
    if update.message:
        await update.message.reply_markdown(mensagem)
    elif update.callback_query:
        await update.callback_query.message.reply_markdown(mensagem)
>>>>>>> 30a5fad083727b992bdfba0aa3648b41f19df41a
