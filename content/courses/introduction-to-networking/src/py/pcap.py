"""Classic libpcap file format reader/writer (note 11).

Global header (24 bytes): magic, version 2.4, thiszone, sigfigs, snaplen,
linktype.  Each record: ts_sec, ts_usec, incl_len, orig_len, then the frame.
Magic 0xa1b2c3d4 in the file's native byte order tells the reader the
endianness (0xa1b23c4d for nanosecond timestamps).  Not pcapng.

No vendored RFC defines this format (it is libpcap's), so the tests check a
round trip, a hand-written big-endian nanosecond file, and that
`synthetic_trace()` is a legal walk through RFC 9293's state machine
(`test_tcp_fsm.py`).
"""
import struct
import sys

LINKTYPE_ETHERNET = 1
MAGIC_USEC, MAGIC_NSEC = 0xA1B2C3D4, 0xA1B23C4D


def write_pcap(path, frames, linktype=LINKTYPE_ETHERNET, snaplen=65535):
    """frames: iterable of (timestamp_seconds: float, frame: bytes)."""
    with open(path, "wb") as f:
        f.write(struct.pack("<IHHiIII", MAGIC_USEC, 2, 4, 0, 0, snaplen, linktype))
        for ts, frame in frames:
            sec, usec = int(ts), int(round((ts - int(ts)) * 1e6))
            cap = frame[:snaplen]
            f.write(struct.pack("<IIII", sec, usec, len(cap), len(frame)) + cap)


def read_pcap(path):
    """Yields (timestamp_seconds, frame_bytes); see read_pcap_header for metadata."""
    with open(path, "rb") as f:
        endian, nsec, _, _ = _header(f.read(24))
        while True:
            rec = f.read(16)
            if len(rec) < 16:
                return
            sec, frac, incl, _orig = struct.unpack(endian + "IIII", rec)
            ts = sec + frac / (1e9 if nsec else 1e6)
            yield ts, f.read(incl)


def read_pcap_header(path):
    with open(path, "rb") as f:
        endian, nsec, snaplen, linktype = _header(f.read(24))
    return {"endian": "little" if endian == "<" else "big", "nanosecond": nsec,
            "snaplen": snaplen, "linktype": linktype}


def _header(raw):
    magic = struct.unpack("<I", raw[:4])[0]
    if magic in (MAGIC_USEC, MAGIC_NSEC):
        endian = "<"
    else:
        magic = struct.unpack(">I", raw[:4])[0]
        if magic not in (MAGIC_USEC, MAGIC_NSEC):
            raise ValueError("not a classic pcap file (pcapng?)")
        endian = ">"
    _, _, _, _, snaplen, linktype = struct.unpack(endian + "HHiIII", raw[4:24])
    return endian, magic == MAGIC_NSEC, snaplen, linktype


# ---------------------------------------------------------------- synthetic trace
def synthetic_trace():
    """A tiny but realistic session: ARP resolve, TCP 3-way handshake, one
    HTTP-ish request and response, FIN/ACK teardown, and a DNS-like UDP
    datagram.  Returned as a list of (timestamp, frame)."""
    from headers import (build_ethernet, build_arp, build_ipv4, build_tcp, build_udp,
                         tcp_option_mss, ETH_P_IP, ETH_P_ARP, IPPROTO_TCP, IPPROTO_UDP)
    A, B = "10.0.0.1", "10.0.0.2"
    MA, MB, BC = "02:00:00:00:00:01", "02:00:00:00:00:02", "ff:ff:ff:ff:ff:ff"
    t = 1_700_000_000.0
    out = []

    def add(dst_mac, src_mac, etype, payload, dt=0.001):
        nonlocal t
        t += dt
        out.append((t, build_ethernet(dst_mac, src_mac, etype, payload)))

    add(BC, MA, ETH_P_ARP, build_arp(1, MA, A, "00:00:00:00:00:00", B))
    add(MA, MB, ETH_P_ARP, build_arp(2, MB, B, MA, A))
    isn_a, isn_b = 1000, 5000
    tcp = lambda s, d, sp, dp, *a, **k: build_ipv4(s, d, IPPROTO_TCP, build_tcp(s, d, sp, dp, *a, **k))
    add(MB, MA, ETH_P_IP, tcp(A, B, 40000, 80, isn_a, 0, "SYN", options=tcp_option_mss(1460)))
    add(MA, MB, ETH_P_IP, tcp(B, A, 80, 40000, isn_b, isn_a + 1, "SYN|ACK", options=tcp_option_mss(1460)))
    add(MB, MA, ETH_P_IP, tcp(A, B, 40000, 80, isn_a + 1, isn_b + 1, "ACK"))
    req = b"GET / HTTP/1.0\r\n\r\n"
    add(MB, MA, ETH_P_IP, tcp(A, B, 40000, 80, isn_a + 1, isn_b + 1, "PSH|ACK", payload=req))
    resp = b"HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\nhi"
    add(MA, MB, ETH_P_IP, tcp(B, A, 80, 40000, isn_b + 1, isn_a + 1 + len(req), "PSH|ACK", payload=resp))
    add(MB, MA, ETH_P_IP, tcp(A, B, 40000, 80, isn_a + 1 + len(req), isn_b + 1 + len(resp), "ACK"))
    add(MA, MB, ETH_P_IP, tcp(B, A, 80, 40000, isn_b + 1 + len(resp), isn_a + 1 + len(req), "FIN|ACK"))
    add(MB, MA, ETH_P_IP, tcp(A, B, 40000, 80, isn_a + 1 + len(req), isn_b + 2 + len(resp), "FIN|ACK"))
    add(MA, MB, ETH_P_IP, tcp(B, A, 80, 40000, isn_b + 2 + len(resp), isn_a + 2 + len(req), "ACK"))
    add(MB, MA, ETH_P_IP, build_ipv4(A, B, IPPROTO_UDP, build_udp(A, B, 53000, 53, b"\x12\x34" + b"\x01\x00" + b"\x00" * 8)))
    return out


if __name__ == "__main__":
    from headers import summarize
    import os, tempfile
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "synthetic.pcap")
    write_pcap(path, synthetic_trace())
    print("wrote", path, read_pcap_header(path))
    t0 = None
    for ts, frame in read_pcap(path):
        t0 = t0 or ts
        print(f"{ts - t0:8.6f}  {summarize(frame)}")
