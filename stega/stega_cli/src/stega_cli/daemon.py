import asyncio
import contextlib
import functools
import json
import socket
import struct
import typing as T

from stega_cli.domain.command import Command


@contextlib.contextmanager
def acquire_connection(sock_path: str) -> T.Generator[socket.SocketType, None, None]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(sock_path)
        yield s


def send_command(sock: socket.SocketType, cmd: dict[str, T.Any]) -> None: 
    payload = json.dumps(cmd).encode("utf-8")
    header = struct.pack("!I", len(payload))
    sock.sendall(header + payload)


async def read_command(reader) -> T.dict[str, Any]:
    # Get prefix length header - 4 bytes
    header_raw = await reader.readexactly(4) 

    # Find number of payload bytes to read
    header = struct.unpack("!I", header_raw)
    length = header[0]

    # Read payload
    payload = await reader.readexactly(length)

    return json.loads(payload.decode("utf-8"))


async def handle_client(reader, writer, cmd_queue) -> None:
    while True:
        payload = await read_command(reader)
        cmd = Command.from_dict(payload) 
        await cmd_queue.put(cmd) 

    writer.close()
    await writer.wait_closed()


async def handle_command(cmd_queue):
    while True:
        cmd = await cmd_queue.get()
        # TODO: Dispatch command 


async def serve(sock_path: str) -> None:
    # Queue to handle async tasks read from socket
    cmd_queue = asyncio.Queue()

    handle_client_partial = functools.partial(handle_client, cmd_queue=cmd_queue)
    server = await asyncio.start_unix_server(
        handle_client_partial,
        path=sock_path,
    )

    # TODO: Create cmd consumer task

    async with server:
        await server.serve_forever()

