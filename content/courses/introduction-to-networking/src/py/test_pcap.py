import struct
from pcap import write_pcap, read_pcap, read_pcap_header, synthetic_trace, MAGIC_USEC
from headers import summarize, parse_frame


def test_roundtrip_and_header(tmp_path):
    p = tmp_path / "t.pcap"
    frames = synthetic_trace()
    write_pcap(p, frames)
    raw = p.read_bytes()
    assert struct.unpack("<I", raw[:4])[0] == MAGIC_USEC and len(raw) == 24 + sum(16 + len(f) for _, f in frames)
    assert read_pcap_header(p) == {"endian": "little", "nanosecond": False, "snaplen": 65535, "linktype": 1}
    back = list(read_pcap(p))
    assert [f for _, f in back] == [f for _, f in frames]
    assert all(abs(a - b) < 1e-6 for (a, _), (b, _) in zip(back, frames))


def test_big_endian_nanosecond_file_is_read(tmp_path):
    p = tmp_path / "be.pcap"
    frame = b"\xaa" * 20
    p.write_bytes(struct.pack(">IHHiIII", 0xA1B23C4D, 2, 4, 0, 0, 100, 1)
                  + struct.pack(">IIII", 5, 500_000_000, len(frame), len(frame)) + frame)
    assert read_pcap_header(p)["endian"] == "big"
    (ts, f), = read_pcap(p)
    assert ts == 5.5 and f == frame


def test_synthetic_trace_decodes_as_handshake_and_teardown():
    summaries = [summarize(f) for _, f in synthetic_trace()]
    assert summaries[0].startswith("ARP who-has") and summaries[1].startswith("ARP 10.0.0.2 is-at")
    flags = [dict(parse_frame(f)).get("tcp", {}).get("flags_str") for _, f in synthetic_trace()[2:11]]
    assert flags == ["SYN", "SYN|ACK", "ACK", "PSH|ACK", "PSH|ACK", "ACK", "FIN|ACK", "FIN|ACK", "ACK"]
    assert summaries[-1].startswith("UDP 10.0.0.1:53000 > 10.0.0.2:53")
