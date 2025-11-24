import contextlib
import socket
import struct
import typing as T


@contextlib.contextmanager
def acquire_connection(
    host: str,
    port: int,
) -> T.Generator[socket.SocketType, None, None]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        yield s


@contextlib.contextmanager
def serve_connection(
    host: str,
    port: int,
) -> T.Generator[socket.SocketType, None, None]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        conn, _ = s.accept()
        with conn:
            yield conn


def read_bytes(sock: socket.SocketType, num_bytes: int) -> bytes:
    buf = b""
    while len(buf) < num_bytes:
        chunk = sock.recv(num_bytes - len(buf))
        if not chunk:
            raise ConnectionError("socket closed")
        buf += chunk
    return buf


def read_command(sock: socket.SocketType) -> dict[str, T.Any]:
    # Get prefix length header
    header = read_bytes(sock, 4)

    # Find number of payload bytes to read
    length, _ = struct.unpack("!I", header)

    # Read payload
    payload = read_bytes(sock, length)

    return json.loads(payload.decode("utf-8"))


def send_command(sock: socket.SocketType, cmd: dict[str, T.Any]) -> None: 
    payload = json.dumps(cmd).encode("utf-8")
    header = struct.pack("!I", len(payload))
    sock.sendall(header + payload)


def serve() -> None:
    with serve_connection(
        host="",
        port=8000,
    ) as conn:
        cmd = read_command(conn)
        print(cmd)
