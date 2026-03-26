import asyncio
import contextlib
import functools
import json
import socket
import struct
from collections.abc import Iterator
from typing import Any

from stega_cli.domain.request import CommandRequest
from stega_cli.ports import db
from stega_cli.services.command import CommandDispatcher, bootstrap_cmd_dispatcher
from stega_cli.services.request import RequestDispatcher


@contextlib.contextmanager
def acquire_connection(sock_path: str) -> Iterator[socket.SocketType]:
    """Open a socket connection on the given socket path.

    Args:
        sock_path: A str of the path to the socket.

    Yields:
        A socket.SocketType instance connected to the socket.

    """
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(sock_path)
        yield s


def read_bytes(sock: socket.SocketType, num_bytes: int) -> bytes:
    """Read a fixed number of bytes from a socket.

    Args:
        sock: A socket.SocketType instance of the socket connection.
        num_bytes: An int of the number of bytes to read.

    Returns:
        The bytes read from the socket.

    """
    buf = b""
    while len(buf) < num_bytes:
        chunk = sock.recv(num_bytes - len(buf))
        if not chunk:
            err_msg = "socket closed"
            raise ConnectionError(err_msg)
        buf += chunk
    return buf


def send_command(sock: socket.SocketType, cmd_dict: dict[str, Any]) -> None:
    """Send a serialized command to a socket.

    Args:
        sock: A socket.SocketType instance of the socket connection.
        cmd_dict: A dict of the serializable representation of a Command.

    """
    payload = json.dumps(cmd_dict).encode("utf-8")
    header = struct.pack("!I", len(payload))
    data = header + payload
    sock.sendall(data)


def read_command(sock: socket.SocketType) -> dict[str, Any]:
    """Read a command from a socket.

    NOTE: Each command has a fixed 4 bytes prefix header specifying the length
    of the actual command payload. This header is read first and the ensuing
    'length' bytes are read and loaded into a serializable representation of the
    command.

    Args:
        sock: A socket.SocketType instance of the socket connection.

    Returns:
        A dict of the serializable representation of a Command.

    """
    # Get prefix length header - 4 bytes
    header_raw = read_bytes(sock, 4)

    # Find number of payload bytes to read
    header = struct.unpack("!I", header_raw)
    length = header[0]

    # Read payload
    payload = read_bytes(sock, length)

    return json.loads(payload.decode("utf-8"))


async def send_command_async(writer: asyncio.StreamWriter, cmd_dict: dict[str, Any]) -> None:
    """Send a command asynchronously to a socket.

    Args:
        writer: A asyncio.StreamWriter instance connected to the socket.
        cmd_dict: A dict of the serializable representation of a Command.

    """
    # Create payload with header
    payload = json.dumps(cmd_dict).encode("utf-8")
    header = struct.pack("!I", len(payload))
    data = header + payload

    # Write payload to stream
    writer.write(data)
    await writer.drain()


async def read_command_async(reader: asyncio.StreamReader) -> dict[str, Any]:
    """Read a command asynchronously from a socket.

    Args:
        reader: A asyncio.StreamReader instance connected to the socket.

    Returns:
        A dict of the serializable representation of a Command.

    """
    # Get prefix length header - 4 bytes
    header_raw = await reader.readexactly(4)

    # Find number of payload bytes to read
    header = struct.unpack("!I", header_raw)
    length = header[0]

    # Read payload
    payload = await reader.readexactly(length)

    return json.loads(payload.decode("utf-8"))


async def handle_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, request_dispatcher: RequestDispatcher
) -> None:
    """Asynchronously handle client requests sent to a unix socket server.

    Args:
        reader: A asyncio.StreamReader instance for reading from a socket.
        writer: A asyncio.StreamWriter instance for writing to a socket.
        request_dispatcher: A RequestDispatcher instance for handling command
            requests.

    """
    payload = await read_command_async(reader)
    cmd_req = CommandRequest.from_dict(payload)
    resp = await request_dispatcher.handle(cmd_req)
    await send_command_async(writer, resp.to_dict())
    writer.close()
    await writer.wait_closed()


async def handle_command(
    cmd_queue: asyncio.Queue,
    cmd_dispatcher: CommandDispatcher,
) -> None:
    """Asynchronously handle daemon commands from a Command queue.

    Args:
        cmd_queue: A asyncio.Queue instance to pull Command instances from.
        cmd_dispatcher: A CommandDispatcher instance for handling commands.

    """
    while True:
        cmd = await cmd_queue.get()
        cmd_dispatcher.handle(cmd)


async def serve(sock_path: str, db_path: str) -> None:
    """Serve the CLI daemon as a background process.

    NOTE: This serves a unix socket server that listens for incoming command
    requests from the associated stega CLI application on the same machine.
    Each request is mapped to its corresponding command which is either sent to
    a queue that is processed asynchronously (writes) or synchronously returns a
    result (reads). In either case the server will send back a response to the
    CLI application over the same socket indicating the submission and/or result
    of the command.

    Args:
        sock_path: A str of the path to the socket.
        db_path: A str of the path to the local database cache.

    """
    # Initialzie database
    db.init_db(db_path)

    # Queue to handle async tasks read from socket
    cmd_queue = asyncio.Queue()

    # Command dispatcher to send commands to appropriate handlers
    cmd_dispatcher = bootstrap_cmd_dispatcher()

    # Request dispatcher to delegate requests to appropriate commands
    req_dispatcher = RequestDispatcher(cmd_dispatcher=cmd_dispatcher, cmd_queue=cmd_queue)

    # Create socket handler
    handle_client_partial = functools.partial(handle_client, request_dispatcher=req_dispatcher)
    server = await asyncio.start_unix_server(handle_client_partial, path=sock_path)

    # Create cmd consumer task, handles writes asynchronously
    background_tasks = set()
    task = asyncio.create_task(handle_command(cmd_queue, cmd_dispatcher))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    async with server:
        await server.serve_forever()
