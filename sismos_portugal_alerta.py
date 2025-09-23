# ================================================================================ #
#                                                                                  #
# Ficheiro:      sismos_portugal_alerta.py                                         #
# Autor:         NunchuckCoder                                                     #
# Versão:        1.0                                                               #
# Data:          Julho 2025                                                        #
# Descrição:     Monitora periodicamente sismos em Portugal, Açores e Madeira e    #
#                envia alertas de magnitude significativa para canais do Telegram. #
# Licença:       MIT License                                                       #
#                                                                                  #
# ================================================================================ #

import os
import aiohttp
import json
from datetime import datetime
from telegram.ext import ContextTypes
from dotenv import load_dotenv

# ================================================================================ #
# ------------------------ CARREGAR VARIÁVEIS DE AMBIENTE ------------------------ #
# ================================================================================ #

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_IDS_RAW = os.getenv("ALERTA_SISMOS_CHANNEL_IDS", "")
CHANNEL_IDS = [canal.strip() for canal in CHANNEL_IDS_RAW.split(",") if canal.strip()]
SISMOS_API = os.getenv("SISMOS_API")
ARQUIVO_SISMOS_PT = "sismos_portugal_notificados.json"

# ================================================================================ #
# ----------------------- FUNÇÕES PARA ARMAZENAR/VERIFICAR ----------------------- #
# ================================================================================ #

def carregar_sismos_notificados():
    try:
        with open(ARQUIVO_SISMOS_PT, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def guardar_sismos_notificados(sismos_set):
    with open(ARQUIVO_SISMOS_PT, "w", encoding="utf-8") as f:
        json.dump(list(sismos_set), f, ensure_ascii=False, indent=2)

# ================================================================================ #
# -------------------------- FUNÇÃO PRINCIPAL DE ALERTA -------------------------- #
# ================================================================================ #

async def verificar_sismos_portugal(context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    sismos_notificados = carregar_sismos_notificados()

    try:
        params = {
            "format": "json",
            "limit": "30",  # obtém mais eventos para melhor cobertura
            "orderby": "time",
            "end": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(SISMOS_API, params=params) as resposta:
                if resposta.status != 200:
                    print(f"[Erro] Código de resposta HTTP: {resposta.status}")
                    return

                dados = await resposta.json()

                for sismo in dados.get("features", []):
                    props = sismo.get("properties", {})
                    geo = sismo.get("geometry", {})
                    sismo_id = props.get("unid")
                    lugar = props.get("flynn_region", "").lower()
                    
                    # Verifica se é em Portugal, Açores ou Madeira
                    if not lugar or all(pt not in lugar for pt in ["portugal", "azores", "madeira"]):
                        continue  # ignora sismos fora de Portugal

                    if not sismo_id or sismo_id in sismos_notificados:
                        continue

                    mag = props.get("mag", 0)
                    magtype = props.get("magtype", "?")
                    profundidade = props.get("depth", "?")
                    datahora = props.get("time", "")[:16].replace("T", " ")
                    latitude = geo.get("coordinates", [None, None])[1]
                    longitude = geo.get("coordinates", [None, None])[0]

                    if latitude and longitude:
                        link_mapa = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
                        mapa_texto = f"🗺️ [Ver no mapa]({link_mapa})"
                    else:
                        mapa_texto = "🗺️ Localização desconhecida"

                    mensagem = (
                        f"📢 *Sismo Detetado em Portugal!*\n\n"
                        f"📍 *{lugar.title()}*\n"
                        f"🕒 Hora: {datahora} UTC\n"
                        f"💥 Magnitude: {magtype} *{mag}*\n"
                        f"📏 Profundidade: {profundidade} Km\n"
                        f"{mapa_texto}\n"
                    )

                    for canal_id in CHANNEL_IDS:
                        try:
                            await bot.send_message(
                                chat_id=int(canal_id),
                                text=mensagem,
                                parse_mode="Markdown",
                                disable_web_page_preview=True
                            )
                        except Exception as e:
                            print(f"[Erro ao enviar para canal {canal_id}]: {e}")

                    sismos_notificados.add(sismo_id)

                guardar_sismos_notificados(sismos_notificados)

    except Exception as erro:
        print(f"[Erro ao verificar sismos de Portugal]: {erro}")
