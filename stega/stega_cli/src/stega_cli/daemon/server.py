import socket
import typing as T


def acquire_connection(
    host: str,
    port: int,
) -> T.Generator[, None, None]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        conn, _ = s.accept()
        with conn:
            yield conn


def recv_command(conn) -> Command:
    """
    COMMAND



    """
    pass


def main():
    with acquire_connection() as conn:
        cmd = recv_command(conn)
        dispatch(cmd)
