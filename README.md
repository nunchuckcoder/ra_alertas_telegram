<h1 align="center">Rede Alfa - Bot de Alertas Telegram</h1>
<p align="center">
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" />
  <img src="https://img.shields.io/badge/JSON-000?style=for-the-badge&logo=json&logoColor=fff" />
  <img src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" />
  <img src="https://img.shields.io/badge/Notepad++-90E59A.svg?style=for-the-badge&logo=notepad%2b%2b&logoColor=black" />
  <img src="https://img.shields.io/badge/-Raspberry_Pi-C51A4A?style=for-the-badge&logo=Raspberry-Pi" />
</p>
<p align="center">Este projeto é um <b>bot para Telegram</b> desenvolvido em Python que fornece <b>alertas automáticos</b> e comandos interativos com informação relevante para Portugal.</p>

---

## 🚀 Funcionalidades

### 🔔 Alertas Automáticos

- **Sismos Graves** (com magnitude configurável no `.env`)
  - Envio automático de alertas para **um ou mais canais de Telegram**
  - Dados retirados da plataforma [SeismicPortal.eu]
  - Evita duplicação de alertas (mesmo após reinício)
  - Verificação periódica (por defeito, de 10 em 10 minutos, configurável no `.env`) para detetar **novos sismos com magnitude igual ou superior ao valor definido**
  - Garante que **o mesmo sismo não é notificado mais do que uma vez**, guardando os IDs num ficheiro `sismos_notificados.json`.
- **Sismos em Portugal** (independentemente da magnitude)
  - Alerta sempre que é detetado qualquer sismo em Portugal, incluindo regiões autónomas (Açores e Madeira)
  - Dados retirados da plataforma [SeismicPortal.eu]
  - Garante que **o mesmo sismo não é notificado mais do que uma vez**, guardando os IDs num ficheiro `sismos_portugal_notificados.json`
  - Verificação periódica (por defeito, de 10 em 10 minutos, configurável no `.env`)
  - Permite enviar para múltiplos canais (definidos em ALERTA_SISMOS_CHANNEL_IDS, configurável no `.env`)

### 🌤️ Previsão Meteorológica

- `/previsao`: previsão **dos próximos 5 dias** para qualquer localidade
- `/temperatura`: previsão **do dia atual**, incluindo:
  - Temperatura mínima e máxima
  - Índice UV
  - Probabilidade de precipitação
- Dados fornecidos pela **IPMA** (Instituto Português do Mar e da Atmosfera)

### 🔥 Fogos Ativos

- `/fogos`: lista dos incêndios ativos em Portugal
- Inclui local, estado, data, hora e meios mobilizados (operacionais, veículos, aéreos)

### 📈 Informação Sísmica

- `/sismos`: lista os últimos **10 sismos** mais recentes, incluindo:
  - Localização
  - Data e hora
  - Magnitude
  - Profundidade
  - Link direto para Google Maps
- `/magnitude_sismica`: explicação os diferentes tipos de magnitude (Richter, Momento, etc) usados para medir sismos

### 📋 Menu Interativo

- `/menu`: abre um **menu interativo** com botões para acesso rápido a todas as funcionalidades

### ℹ️ Outros

- `/ajuda`: mostra uma **lista de todos os comandos disponíveis** e instruções de uso

---

## 🛠️ Instalação

1. **Clona o repositório** ou extrai o `.zip`

   ```bash
   git clone https://github.com/seu-username/RA_alertas_telegram.git
   cd RA_alertas_telegram
   ```

