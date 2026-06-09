# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Osvaldo Cipriano (github.com/nunchuckcoder)

import html
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from config import IPMA_API
from http_session import get_session

# ------------------------- CONFIGURAÇÃO DE LOGS ---------------------------

logger = logging.getLogger(__name__)

# Fuso horário de Portugal continental (trata automaticamente do
# horário de verão/inverno, ao contrário de um offset fixo +1).
TZ_LISBOA = ZoneInfo("Europe/Lisbon")

# ------------------------- CONFIGURAÇÕES DE FUNÇÕES -----------------------


async def obter_previsao_ipma(local_id: int):
    """
    Obtém a previsão meteorológica para o dia atual de um local específico,
    garantindo que inclui temperatura mínima, máxima, índice UV e precipitação.
    """
    url = f"{IPMA_API}{local_id}.json"

    try:
        session = get_session()
        async with session.get(url) as response:
            if response.status != 200:
                logger.error("Erro HTTP %s ao obter previsão para local %s", response.status, local_id)
                return None
            data = await response.json()

            # Data de hoje em Portugal continental
            hoje = datetime.now(TZ_LISBOA).date().isoformat()

            # Filtrar registos do dia de hoje
            previsoes_hoje = [p for p in data if p.get("dataPrev", "").startswith(hoje)]
            if not previsoes_hoje:
                logger.warning("Sem previsões para hoje (%s) para o local %s", hoje, local_id)
                return None

            # Selecionar os melhores registos disponíveis
            tmin_reg = next((p for p in previsoes_hoje if p.get("tMin") is not None), None)
            tmax_reg = next((p for p in previsoes_hoje if p.get("tMax") is not None), None)
            iuv_reg = next((p for p in previsoes_hoje if p.get("iUv") is not None), None)
            prec_reg = next((p for p in previsoes_hoje if p.get("probabilidadePrecipita") is not None), None)

            resultado = {
                "dataPrev": hoje + "T00:00:00",
                "tMin": tmin_reg.get("tMin") if tmin_reg else None,
                "tMax": tmax_reg.get("tMax") if tmax_reg else None,
                "iUv": iuv_reg.get("iUv") if iuv_reg else None,
                "probabilidadePrecipita": prec_reg.get("probabilidadePrecipita") if prec_reg else None,
            }

            return [resultado]  # mantém compatibilidade com a lógica do handler

    except Exception:
        logger.exception("Erro ao obter previsão para local %s", local_id)
        return None


async def obter_previsao_multidias_ipma(local_id: int):
    """Obtém a previsão meteorológica completa (vários dias) de um local."""
    url = f"{IPMA_API}{local_id}.json"

    try:
        session = get_session()
        async with session.get(url) as response:
            if response.status != 200:
                logger.error("Erro HTTP %s ao obter previsão para local %s", response.status, local_id)
                return None
            return await response.json()
    except Exception:
        logger.exception("Erro ao obter previsão multi-dias para local %s", local_id)
        return None


def formatar_mensagem_previsao_multidias(previsoes: list, nome_local: str) -> str:
    """Formata a previsão de 5 dias em HTML (campos dinâmicos escapados)."""
    mensagem = f"📍 <b>{html.escape(nome_local)}</b> - Previsão para os próximos 5 dias:\n"
    dias_adicionados = set()

    # Agrupar previsões por dia
    previsoes_por_dia = {}
    for prev in previsoes:
        data_prev = prev.get("dataPrev", "").split("T")[0]
        previsoes_por_dia.setdefault(data_prev, []).append(prev)

    for data_prev in sorted(previsoes_por_dia.keys()):
        if data_prev in dias_adicionados:
            continue

        grupo = previsoes_por_dia[data_prev]
        registo_00h = next((p for p in grupo if p.get("dataPrev", "").endswith("T00:00:00")), None)
        registo_com_temp = next(
            (p for p in grupo if p.get("tMin") is not None and p.get("tMax") is not None), None
        )
        registo_com_uv = next((p for p in grupo if p.get("iUv") is not None), None)

        tmin = registo_com_temp.get("tMin") if registo_com_temp else None
        tmax = registo_com_temp.get("tMax") if registo_com_temp else None
        meteo = registo_00h.get("probabilidadePrecipita") if registo_00h else None
        uv = registo_com_uv.get("iUv") if registo_com_uv else None

        tmin_str = f"{tmin}°C" if tmin is not None else "?"
        tmax_str = f"{tmax}°C" if tmax is not None else "?"
        meteo_str = f"{meteo}" if meteo is not None else "?"
        iuv_str = f"{uv}" if uv is not None else "Indisponível"

        mensagem += (
            f"\n📅 {data_prev}\n"
            f"🌡️ {tmin_str} ~ {tmax_str}\n"
            f"🔆 Índice UV: {iuv_str}\n"
            f"🌦️ Prob. de precipitação: {meteo_str}%\n"
        )

        dias_adicionados.add(data_prev)
        if len(dias_adicionados) == 5:
            break

    return mensagem
