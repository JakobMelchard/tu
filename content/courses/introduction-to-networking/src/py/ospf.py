"""OSPFv2 constants and LSA freshness, RFC 2328 (note 07).

`linkstate.py` runs the *algorithm* (Dijkstra over a synchronised database).
This module is the *protocol's* bookkeeping around it, and in particular the two
things the notes used to state without a source:

* **Which timers OSPF actually defines.**  RFC 2328 Appendix B fixes a handful
  of *architectural* constants (LSRefreshTime, MaxAge, ...) that no operator may
  change.  Everything an operator tunes is in Appendix C, and Appendix C gives
  **sample values, not defaults**: "Sample value for a local area network: 10
  seconds" for HelloInterval, and for RouterDeadInterval only "should be some
  multiple of the HelloInterval (say 4)".  The familiar 10 s / 40 s pair is the
  Appendix C sample times four, which is what Cisco IOS, FRR and BIRD ship --
  it is not an RFC default, and the RFC prescribes no link cost formula either
  (the reference-bandwidth rule is a vendor convention).

* **Which of two copies of an LSA is newer** (section 13.1).  Compare LS
  sequence number, then LS checksum, then age, with the two MaxAge special
  cases.  Flooding is only loop-free because every router answers this question
  identically.

Reference implementation of the tables an exam asks you to reproduce, plus a
`hello_dead_pair` helper for the "what happens if the two ends disagree?"
question -- Hello and Dead must match or the neighbours never form an adjacency
(section 10.5: the received Hello's HelloInterval and RouterDeadInterval must
equal the receiving interface's).
"""

# RFC 2328 Appendix B -- architectural constants; not configurable.
ARCHITECTURAL = {
    "LSRefreshTime": 1800,          # 30 minutes
    "MinLSInterval": 5,             # seconds
    "MinLSArrival": 1,              # second
    "MaxAge": 3600,                 # 1 hour
    "CheckAge": 300,                # 5 minutes
    "MaxAgeDiff": 900,              # 15 minutes
    "LSInfinity": 0xFFFFFF,         # 24-bit all ones
    "DefaultDestination": "0.0.0.0",
    "InitialSequenceNumber": 0x80000001,   # signed 32-bit
    "MaxSequenceNumber": 0x7FFFFFFF,
}

# RFC 2328 Appendix C.3 -- configurable per interface.  These are the RFC's own
# *sample* values for a local area network, not defaults.
SAMPLE_LAN = {
    "HelloInterval": 10,            # "Sample value for a local area network: 10 seconds"
    "RxmtInterval": 5,              # "Sample value for a local area network: 5 seconds"
    "InfTransDelay": 1,             # "Sample value for a local area network: 1 second"
}
SAMPLE_X25 = {"HelloInterval": 30}  # "Sample value for a X.25 PDN network: 30 seconds"
DEAD_INTERVAL_MULTIPLIER = 4        # Appendix C.3: "some multiple of the HelloInterval (say 4)"

# RFC 2328 Appendix A.1 -- encapsulation.
IP_PROTOCOL = 89
ALL_SPF_ROUTERS = "224.0.0.5"       # every OSPF router listens here
ALL_D_ROUTERS = "224.0.0.6"         # only the DR and BDR listen here

LSA_TYPES = {1: "router-LSA", 2: "network-LSA", 3: "summary-LSA (IP network)",
             4: "summary-LSA (ASBR)", 5: "AS-external-LSA"}


def hello_dead_pair(hello=None, multiplier=DEAD_INTERVAL_MULTIPLIER):
    """The (HelloInterval, RouterDeadInterval) an implementation derives from
    RFC 2328 Appendix C.3.  With the RFC's LAN sample and its suggested factor
    of 4 this is the familiar (10, 40)."""
    hello = SAMPLE_LAN["HelloInterval"] if hello is None else hello
    return hello, hello * multiplier


def adjacency_possible(local, remote):
    """RFC 2328 section 10.5: a Hello is only accepted if the network mask (on
    non-point-to-point links), HelloInterval and RouterDeadInterval it carries
    match the receiving interface's.  Returns the list of mismatching fields,
    empty when an adjacency can form."""
    return [k for k in ("mask", "HelloInterval", "RouterDeadInterval")
            if k in local and k in remote and local[k] != remote[k]]


