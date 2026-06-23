import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel

from moon_claude.core.bus.envelope import INVALID_REQUEST, PARSE_ERROR, make_error

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

    # 处理单个客户端连接，并在读取结束后关闭写流
    async def _handle_connection(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        try:
            await self._read_loop(reader, writer)
        finally:
            writer.close()
            try:
                await asyncio.wait_for(writer.wait_closed(), timeout=1.0)
            except TimeoutError:
                pass

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

    async def _send(
        self,
        writer: asyncio.StreamWriter,
        message: BaseModel,
    ) -> None:
        writer.write(message.model_dump_json().encode() + b"\n")
        await writer.drain()

    async def _handle_line(
        self,
        line: bytes,
        writer: asyncio.StreamWriter,
    ) -> None:
        try:
            json.loads(line)
        except json.JSONDecodeError as error:
            response = make_error(
                None,
                PARSE_ERROR,
                f"Parse error: {error}",
            )
            await self._send(writer, response)
            return

    async def _read_loop(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        while True:
            try:
                line = await reader.readline()
            except asyncio.LimitOverrunError:
                response = make_error(
                    None,
                    INVALID_REQUEST,
                    "Request too large",
                )
                await self._send(writer, response)
                return

            if not line:
                return

            await self._handle_line(line, writer)
