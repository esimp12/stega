import contextlib
import json
import socket
import struct
import typing as T


@contextlib.contextmanager
def acquire_connection(sock_path: str) -> T.Generator[socket.SocketType, None, None]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(sock_path)
        yield s


@contextlib.contextmanager
def serve_socket(sock_path: str) -> T.Generator[socket.SocketType, None, None]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.bind(sock_path)
        s.listen()
        yield s


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
    header_raw = read_bytes(sock, 4)

    # Find number of payload bytes to read
    header = struct.unpack("!I", header_raw)
    length = header[0]

    # Read payload
    payload = read_bytes(sock, length)

    return json.loads(payload.decode("utf-8"))


def send_command(sock: socket.SocketType, cmd: dict[str, T.Any]) -> None: 
    payload = json.dumps(cmd).encode("utf-8")
    header = struct.pack("!I", len(payload))
    sock.sendall(header + payload)


def serve(sock_path: str) -> None:
    with serve_socket(sock_path) as s:
        while True:
            conn, _ = s.accept()
            with conn:
                cmd = read_command(conn)
                print(cmd)
