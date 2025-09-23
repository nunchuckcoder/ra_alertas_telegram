# ================================================================================ #
#                                                                                  #
# Ficheiro:      handlers.py                                                       #
# Autor:         NunchuckCoder                                                     #
# Versão:        1.0                                                               #
# Data:          Julho 2025                                                        #
# Descrição:     Handlers do bot Telegram para comandos de previsão do tempo,      #
#                temperatura, fogos, sismos e menu interativo.                     #
# Licença:       MIT License                                                       #
#                                                                                  #
# ================================================================================ #

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from locais import ID_LOCAL_TO_NAME, LOCAIS_POR_DISTRITO
from ipma_utils import (
    obter_previsao_ipma,
    formatar_mensagem_previsao_multidias
)
from fogos import obter_fogos_ativos
from sismos import sismos, magnitude_sismica

# ================================================================================ #
# -------------------------------- COMANDOS DO BOT ------------------------------- #
# ================================================================================ #

# Comando /previsao - mostra lista de distritos
async def comando_lista_distritos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    row = []
    count = 0

    for local_id, nome in ID_LOCAL_TO_NAME.items():
        row.append(InlineKeyboardButton(nome, callback_data=f"distrito_{local_id}"))
        count += 1
        if count % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("Escolhe um distrito:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Escolhe um distrito:", reply_markup=reply_markup)


# Callback para distrito - mostra lista de localidades desse distrito
async def callback_distrito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("distrito_"):
        return
    local_id_distrito = int(data.split("_")[1])

    localidades = LOCAIS_POR_DISTRITO.get(local_id_distrito)
    if not localidades:
        await query.edit_message_text("Nenhuma localidade encontrada para este distrito.")
        return

    keyboard = []
    row = []
    count = 0
    for local in localidades:
        nome_local = local["local"]
        id_local = local["globalIdLocal"]
        row.append(InlineKeyboardButton(nome_local, callback_data=f"local_{id_local}"))
        count += 1
        if count % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Agora escolhe a localidade:", reply_markup=reply_markup)

# Callback para localidade - mostra previsão 5 dias e remove botões
async def callback_localidade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("local_"):
        return
    local_id = int(data.split("_")[1])

    # Descobre o nome da localidade para mostrar na mensagem
    nome_local = None
    for lista in LOCAIS_POR_DISTRITO.values():
        for loc in lista:
            if loc["globalIdLocal"] == local_id:
                nome_local = loc["local"]
                break
        if nome_local:
            break
    if not nome_local:
        nome_local = "Desconhecido"

    from ipma_utils import obter_previsao_multidias_ipma  # importa a nova função
    previsoes = await obter_previsao_multidias_ipma(local_id)

    if not previsoes:
        await query.edit_message_text("⚠️ Erro ao obter a previsão para esta localidade.")
        return

    mensagem = formatar_mensagem_previsao_multidias(previsoes, nome_local)
    await query.edit_message_text(mensagem, parse_mode="Markdown")


