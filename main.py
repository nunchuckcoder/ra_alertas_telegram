# ================================================================================ #
#                                                                                  #
# Ficheiro:      main.py                                                           #
# Autor:         NunchuckCoder                                                     #
# Versão:        1.0                                                               #
# Data:          Julho 2025                                                        #
# Descrição:     Bot para Telegram que envia alertas meteorológicos, de incêndios  #
#                e sismos. Inclui comandos para previsão, temperatura, fogos,      #
#                sismos e menu interativo.                                         #
# Licença:       MIT License                                                       #
#                                                                                  #
# ================================================================================ #
#                                                                                  #
# Funcionalidades principais:                                                      #
#   1. /previsao          - Lista de distritos e previsão do tempo                 #
#   2. /temperatura       - Temperatura por distrito ou cidade                     #
#   3. /fogos             - Alertas de incêndios                                   #
#   4. /sismos            - Consulta de sismos recentes                            #
#   5. /magnitude_sismica - Consulta por magnitude de sismos                       #
#   6. /menu              - Menu interativo                                        #
#   7. /ajuda             - Informação de ajuda sobre comandos                     #
#                                                                                  #
# Jobs periódicos:                                                                 #
#   - Verificação automática de sismos graves                                      #
#   - Verificação automática de sismos em Portugal                                 #
#                                                                                  #
# ================================================================================ #

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN
from sismos import sismos, magnitude_sismica
from sismos_alerta import verificar_sismos_graves
from sismos_portugal_alerta import verificar_sismos_portugal
from handlers import (
    comando_lista_distritos,
    callback_distrito,
    callback_localidade,
    temperatura,
    callback_temperatura_distrito,
    callback_temperatura_cidade,
    comando_fogos,
    menu_principal,
    callback_menu,
    ajuda,
)
import os

# ================================================================================ #
# ------------------------------- FUNÇÃO PRINCIPAL ------------------------------- #
# ================================================================================ #

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

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

    # Intervalo de verificação (segundos)
    intervalo = int(os.getenv("INTERVALO_VERIFICACAO", 600))  # 10 min por defeito

    # Adicionar job periódico para verificar sismos
    app.job_queue.run_repeating(verificar_sismos_graves, interval=intervalo, first=10)
    app.job_queue.run_repeating(verificar_sismos_portugal, interval=intervalo, first=10)

    # Iniciar o bot
    app.run_polling()

# ================================================================================ #
# -------------------------------- EXECUÇÃO DO BOT ------------------------------- #
# ================================================================================ #

if __name__ == "__main__":
    main()
