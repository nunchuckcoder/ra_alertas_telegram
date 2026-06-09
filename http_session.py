# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Osvaldo Cipriano (github.com/nunchuckcoder)

"""Sessão HTTP partilhada.

Em vez de criar uma `aiohttp.ClientSession` nova a cada pedido (abre e fecha
ligações constantemente), reutilizamos uma única sessão durante a vida do
processo. É criada de forma preguiçosa, já dentro do event loop, e fechada
no shutdown do bot (ver `main.py`).
"""

import aiohttp

_session: aiohttp.ClientSession | None = None

# Timeout total por pedido, para nunca ficar pendurado indefinidamente.
_TIMEOUT = aiohttp.ClientTimeout(total=15)


def get_session() -> aiohttp.ClientSession:
    """Devolve a sessão partilhada, criando-a se necessário."""
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(timeout=_TIMEOUT)
    return _session


async def close_session() -> None:
    """Fecha a sessão partilhada (chamar no shutdown do bot)."""
    global _session
    if _session is not None and not _session.closed:
        await _session.close()
    _session = None
