import socket
import threading
import pytest
from sockets_echo import *


def test_tcp_echo_roundtrip_with_framing():
    port, stop = start_server(tcp_server)
    try:
        msgs = [b"hello", b"", b"x" * 5000, bytes(range(256))]
        assert tcp_client("127.0.0.1", port, msgs) == msgs
        assert tcp_client("127.0.0.1", port, [b"again"]) == [b"again"]    # second connection
    finally:
        stop.set()


def test_framing_survives_coalesced_and_split_segments():
    """Two messages sent in one write must come back as two; recv_exact copes with
    the server delivering one message over several recv() calls."""
    port, stop = start_server(tcp_server)
    try:
        with socket.create_connection(("127.0.0.1", port)) as c:
            c.sendall(HDR.pack(3) + b"abc" + HDR.pack(2) + b"de")   # Nagle/coalescing
            assert recv_msg(c) == b"abc" and recv_msg(c) == b"de"
            big = b"y" * 70000
            with pytest.raises(ValueError):
                send_msg(c, big)
            send_msg(c, b"QUIT")
    finally:
        stop.set()


def test_udp_echo_and_boundaries():
    port, stop = start_server(udp_server)
    try:
        assert udp_client("127.0.0.1", port, [b"ping", b"", b"z" * 1400]) == [b"ping", b"", b"z" * 1400]
    finally:
        stop.set()


def test_recv_exact_raises_on_early_close():
    a, b = socket.socketpair()
    a.sendall(b"\x00\x05ab")
    a.close()
    with pytest.raises(ConnectionError):
        recv_msg(b)
    b.close()
