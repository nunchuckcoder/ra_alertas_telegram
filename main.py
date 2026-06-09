# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Osvaldo Cipriano (github.com/nunchuckcoder)

import logging

from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from config import BOT_TOKEN, INTERVALO_VERIFICACAO
from handlers import (
    ajuda,
    callback_distrito,
    callback_localidade,
    callback_menu,
    callback_temperatura_cidade,
    callback_temperatura_distrito,
    comando_fogos,
    comando_lista_distritos,
    menu_principal,
    temperatura,
)
from http_session import close_session
from sismos import magnitude_sismica, sismos
from sismos_alerta import verificar_sismos_graves
from sismos_portugal_alerta import verificar_sismos_portugal

# ------------------------- CONFIGURAÇÃO DE LOGS ---------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ------------------------- SHUTDOWN ---------------------------------------


async def _post_shutdown(app) -> None:
    """Fecha a sessão HTTP partilhada quando o bot encerra."""
    await close_session()


# ------------------------- FUNÇÃO PRINCIPAL -------------------------------


def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).post_shutdown(_post_shutdown).build()

    # Registar handlers
    app.add_handler(CommandHandler("previsao", comando_lista_distritos))
    app.add_handler(CallbackQueryHandler(callback_distrito, pattern="^distrito_"))
    app.add_handler(CallbackQueryHandler(callback_localidade, pattern="^local_"))
    app.add_handler(CommandHandler("temperatura", temperatura))
    app.add_handler(CallbackQueryHandler(callback_temperatura_distrito, pattern=r"^temp_dist_\d+$"))
    app.add_handler(CallbackQueryHandler(callback_temperatura_cidade, pattern=r"^temp_cidade_\d+$"))
    app.add_handler(CommandHandler("fogos", comando_fogos))
    app.add_handler(CommandHandler("sismos", sismos))
    app.add_handler(CommandHandler("magnitude_sismica", magnitude_sismica))
    app.add_handler(CommandHandler("menu", menu_principal))
    app.add_handler(CallbackQueryHandler(callback_menu, pattern="^menu_"))
    app.add_handler(CommandHandler("ajuda", ajuda))

    # Jobs periódicos de verificação de sismos
    app.job_queue.run_repeating(verificar_sismos_graves, interval=INTERVALO_VERIFICACAO, first=10)
    app.job_queue.run_repeating(verificar_sismos_portugal, interval=INTERVALO_VERIFICACAO, first=10)

    logger.info("Bot iniciado. Intervalo de verificação: %ss", INTERVALO_VERIFICACAO)
    app.run_polling()


# ------------------------- EXECUÇÃO DO BOT --------------------------------

if __name__ == "__main__":
    main()
