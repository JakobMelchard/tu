"""TCP and UDP echo with a length-prefixed framing mini-protocol (note 10).

Framing: every message is  <2-byte big-endian length><payload>.  TCP is a
byte stream, so without framing the receiver cannot know where one message
ends; UDP preserves datagram boundaries but the same framing keeps the code
symmetric.  Servers are single-threaded and stop when `stop_event` is set.

RFC sections: the calls map onto RFC 9293 section 3.9.1's abstract user
interface (OPEN = connect/listen+accept, SEND = sendall, RECEIVE = recv,
CLOSE = close).  Section 2.2 ("byte-stream service") and section 3.9.1.3 (a
RECEIVE returns when a PUSH is seen or the buffer fills, not per SEND) are why
`recv_exact` loops and why framing is needed at all.  Loopback only: every
server binds 127.0.0.1 with port 0, so tests never leave the host.
"""
import socket
import struct
import sys
import threading

HDR = struct.Struct("!H")


def recv_exact(conn, n):
    """Loop until n bytes arrived: recv() may return fewer bytes than asked."""
    buf = b""
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("peer closed mid-message")
        buf += chunk
    return buf


def send_msg(conn, payload):
    if len(payload) > 0xFFFF:
        raise ValueError("payload too long for 16-bit length prefix")
    conn.sendall(HDR.pack(len(payload)) + payload)


def recv_msg(conn):
    (n,) = HDR.unpack(recv_exact(conn, HDR.size))
    return recv_exact(conn, n)


# ---------------------------------------------------------------- TCP
def tcp_server(host="127.0.0.1", port=0, stop_event=None, ready=None, transform=lambda b: b):
    """socket -> bind -> listen -> accept -> recv/send -> close.  Passing port 0
    lets the OS pick; the chosen port is published via `ready` (a dict)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(5)
        srv.settimeout(0.2)                          # so the loop can notice stop_event
        if ready is not None:
            ready["port"] = srv.getsockname()[1]
            ready["event"].set()
        while stop_event is None or not stop_event.is_set():
            try:
                conn, _ = srv.accept()
            except socket.timeout:
                continue
            with conn:
                try:
                    while True:
                        msg = recv_msg(conn)
                        if msg == b"QUIT":
                            break
                        send_msg(conn, transform(msg))
                except ConnectionError:
                    pass


def tcp_client(host, port, messages):
    """socket -> connect -> send/recv -> close.  Returns echoed replies."""
    with socket.create_connection((host, port)) as c:
        replies = []
        for m in messages:
            send_msg(c, m)
            replies.append(recv_msg(c))
        send_msg(c, b"QUIT")
    return replies


# ---------------------------------------------------------------- UDP
def udp_server(host="127.0.0.1", port=0, stop_event=None, ready=None):
    """No connection: recvfrom tells us who sent it, sendto answers them."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((host, port))
        s.settimeout(0.2)
        if ready is not None:
            ready["port"] = s.getsockname()[1]
            ready["event"].set()
        while stop_event is None or not stop_event.is_set():
            try:
                data, addr = s.recvfrom(65535)
            except socket.timeout:
                continue
            (n,) = HDR.unpack(data[:2])
            s.sendto(HDR.pack(n) + data[2:2 + n], addr)


def udp_client(host, port, messages, timeout=2.0):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(timeout)
        replies = []
        for m in messages:
            s.sendto(HDR.pack(len(m)) + m, (host, port))
            data, _ = s.recvfrom(65535)
            replies.append(data[2:2 + HDR.unpack(data[:2])[0]])
    return replies


def start_server(fn, **kw):
    """Run a server in a daemon thread; returns (port, stop_event)."""
    stop, ready = threading.Event(), {"event": threading.Event()}
    t = threading.Thread(target=fn, kwargs={"stop_event": stop, "ready": ready, **kw}, daemon=True)
    t.start()
    ready["event"].wait(2.0)
    return ready["port"], stop


if __name__ == "__main__":
    port, stop = start_server(tcp_server, transform=bytes.upper)
    print("TCP:", tcp_client("127.0.0.1", port, [b"hello", b"world", b""]))
    stop.set()
    port, stop = start_server(udp_server)
    print("UDP:", udp_client("127.0.0.1", port, [b"ping", b"x" * 1000]))
    stop.set()
