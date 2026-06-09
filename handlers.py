# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Osvaldo Cipriano (github.com/nunchuckcoder)

import html

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from fogos import obter_fogos_ativos
from ipma_utils import (
    formatar_mensagem_previsao_multidias,
    obter_previsao_ipma,
    obter_previsao_multidias_ipma,
)
from locais import ID_LOCAL_TO_NAME, LOCAIS_POR_DISTRITO
from sismos import magnitude_sismica, sismos

# ------------------------- AUXILIARES -------------------------------------


def _teclado_distritos(prefixo: str, por_linha: int = 3) -> InlineKeyboardMarkup:
    """Constrói o teclado com todos os distritos (callback `<prefixo><id>`)."""
    keyboard, row = [], []
    for local_id, nome in ID_LOCAL_TO_NAME.items():
        row.append(InlineKeyboardButton(nome, callback_data=f"{prefixo}{local_id}"))
        if len(row) == por_linha:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


def _teclado_localidades(localidades: list, prefixo: str, por_linha: int = 2) -> InlineKeyboardMarkup:
    """Constrói o teclado com as localidades de um distrito."""
    keyboard, row = [], []
    for local in localidades:
        row.append(
            InlineKeyboardButton(local["local"], callback_data=f"{prefixo}{local['globalIdLocal']}")
        )
        if len(row) == por_linha:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


def _nome_localidade(local_id: int) -> str:
    """Descobre o nome de uma localidade a partir do seu globalIdLocal."""
    for lista in LOCAIS_POR_DISTRITO.values():
        for loc in lista:
            if loc["globalIdLocal"] == local_id:
                return loc["local"]
    return "Desconhecido"


async def _enviar(update: Update, texto: str, reply_markup=None) -> None:
    """Responde a comandos e callbacks de forma uniforme, em HTML."""
    if update.message:
        await update.message.reply_text(texto, parse_mode="HTML", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            texto, parse_mode="HTML", reply_markup=reply_markup
        )


# ------------------------- PREVISÃO (5 DIAS) ------------------------------


async def comando_lista_distritos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _enviar(update, "Escolhe um distrito:", reply_markup=_teclado_distritos("distrito_"))


async def callback_distrito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("distrito_"):
        return
    local_id_distrito = int(query.data.split("_")[1])

    localidades = LOCAIS_POR_DISTRITO.get(local_id_distrito)
    if not localidades:
        await query.edit_message_text("Nenhuma localidade encontrada para este distrito.")
        return

    await query.edit_message_text(
        "Agora escolhe a localidade:", reply_markup=_teclado_localidades(localidades, "local_")
    )


async def callback_localidade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("local_"):
        return
    local_id = int(query.data.split("_")[1])

    nome_local = _nome_localidade(local_id)
    previsoes = await obter_previsao_multidias_ipma(local_id)

    if not previsoes:
        await query.edit_message_text("⚠️ Erro ao obter a previsão para esta localidade.")
        return

    mensagem = formatar_mensagem_previsao_multidias(previsoes, nome_local)
    await query.edit_message_text(mensagem, parse_mode="HTML")


# ------------------------- TEMPERATURA (HOJE) -----------------------------