# Comando /temperatura - Mostra a previsão do tempo para hoje pelo local escolhido   
async def temperatura(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = []
    row = []
    count = 0

    for local_id, nome in ID_LOCAL_TO_NAME.items():
        row.append(InlineKeyboardButton(nome, callback_data=f"temp_dist_{local_id}"))
        count += 1
        if count % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("Escolhe um distrito:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Escolhe um distrito:", reply_markup=reply_markup)
    
# Callback distrito para mostrar cidades do distrito
async def callback_temperatura_distrito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data  # Exemplo: "temp_dist_1010500"
    if not data.startswith("temp_dist_"):
        return
    distrito_id = int(data.split("_")[-1])

    cidades_do_distrito = LOCAIS_POR_DISTRITO.get(distrito_id, [])

    if not cidades_do_distrito:
        await query.edit_message_text("Não foram encontradas cidades para este distrito.")
        return

    keyboard = []
    row = []
    count = 0
    for cidade in cidades_do_distrito:
        row.append(InlineKeyboardButton(cidade["local"], callback_data=f"temp_cidade_{cidade['globalIdLocal']}"))
        count += 1
        if count % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Escolhe uma cidade:", reply_markup=reply_markup)


# Callback cidade para mostrar previsão e remover botões
async def callback_temperatura_cidade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data  # Exemplo: "temp_cidade_1010100"
    if not data.startswith("temp_cidade_"):
        return
    cidade_id = int(data.split("_")[-1])

    nome_cidade = "Desconhecido"
    for lista in LOCAIS_POR_DISTRITO.values():
        for loc in lista:
            if loc["globalIdLocal"] == cidade_id:
                nome_cidade = loc["local"]
                break
        if nome_cidade != "Desconhecido":
            break

    previsao = await obter_previsao_ipma(cidade_id)

    if not previsao:
        await query.edit_message_text("⚠️ Erro ao obter a previsão para esta localidade.")
        return

    hoje = next((p for p in previsao if p.get("dataPrev", "").endswith("T00:00:00")), previsao[0])

    mensagem = (
        f"🌤️ Temperaturas para *{nome_cidade}* (Hoje)\n\n"
        f"🗓️ Data: {hoje.get('dataPrev', 'Desconhecida').split('T')[0]}\n"
        f"🌡️ Temperatura Mínima: {hoje.get('tMin', '?')}°C\n"
        f"🌡️ Temperatura Máxima: {hoje.get('tMax', '?')}°C\n"
        f"🔆 Índice UV: {hoje.get('iUv', '?')}\n"
        f"🌦️ Prob. de precipitação: {hoje.get('probabilidadePrecipita', '?')}%\n"
    )

    # Remove os botões da mensagem
    await query.edit_message_text(text=mensagem, parse_mode="Markdown")

def formatar_mensagem_fogos(fogos):
    if not fogos:
        return "✅ Sem incêndios ativos de momento em Portugal."

    mensagem = f"🔥 *Incêndios Ativos em Portugal:* _{len(fogos)}_\n"
    for fogo in fogos[:10]:  # Limitar aos 10 primeiros para evitar mensagens grandes
        local = fogo.get("location", "Local desconhecido")
        concelho = fogo.get("concelho", "Concelho desconhecido")
        distrito = fogo.get("district", "Distrito desconhecido")
        freguesia = fogo.get("freguesia", "Distrito desconhecido")
        natureza = fogo.get("natureza", "Distrito desconhecido")
        operacionais = fogo.get("man", "Operacionais desconhecido")
        terrestres = fogo.get("terrain", "Terrestres desconhecido")
        aereos = fogo.get("aerial", "Aéreos desconhecido")
        hora = fogo.get("hour", "Aéreos desconhecido")
        data = fogo.get("date", "Aéreos desconhecido")
        status = fogo.get("status", "Estado desconhecido")
        mensagem += (
            f"\n───────────────────\n"  # Separador visual
            f"\n📍 *{local}* - _{status}_\n"
            f"🕓 Início: {data} | {hora}\n"
            f"🔥 Tipo de incêndio: {natureza}\n"
            f"\nNeste momento, estão mobilizados:\n"
            f"     👨‍🚒 {operacionais} operacionais\n"
            f"     🚒 {terrestres} veículos\n"
            f"     🚁 {aereos} aéreos\n"
        )
    return mensagem

async def comando_fogos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fogos = await obter_fogos_ativos()
    mensagem = formatar_mensagem_fogos(fogos)
    
    if update.message:
        await update.message.reply_text(mensagem, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.reply_text(mensagem, parse_mode="Markdown")

async def menu_principal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📍 Ver previsão temperatura (5 dias)", callback_data="menu_previsao")],
        [InlineKeyboardButton("⚠️ Temperatura (hoje)", callback_data="menu_temperatura")],
        [InlineKeyboardButton("🔥 Incêndios ativos", callback_data="menu_fogos")],
        [InlineKeyboardButton("🌍 Sismos recentes (últimos 10)", callback_data="menu_sismos")],
        [InlineKeyboardButton("📈 Magnitude sísmica", callback_data="menu_magnitude")],
        [InlineKeyboardButton("ℹ️ Ajuda", callback_data="menu_ajuda")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🧭 Escolhe uma opção abaixo:", reply_markup=reply_markup)       

async def callback_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Dicionário com os nomes visíveis dos botões
    MENU_LABELS = {
        "menu_previsao": "📍 Ver previsão (5 dias)",
        "menu_temperatura": "⚠️ Temperatura (hoje)",
        "menu_fogos": "🔥 Incêndios ativos",
        "menu_sismos": "🌍 Sismos recentes",
        "menu_magnitude": "📈 Magnitude sísmica",
        "menu_ajuda": "ℹ️ Ajuda"
    }

    selected_option = query.data
    label = MENU_LABELS.get(selected_option, "✅ Opção selecionada")

    await query.edit_message_text(f"✅ Selecionaste: *{label}*", parse_mode="Markdown")

    # Chamadas aos comandos conforme a seleção
    if selected_option == "menu_previsao":
        await comando_lista_distritos(update, context)
    elif selected_option == "menu_temperatura":
        await temperatura(update, context)
    elif selected_option == "menu_fogos":
        await comando_fogos(update, context)
    elif selected_option == "menu_sismos":
        await sismos(update, context)
    elif selected_option == "menu_magnitude":
        await magnitude_sismica(update, context)
    elif selected_option == "menu_ajuda":
        await ajuda(update, context)

       
# Comando /ajuda - Mostra lista de comandos disponiveis
async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia mensagem de ajuda com a lista de comandos disponíveis."""
    mensagem = (
        "🤖 *Explicação dos comandos disponíveis:*\n\n"
        "📍 *Ver previsão (5 dias)*\n - Mostra a previsão meteorológica para os próximos 5 dias.\n\n"
        "⚠️ *Temperatura (hoje)*\n – Mostra a previsão do tempo para hoje.\n\n"
        "🔥 *Incêndios ativos*\n – Lista os incêndios ativos em Portugal.\n\n"
        "🌍 *Sismos recentes*\n – Mostra os 10 sismos mais recentes registados.\n\n"
        "📈 *Magnitude sísmica*\n – Explica os diferentes tipos de magnitude (Richter, Momento, etc) usados para medir sismos.\n\n"
        "ℹ️ `/menu` – Voltas ao menu inicial."
    )
    if update.message:
        await update.message.reply_text(mensagem, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.reply_text(mensagem, parse_mode="Markdown")
