__all__ = [
    "connect",
]


# standard library
from socket import socket, AF_INET, SOCK_STREAM
from typing import Optional, Sequence, Union
from logging import getLogger
# constants
BUFSIZE: int = 4096
ENCODING: str = "ascii"
FLAGS: int = 0
TIMEOUT: float = None


# module logger
logger = getLogger(__name__)


# helper features
class CustomSocket(socket):
    """Custom socket class to send/recv string with logging."""

    def send(
        self,
        command: str,
        flags: int = FLAGS,
        encoding: str = ENCODING,
    ) -> int:
        """Same as socket.send(), but accepts string, not bytes."""
        n_bytes = super().send(command.encode(encoding), flags)

        host, port = self.getpeername()
        logger.info(f"{host}, {port}, {command}")

        return n_bytes

    def recv(
        self,
        bufsize: int = BUFSIZE,
        flags: int = FLAGS,
        encoding: str = ENCODING,
    ) -> str:
        """Same as socket.recv(), but returns string, not bytes."""
        received = super().recv(bufsize, flags).decode(encoding)

        host, port = self.getpeername()
        logger.info(f"{host}, {port}, {received}")

        return received


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
                sock.send("SYST:ERR?")
                print(sock.recv())

    """
    sock = CustomSocket(AF_INET, SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect((host, port))

    return sock
