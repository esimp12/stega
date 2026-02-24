import asyncio
import contextlib
import functools
import json
import socket
import struct
import typing as T

from stega_cli.domain.command import (
    Command,
    ReadCommand,
    WriteCommand,
    Response,
)
from stega_cli.services.dispatcher import bootstrap_dispatcher, Dispatcher


@contextlib.contextmanager
def acquire_connection(sock_path: str) -> T.Generator[socket.SocketType, None, None]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(sock_path)
        yield s


def read_bytes(sock: socket.SocketType, num_bytes: int) -> bytes:
    buf = b""
    while len(buf) < num_bytes:
        chunk = sock.recv(num_bytes - len(buf))
        if not chunk:
            raise ConnectionError("socket closed")
        buf += chunk
    return buf


def send_command(
    sock: socket.SocketType,
    cmd: dict[str, T.Any],
) -> None: 
    payload = json.dumps(cmd).encode("utf-8")
    header = struct.pack("!I", len(payload))
    data = header + payload
    sock.sendall(data)


def read_command(sock: socket.SocketType) -> T.dict[str, T.Any]:
    # Get prefix length header - 4 bytes
    header_raw = read_bytes(sock, 4)

    # Find number of payload bytes to read
    header = struct.unpack("!I", header_raw)
    length = header[0]

    # Read payload
    payload = read_bytes(sock, length)

    return json.loads(payload.decode("utf-8"))


async def send_command_async(
    writer: asyncio.StreamWriter,
    cmd: dict[str, T.Any],
) -> None:
    # Create payload with header
    payload = json.dumps(cmd).encode("utf-8")
    header = struct.pack("!I", len(payload))
    data = header + payload

    # Write payload to stream
    writer.write(data)
    await writer.drain()


async def read_command_async(reader: asyncio.StreamReader) -> T.dict[str, Any]:
    # Get prefix length header - 4 bytes
    header_raw = await reader.readexactly(4) 

    # Find number of payload bytes to read
    header = struct.unpack("!I", header_raw)
    length = header[0]

    # Read payload
    payload = await reader.readexactly(length)

    return json.loads(payload.decode("utf-8"))


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    cmd_queue: asyncio.Queue,
    dispatcher: Dispatcher,
) -> None:
    while True:
        payload = await read_command_async(reader)
        cmd = Command.from_dict(payload) 

        # ReadCommand, synchronously generate resposne
        if isinstance(cmd, ReadCommand):
            response = dispatcher.handle(cmd)

        # WriteCommand, asynchronously hand off work to command queue, immediately return correlation id
        elif isinstance(cmd, WriteCommand):
            response = Response(
                status="ok",
                result={"correlation_id": cmd.correlation_id},
            )
            await cmd_queue.put(cmd)
        
        # Send response back to socket caller
        await send_command_async(writer, response.to_dict())

    writer.close()
    await writer.wait_closed()


async def handle_command(
    cmd_queue: asyncio.Queue,
    dispatcher: Dispatcher,
) -> None:
    while True:
        cmd = await cmd_queue.get()
        dispatcher.handle(cmd)


async def serve(sock_path: str) -> None:
    # Queue to handle async tasks read from socket
    cmd_queue = asyncio.Queue()

    # Dispatcher to send commands to appropriate handlers
    dispatcher = bootstrap_dispatcher()

    # Create socket handler
    handle_client_partial = functools.partial(
        handle_client,
        cmd_queue=cmd_queue,
        dispatcher=dispatcher,
    )
    server = await asyncio.start_unix_server(
        handle_client_partial,
        path=sock_path,
    )

    # Create cmd consumer task
    asyncio.create_task(handle_command(cmd_queue, dispatcher))

    async with server:
        await server.serve_forever()

