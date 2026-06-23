import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

# 异步 handler 类型
type CommandHandler = Callable[[dict[str, Any]], Awaitable[Any]]

_MAX_LINE_BYTES = 1 * 1024 * 1024


class SocketServer:
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._handlers: dict[str, CommandHandler] = {}
        self._server: asyncio.AbstractServer | None = None

    def register(self, method: str, handler: CommandHandler) -> None:
        self._handlers[method] = handler