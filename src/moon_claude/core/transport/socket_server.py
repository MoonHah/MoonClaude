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


    # 临时连接处理器
    async def _handle_connection(
            self,
            _reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter,
    ) -> None:
        writer.close()
        await writer.wait_closed()


    async def start(self) -> str:
        try:
            _reader, writer = await asyncio.open_connection(self._host, self._port)
            writer.close()
            await writer.wait_closed()
            raise SystemExit(f"core already running at {self._host}:{self._port}")
        except (ConnectionRefusedError, OSError):
            pass

        self._server = await asyncio.start_server(
            self._handle_connection,
            host=self._host,
            port=self._port,
            limit=_MAX_LINE_BYTES,
        )
        return f"{self._host}:{self._port}"


    async def stop(self) -> None:
        if self._server is None:
            return

        self._server.close()
        await asyncio.wait_for(self._server.wait_closed(), timeout=2.0)