class LSA:
    """Only the header fields section 13.1 compares."""

    def __init__(self, ls_type, ls_id, adv_router, seq, checksum=0, age=0):
        self.ls_type, self.ls_id, self.adv_router = ls_type, ls_id, adv_router
        self.seq, self.checksum, self.age = seq, checksum, age

    def identity(self):
        """Section 12.1: an LSA is identified by type, Link State ID and
        advertising router.  Two LSAs with the same identity are two
        *instances* of the same LSA; everything else is a different LSA."""
        return (self.ls_type, self.ls_id, self.adv_router)

    def is_max_age(self):
        return self.age >= ARCHITECTURAL["MaxAge"]

    def __repr__(self):
        return (f"LSA({LSA_TYPES.get(self.ls_type, self.ls_type)} {self.ls_id} from "
                f"{self.adv_router} seq=0x{self.seq:08x} age={self.age})")


def which_is_newer(a, b):
    """RFC 2328 section 13.1, "Determining which LSA is newer".  Returns
    "a", "b" or "same".  The order of the tests is the whole point: sequence
    number, then checksum, then the two MaxAge rules, then an age difference of
    more than MaxAgeDiff; otherwise the instances count as identical.
    """
    if a.identity() != b.identity():
        raise ValueError("section 13.1 compares two instances of the same LSA")
    if a.seq != b.seq:                                    # signed comparison
        return "a" if _sgn(a.seq) > _sgn(b.seq) else "b"
    if a.checksum != b.checksum:                          # larger checksum wins
        return "a" if a.checksum > b.checksum else "b"
    if a.is_max_age() != b.is_max_age():                  # MaxAge instance wins
        return "a" if a.is_max_age() else "b"
    if abs(a.age - b.age) > ARCHITECTURAL["MaxAgeDiff"]:  # smaller age wins
        return "a" if a.age < b.age else "b"
    return "same"


def _sgn(seq):
    """LS sequence numbers are *signed* 32-bit: 0x80000001 (the initial value)
    is the most negative, 0x7fffffff the largest."""
    return seq - (1 << 32) if seq >= (1 << 31) else seq


def install(database, lsa):
    """Section 13: accept an LSA into the link-state database only if it is
    newer than the copy already held.  Returns True when the database changed
    (and the LSA therefore has to be flooded on)."""
    have = database.get(lsa.identity())
    if have is not None and which_is_newer(lsa, have) != "a":
        return False
    database[lsa.identity()] = lsa
    return True


def demo():
    hello, dead = hello_dead_pair()
    print("== RFC 2328 Appendix C.3 sample values (not defaults) ==")
    print(f"  HelloInterval       {hello} s   (RFC: 'sample value for a local area network')")
    print(f"  RouterDeadInterval  {dead} s   (RFC: 'some multiple of the HelloInterval (say 4)')")
    print(f"  RxmtInterval        {SAMPLE_LAN['RxmtInterval']} s, "
          f"InfTransDelay {SAMPLE_LAN['InfTransDelay']} s")
    print(f"  Hello on a X.25 PDN {SAMPLE_X25['HelloInterval']} s")
    print("  the RFC prescribes no cost formula: Appendix C.3 only requires cost > 0\n")

    print("== RFC 2328 Appendix B architectural constants ==")
    for k, v in ARCHITECTURAL.items():
        print(f"  {k:<22} {v if not isinstance(v, int) or v < 0x1000 else hex(v)}")
    print()

    print("== section 10.5: mismatched Hello parameters block the adjacency ==")
    local = {"mask": "255.255.255.0", "HelloInterval": 10, "RouterDeadInterval": 40}
    remote = {"mask": "255.255.255.0", "HelloInterval": 10, "RouterDeadInterval": 120}
    print(f"  mismatching fields: {adjacency_possible(local, remote)}\n")

    print("== section 13.1: which instance is newer ==")
    db = {}
    first = LSA(1, "10.0.0.1", "10.0.0.1", ARCHITECTURAL["InitialSequenceNumber"], 0x1234, 30)
    newer = LSA(1, "10.0.0.1", "10.0.0.1", ARCHITECTURAL["InitialSequenceNumber"] + 1, 0x9876, 0)
    flush = LSA(1, "10.0.0.1", "10.0.0.1", newer.seq, newer.checksum, ARCHITECTURAL["MaxAge"])
    for lsa in (first, newer, first, flush):
        print(f"  install {lsa} -> {'flood on' if install(db, lsa) else 'discard (not newer)'}")


if __name__ == "__main__":
    demo()