async def temperatura(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _enviar(update, "Escolhe um distrito:", reply_markup=_teclado_distritos("temp_dist_"))


async def callback_temperatura_distrito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("temp_dist_"):
        return
    distrito_id = int(query.data.split("_")[-1])

    cidades = LOCAIS_POR_DISTRITO.get(distrito_id, [])
    if not cidades:
        await query.edit_message_text("Não foram encontradas cidades para este distrito.")
        return

    await query.edit_message_text(
        "Escolhe uma cidade:", reply_markup=_teclado_localidades(cidades, "temp_cidade_")
    )


async def callback_temperatura_cidade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("temp_cidade_"):
        return
    cidade_id = int(query.data.split("_")[-1])

    nome_cidade = _nome_localidade(cidade_id)
    previsao = await obter_previsao_ipma(cidade_id)

    if not previsao:
        await query.edit_message_text("⚠️ Erro ao obter a previsão para esta localidade.")
        return

    hoje = next((p for p in previsao if p.get("dataPrev", "").endswith("T00:00:00")), previsao[0])

    mensagem = (
        f"🌤️ Temperaturas para <b>{html.escape(nome_cidade)}</b> (Hoje)\n\n"
        f"🗓️ Data: {html.escape(str(hoje.get('dataPrev', 'Desconhecida')).split('T')[0])}\n"
        f"🌡️ Temperatura Mínima: {hoje.get('tMin', '?')}°C\n"
        f"🌡️ Temperatura Máxima: {hoje.get('tMax', '?')}°C\n"
        f"🔆 Índice UV: {hoje.get('iUv', '?')}\n"
        f"🌦️ Prob. de precipitação: {hoje.get('probabilidadePrecipita', '?')}%\n"
    )
    await query.edit_message_text(text=mensagem, parse_mode="HTML")


# ------------------------- FOGOS ------------------------------------------


def formatar_mensagem_fogos(fogos) -> str:
    if not fogos:
        return "✅ Sem incêndios ativos de momento em Portugal."

    mensagem = f"🔥 <b>Incêndios Ativos em Portugal:</b> <i>{len(fogos)}</i>\n"
    for fogo in fogos[:10]:  # Limitar aos 10 primeiros para evitar mensagens grandes
        local = html.escape(str(fogo.get("location", "Local desconhecido")))
        natureza = html.escape(str(fogo.get("natureza", "Desconhecida")))
        operacionais = html.escape(str(fogo.get("man", "?")))
        terrestres = html.escape(str(fogo.get("terrain", "?")))
        aereos = html.escape(str(fogo.get("aerial", "?")))
        hora = html.escape(str(fogo.get("hour", "?")))
        data = html.escape(str(fogo.get("date", "?")))
        status = html.escape(str(fogo.get("status", "Estado desconhecido")))
        mensagem += (
            "\n───────────────────\n"
            f"\n📍 <b>{local}</b> - <i>{status}</i>\n"
            f"🕓 Início: {data} | {hora}\n"
            f"🔥 Tipo de incêndio: {natureza}\n"
            "\nNeste momento, estão mobilizados:\n"
            f"     👨‍🚒 {operacionais} operacionais\n"
            f"     🚒 {terrestres} veículos\n"
            f"     🚁 {aereos} aéreos\n"
        )
    return mensagem


async def comando_fogos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fogos = await obter_fogos_ativos()
    await _enviar(update, formatar_mensagem_fogos(fogos))


# ------------------------- MENU E AJUDA -----------------------------------


async def menu_principal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📍 Ver previsão temperatura (5 dias)", callback_data="menu_previsao")],
        [InlineKeyboardButton("⚠️ Temperatura (hoje)", callback_data="menu_temperatura")],
        [InlineKeyboardButton("🔥 Incêndios ativos", callback_data="menu_fogos")],
        [InlineKeyboardButton("🌍 Sismos recentes (últimos 10)", callback_data="menu_sismos")],
        [InlineKeyboardButton("📈 Magnitude sísmica", callback_data="menu_magnitude")],
        [InlineKeyboardButton("ℹ️ Ajuda", callback_data="menu_ajuda")],
    ]
    await update.message.reply_text(
        "🧭 Escolhe uma opção abaixo:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def callback_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    MENU_LABELS = {
        "menu_previsao": "📍 Ver previsão (5 dias)",
        "menu_temperatura": "⚠️ Temperatura (hoje)",
        "menu_fogos": "🔥 Incêndios ativos",
        "menu_sismos": "🌍 Sismos recentes",
        "menu_magnitude": "📈 Magnitude sísmica",
        "menu_ajuda": "ℹ️ Ajuda",
    }

    selected = query.data
    label = MENU_LABELS.get(selected, "✅ Opção selecionada")
    await query.edit_message_text(f"✅ Selecionaste: <b>{html.escape(label)}</b>", parse_mode="HTML")

    acoes = {
        "menu_previsao": comando_lista_distritos,
        "menu_temperatura": temperatura,
        "menu_fogos": comando_fogos,
        "menu_sismos": sismos,
        "menu_magnitude": magnitude_sismica,
        "menu_ajuda": ajuda,
    }
    acao = acoes.get(selected)
    if acao:
        await acao(update, context)


async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia mensagem de ajuda com a lista de comandos disponíveis."""
    mensagem = (
        "🤖 <b>Explicação dos comandos disponíveis:</b>\n\n"
        "📍 <b>Ver previsão (5 dias)</b>\n - Mostra a previsão meteorológica para os próximos 5 dias.\n\n"
        "⚠️ <b>Temperatura (hoje)</b>\n – Mostra a previsão do tempo para hoje.\n\n"
        "🔥 <b>Incêndios ativos</b>\n – Lista os incêndios ativos em Portugal.\n\n"
        "🌍 <b>Sismos recentes</b>\n – Mostra os 10 sismos mais recentes registados.\n\n"
        "📈 <b>Magnitude sísmica</b>\n – Explica os diferentes tipos de magnitude "
        "(Richter, Momento, etc) usados para medir sismos.\n\n"
        "ℹ️ <code>/menu</code> – Voltas ao menu inicial."
    )
    await _enviar(update, mensagem)