2. Cria um ambiente virtual (opcional mas recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   .\venv\Scripts\activate    # Windows
   ```

3. **Instala as dependências**:

   ```bash
   pip install -r requirements.txt
   ```

4. Cria um ficheiro `.env` com as seguintes variáveis:

   ```env
   # TELEGRAM
   BOT_TOKEN=TOKEN_DO_TEU_BOT

   # CONFIGURAÇÕES DOS SISMOS
   SEISMIC_LIMIT=10
   SEISMIC_START=2025-01-01
   #SEISMIC_END=2025-12-31  # comenta para não usares data final
   SEISMIC_FORMAT=json
   SEISMIC_MINMAG=2

   # ALERTA DOS SISMOS
   ALERTA_SISMOS_CHANNEL_IDS=-1000000000000,-4444444444,5555555555 # separados por vírgula
   MIN_MAGNITUDE_ALERTA=6
   INTERVALO_VERIFICACAO=600  # em segundos (exemplo: 1800 = 30 minutos)

   # ENDPOINTS DAS APIS
   IPMA_API=URL
   FOGOS_API=URL
   SISMOS_API=URL
   ```

- BOT_TOKEN: Token do teu bot.
- SEISMIC_LIMIT, SEISMIC_START, SEISMIC_START, SEISMIC_FORMAT, SEISMIC_MINMAG: Parâmetros da pesquisa da API de sismos.
- ALERTA_SISMOS_CHANNEL_IDS: Lista de IDs de canais ou grupos onde os alertas serão enviados.
- MIN_MAGNITUDE_ALERTA: Magnitude mínima para envio de alerta.
- INTERVALO_VERIFICACAO: Intervalo entre verificações (em segundos).
- IPMA_API: Endpoint da API pública do IPMA para previsão meteorológica.
- FOGOS_API: Endpoint da API dos fogos.
- SISMOS_API: Endpoint da API de sismos.

---

## ▶️ Execução

Para iniciar o bot:

   ```bash
   python3 main.py
   ```

> ✅ O ficheiro `main.py` inicia automaticamente o sistema de **alertas sísmicos**, sem necessidade de executar manualmente o `sismos_alerta.py`.

---

## 📁 Estrutura do Projeto

```
📂 bot/
   ├── handlers.py             # Comandos e callbacks do bot
   ├── ipma_utils.py           # Funções IPMA (tempo, temperaturas)
   ├── locais.py               # Mapeamento de localidades
   ├── fogos.py                # Recolha de incêndios ativos
   ├── sismos_alerta.py        # Função de verificação e envio de alertas sísmicos
   ├── sismos.py               # Recolha de sismos ativos
   ├── sismos_registados.json  # Guarda sismos já anunciados
   ├── main.py                 # Ponto de entrada do bot
   ├── .env                    # Configuração do ambiente
   ├── config.py               # Leitura e validação das variáveis de ambiente
   └── requirements.txt        # Dependências do projeto
```

---

## 📜 Exemplo de saída dos comandos

### 📍 Ver previsão temperatura (5 dias)

   ```bash
   📍 Praia de Armação de Pera - Previsão para os próximos 5 dias:

   📅 2025-08-02
   🌡️ 19.7°C ~ 31.8°C
   🔆 Índice UV: 8.7
   🌦️ Prob. de precipitação: 0.0%
   ```
   
### ️⚠️ Temperatura (hoje)

   ```bash
   🌤️ Temperaturas para Praia de Armação de Pera (Hoje)

   🗓️ Data: 2025-08-02
   🌡️ Temperatura Mínima: 19.7°C
   🌡️ Temperatura Máxima: 31.8°C
   🔆 Índice UV: 8.7
   🌦️ Prob. de precipitação: 0.0%
   ```

### 🔥 Incêndios ativos

   ```bash
   🔥 Incêndios Ativos em Portugal: 6
   
   ───────────────────
   
   📍 Viana Do Castelo, Ponte da Barca, Lindoso - Em Curso
   🕓 Início: 26-07-2025 | 21:47
   🔥 Tipo de incêndio: Mato
   
   Neste momento, estão mobilizados:
     👨‍🚒 599 operacionais
     🚒 193 veículos
     🚁 5 aéreos

   ───────────────────
   ```
   
### 🌍 Sismos recentes

   ```bash
   🌍 Últimos Sismos:

   📍 GUATEMALA
   🕒 2025-08-02 15:54:03
   💥️ Magnitude: 🟢 m 2.8
   📏 Profundidade: 6.0 Km
   🗺️ Ver no mapa
   ```
   
### 🔔 Alertas Automáticos de sismos

   ```bash
   🚨 Sismo de Grande Magnitude Detetado!

   📍 OFF EAST COAST OF KAMCHATKA
   🕒 Hora: 2025-08-02 14:14 UTC
   💥 Magnitude: mw 6.0
   📏 Profundidade: 20.5 Km
   🗺️ Ver no mapa
   ```

---

## 🔧 Requisitos

- Python 3.10 ou superior
- Conta Telegram + Bot API
  - Procura no Telegram por `@BotFather` e segue as instruções para criar um bot
  - Guarda o **Token** fornecido pelo BotFather
- Links de API do IPMA, Fogos.pt e SeismicPortal.eu
- Bibliotecas:
  - python-telegram-bot[job-queue]
  - aiohttp
  - python-dotenv

---

## 🧪 Testado em

- Python 3.11
- Ubuntu 22.04 & Windows 10
- Telegram bot em **grupos e canais**

---

## 📌️ Notas Finais

- O bot está preparado para ser executado como **serviço systemd**.
- Os dados são recolhidos de fontes oficiais (IPMA, Prociv e SeismicPortal).

---

## 📬 Contribuição

- Contribuições são bem-vindas! Se encontrares bugs ou tiveres sugestões, abre um issue ou faz um pull request.

---

## 📬 Contato

- Desenvolvido por **Mikey**
- **Email:** code.wish815@passmail.com
- **GitHub:** [https://github.com/NunchuckCoder](https://github.com/NunchuckCoder)
- **Discord:** Rede Alfa - [https://discord.gg/kBHcmUbZAP](https://discord.gg/kBHcmUbZAP)

---

## 🛡️ Licença

- Este projeto é open-source sob a licença MIT.

---

Feito com 💚 para a Rede Alfa
