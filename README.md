<h1 align="center">Rede Alfa - Bot de Alertas Telegram</h1>
<p align="center">
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" />
  <img src="https://img.shields.io/badge/JSON-000?style=for-the-badge&logo=json&logoColor=fff" />
  <img src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" />
  <img src="https://img.shields.io/badge/status-active-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" />
</p>
<p align="center">Bot para <b>Telegram</b> desenvolvido em Python que fornece <b>alertas automáticos</b> e comandos interativos com informação relevante para Portugal: sismos, meteorologia (IPMA) e incêndios ativos.</p>

---

## 🚀 Funcionalidades

### 🔔 Alertas Automáticos

- **Sismos graves** (magnitude configurável no `.env`)
  - Envio automático para **um ou mais canais/grupos de Telegram**
  - Dados da plataforma [SeismicPortal.eu](https://www.seismicportal.eu)
  - Verificação periódica (por defeito de 10 em 10 minutos, configurável) de **novos sismos com magnitude igual ou superior ao valor definido**
  - Garante que **o mesmo sismo não é notificado duas vezes**, guardando os IDs em `sismos_notificados.json` (persiste após reinício)
- **Sismos em Portugal** (qualquer magnitude)
  - Alerta sempre que é detetado um sismo em Portugal, incluindo Açores e Madeira
  - Deduplicação própria via `sismos_portugal_notificados.json`

### 🌤️ Previsão Meteorológica (IPMA)

- `/previsao` — previsão **dos próximos 5 dias** para qualquer localidade
- `/temperatura` — previsão **do dia atual**: temperatura mínima/máxima, índice UV e probabilidade de precipitação
  - Temperatura mínima e máxima
  - Índice UV
  - Probabilidade de precipitação

### 🔥 Fogos Ativos

- `/fogos` — lista dos incêndios ativos em Portugal (local, estado, data/hora e meios mobilizados)
  - Inclui local, estado, data, hora e meios mobilizados (operacionais, veículos, aéreos)

### 📈 Informação Sísmica

- `/sismos` — últimos **10 sismos** (localização, data/hora, magnitude, profundidade e link para o Google Maps)
  - Localização
  - Data e hora
  - Magnitude
  - Profundidade
  - Link direto para Google Maps
- `/magnitude_sismica` — explicação dos tipos de magnitude (Richter, Momento, etc.)

### 📋 Menu e Ajuda

- `/menu` — menu interativo com botões para todas as funcionalidades
- `/ajuda` — lista de comandos disponíveis

---

## 🛠️ Instalação

1. **Clona o repositório**

   ```bash
   git clone https://github.com/nunchuckcoder/ra_alertas_telegram.git
   cd ra_alertas_telegram
   ```

2. **Cria um ambiente virtual** (recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/macOS
   .\venv\Scripts\activate       # Windows
   ```

3. **Instala as dependências**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configura o `.env`** a partir do exemplo:

   ```bash
   cp .env.example .env
   ```

   Edita o `.env` e preenche pelo menos o `BOT_TOKEN` e o `ALERTA_SISMOS_CHANNEL_IDS`. As restantes variáveis já vêm com valores por defeito:

   | Variável | Descrição |
   |---|---|
   | `BOT_TOKEN` | Token do bot, obtido no `@BotFather` |
   | `SEISMIC_LIMIT`, `SEISMIC_START`, `SEISMIC_END`, `SEISMIC_FORMAT`, `SEISMIC_MINMAG` | Parâmetros da pesquisa do comando `/sismos` |
   | `ALERTA_SISMOS_CHANNEL_IDS` | IDs de canais/grupos para os alertas, separados por vírgula |
   | `MIN_MAGNITUDE_ALERTA` | Magnitude mínima para o alerta de sismos graves |
   | `INTERVALO_VERIFICACAO` | Intervalo entre verificações, em segundos |
   | `IPMA_API`, `FOGOS_API`, `SISMOS_API` | Endpoints das APIs (públicas, sem chave) |

---

## ▶️ Execução

```bash
python3 main.py
```

> ✅ O `main.py` arranca também os **alertas sísmicos** automaticamente — não é preciso correr os `sismos_*_alerta.py` à mão.
>
> Os ficheiros `sismos_notificados.json` e `sismos_portugal_notificados.json` são criados automaticamente na primeira execução (e estão no `.gitignore`).

---

## 📁 Estrutura do Projeto

```
ra_alertas_telegram/
├── main.py                          # Ponto de entrada do bot
├── config.py                        # Leitura e validação do .env (fonte única)
├── http_session.py                  # Sessão HTTP partilhada (aiohttp)
├── handlers.py                      # Comandos e callbacks do bot
├── ipma_utils.py                    # Funções IPMA (tempo, temperaturas)
├── fogos.py                         # Recolha de incêndios ativos
├── sismos.py                        # Comando /sismos e /magnitude_sismica
├── alertas_core.py                  # Lógica partilhada dos alertas (fetch/dedup/envio)
├── sismos_alerta.py                 # Alerta de sismos de grande magnitude
├── sismos_portugal_alerta.py        # Alerta de qualquer sismo em Portugal
├── locais.py                        # Mapeamento de distritos e localidades
├── requirements.txt                 # Dependências
├── .env.example                     # Exemplo de configuração
└── README.md
```

---

## 📜 Exemplos de saída

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

```
🔥 Incêndios Ativos em Portugal: 6

───────────────────

📍 Viana do Castelo, Ponte da Barca, Lindoso - Em Curso
🕓 Início: 26-07-2025 | 21:47
🔥 Tipo de incêndio: Mato

Neste momento, estão mobilizados:
     👨‍🚒 599 operacionais
     🚒 193 veículos
     🚁 5 aéreos
```

### 🌍 Sismos recentes

```
🌍 Últimos Sismos:

📍 GUATEMALA
🕒 2025-08-02 15:54:03
💥️ Magnitude: 🟢 m 2.8
📏 Profundidade: 6.0 Km
🗺️ Ver no mapa
```

### 🔔 Alerta automático

```
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
- Conta Telegram + bot criado no `@BotFather` (guarda o **token**)
- Bibliotecas (ver `requirements.txt`):
  - `python-telegram-bot[job-queue]`
  - `aiohttp`
  - `python-dotenv`

As APIs do **IPMA**, **Fogos.pt** e **SeismicPortal.eu** são públicas e **não requerem chave de API**.

---

## 🧪 Testado em

- Python 3.11 / 3.13
- Ubuntu 22.04 e Windows 10
- Bot em **grupos e canais** de Telegram

---

## 📌 Notas

- Preparado para correr como **serviço systemd** (os ficheiros de estado são gravados na pasta do projeto, independentemente do *working directory*).
- Dados recolhidos de fontes oficiais: IPMA, Fogos.pt (ANEPC) e SeismicPortal.eu.

---

## 🤝 Contribuição

Contribuições são bem-vindas — abre um *issue* ou um *pull request*.

---

## 📜 Licença

Distribuído sob a licença **MIT**. Ver [`LICENSE`](LICENSE).

