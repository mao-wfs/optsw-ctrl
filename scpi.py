__all__ = [
    "connect",
]


# standard library
import os
import sys
from logging import basicConfig, INFO, getLogger
from logging import FileHandler, StreamHandler
from socket import socket, AF_INET, SOCK_STREAM
from typing import Optional, Union
from pathlib import Path


# constants
AUTO_RECV: bool = True
BUFSIZE: int = 4096
ENCODING: str = "ascii"
END_SEND: str = "\n"
END_RECV: str = "\n"
KWD_COMMENT: str = "#"
KWD_QUERY: str = "?"
LOG_WIDTH: int = 100
TIMEOUT: Optional[float] = None


# module logger
logger = getLogger(__name__)


# type aliases
PathLike = Union[Path, str]


# main feature
class CustomSocket(socket):
    """Custom socket class to send/recv string with logging."""

    def send(self, string: str) -> int:
        """Same as socket.send(), but accepts string, not bytes."""
        n_bytes = super().send((string + END_SEND).encode(ENCODING))

        host, port = self.getpeername()
        logger.info(f"{host}:{port} <- {shorten(string, LOG_WIDTH)}")
        return n_bytes

    def recv(self) -> str:
        """Same as socket.recv(), but returns string, not bytes."""
        string = super().recv(BUFSIZE).decode(ENCODING).rstrip(END_RECV)

        host, port = self.getpeername()
        logger.info(f"{host}:{port} -> {shorten(string, LOG_WIDTH)}")
        return string

    def send_from(self, path: Path, auto_recv: bool = AUTO_RECV) -> None:
        """Send line(s) written in a file and receive data if exists."""
        with open(path) as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith(KWD_COMMENT):
                    continue

                self.write(line)

                if auto_recv and line.endswith(KWD_QUERY):
                    self.recv()


def connect(host: str, port: int, timeout: Optional[float] = TIMEOUT) -> CustomSocket:
    """Connect to an SCPI server and returns a custom socket object.

    Args:
        host: IP address or host name of the server.
        port: Port of the server.
        timeout: Timeout value in units of seconds.

    Returns:
        Custom socket object.

    Examples:
        To send an SCPI command to a server::

            with connect('192.168.1.3', 5000) as sock:
                sock.send('*CLS')

        To receive a message from a server::

            with connect('192.168.1.3', 5000) as sock:
                sock.send('SYST:ERR?')
                print(sock.recv())

    """
    sock = CustomSocket(AF_INET, SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect((host, port))

    return sock


# helper features
def shorten(string: str, width: int, placeholder: str = "...") -> str:
    """Same as textwrap.shorten(), but compatible with string without whitespaces."""
    return string[:width] + (placeholder if string[width:] else "")


# main script
if __name__ == "__main__":
    """Mini tool to send command or line(s) written in a file.

    Usage:
        $ export FG_HOST=<host name>
        $ export FG_PORT=<port number>
        $ export PG_HOST=<host name>
        $ export PG_PORT=<port number>
        $ poetry run python scpi.py [FG|PG] <file path or command>

    """
    basicConfig(
        level=INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=(StreamHandler(), FileHandler("scpi.log")),
    )

    device = sys.argv[1]
    path_or_cmd = sys.argv[2]

    if device.upper() == "FG":
        host = os.environ["FG_HOST"]
        port = os.environ["FG_PORT"]
    elif device.upper() == "PG":
        host = os.environ["PG_HOST"]
        port = os.environ["PG_PORT"]
    else:
        raise ValueError("Device must be either FG or PG.")

    if Path(path_or_cmd).exists():
        with connect(host, port) as sock:
            sock.send_from(path_or_cmd)
    else:
        with connect(host, port) as sock:
            sock.send(path_or_cmd)

            if path_or_cmd.endswith(KWD_QUERY):
                sock.recv()
