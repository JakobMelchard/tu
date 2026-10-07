"""Minimal Telnet: RFC 854 stream parsing and RFC 1143 option negotiation (note 08).

Telnet is a byte stream where 0xFF (IAC, 'interpret as command') escapes
commands (RFC 854, "TELNET COMMAND STRUCTURE": IAC 255, DONT 254, DO 253,
WONT 252, WILL 251, SB 250, SE 240).  Option negotiation (RFC 855) uses
WILL/WONT (I will/won't do X) and DO/DONT (please do/don't do X).
Sub-negotiation SB ... SE carries option parameters (e.g. terminal type).

`QOption` is RFC 1143 section 7's example state machine, row for row: per
option and per side a state NO/YES/WANTNO/WANTYES and a queue bit.  The rules
it enforces are section 2's: answer every request that proposes a change
(so a repeated DO for a refused option is refused again), never answer one
that does not (WONT for a disabled option is ignored), and never answer a
refusal with a new request.  `negotiate` is a refuse-by-default client on top.
"""
IAC, DONT, DO, WONT, WILL, SB, SE = 255, 254, 253, 252, 251, 250, 240
NOP, GA = 241, 249
OPTS = {0: "BINARY", 1: "ECHO", 3: "SGA", 24: "TTYPE", 31: "NAWS", 32: "TSPEED", 34: "LINEMODE"}
CMDS = {DONT: "DONT", DO: "DO", WONT: "WONT", WILL: "WILL", SB: "SB", SE: "SE", NOP: "NOP", GA: "GA"}


def parse_stream(data):
    """Split raw bytes into ('data', bytes) and ('cmd', name, option[, payload]) items.
    IAC IAC is an escaped literal 0xFF data byte."""
    items, text, i = [], b"", 0

    def flush():
        nonlocal text
        if text:
            items.append(("data", text))
            text = b""
    while i < len(data):
        b = data[i]
        if b != IAC:
            text += bytes([b])
            i += 1
            continue
        cmd = data[i + 1]
        if cmd == IAC:
            text += b"\xff"
            i += 2
        elif cmd in (DO, DONT, WILL, WONT):
            flush()
            items.append(("cmd", CMDS[cmd], data[i + 2]))
            i += 3
        elif cmd == SB:
            flush()
            end = data.index(bytes([IAC, SE]), i + 2)
            items.append(("cmd", "SB", data[i + 2], data[i + 3:end]))
            i = end + 2
        else:
            flush()
            items.append(("cmd", CMDS.get(cmd, f"cmd{cmd}"), None))
            i += 2
    flush()
    return items


NO, YES, WANTNO, WANTYES, EMPTY, OPPOSITE = "NO", "YES", "WANTNO", "WANTYES", "EMPTY", "OPPOSITE"


class QOption:
    """RFC 1143 section 7 for one option.  Side 'him' is enabled by his WILL and
    answered with DO/DONT; side 'us' is the mirror ("with DO-WILL, DONT-WONT,
    him-us, himq-usq swapped").  Methods return the command to send, or None."""

    def __init__(self, accept_him=False, accept_us=False):
        self.state = {"him": NO, "us": NO}
        self.queue = {"him": EMPTY, "us": EMPTY}
        self.accept = {"him": accept_him, "us": accept_us}

    @staticmethod
    def _cmds(side):                      # (enable, disable) we send for that side
        return (DO, DONT) if side == "him" else (WILL, WONT)

    def _set(self, side, state, queue=EMPTY):
        self.state[side], self.queue[side] = state, queue

    def received_enable(self, side):      # WILL for 'him', DO for 'us'
        yes, no = self._cmds(side)
        st, q = self.state[side], self.queue[side]
        if st == NO:
            if self.accept[side]:
                self._set(side, YES)
                return yes
            return no                                  # refuse; state stays NO
        if st == WANTNO:                               # error: DONT answered by WILL
            self._set(side, NO if q == EMPTY else YES)
        elif st == WANTYES:
            if q == EMPTY:
                self._set(side, YES)
            else:
                self._set(side, WANTNO)
                return no
        return None                                    # YES: ignore

    def received_disable(self, side):     # WONT for 'him', DONT for 'us'
        yes, no = self._cmds(side)
        st, q = self.state[side], self.queue[side]
        if st == YES:
            self._set(side, NO)
            return no
        if st == WANTNO and q == OPPOSITE:
            self._set(side, WANTYES)
            return yes
        if st in (WANTNO, WANTYES):
            self._set(side, NO)
        return None                                    # NO: ignore

    def request(self, side, enable):
        """Our own initiative ('If we decide to ask him to enable/disable'),
        with the queue bit; raises where the RFC says Error."""
        yes, no = self._cmds(side)
        st, q = self.state[side], self.queue[side]
        want, pending, target = (WANTYES, WANTNO, YES) if enable else (WANTNO, WANTYES, NO)
        if st == (NO if enable else YES):
            self._set(side, want)
            return yes if enable else no
        if st == target:
            raise ValueError("already " + ("enabled" if enable else "disabled"))
        if st == pending and q == EMPTY:
            self._set(side, pending, OPPOSITE)         # queue the change of mind
            return None
        if st == want and q == OPPOSITE:
            self._set(side, want, EMPTY)               # cancel the queued opposite
            return None
        raise ValueError("already negotiating" if st == want else "already queued")


class Negotiator:
    """Per-connection table of QOption; `receive` answers a parsed stream."""

    def __init__(self, will_do=("SGA",), will_accept=("ECHO", "SGA")):
        self.will_do, self.will_accept, self.options = will_do, will_accept, {}

    def option(self, opt):
        name = OPTS.get(opt, str(opt))
        return self.options.setdefault(opt, QOption(accept_him=name in self.will_accept,
                                                    accept_us=name in self.will_do))

    def receive(self, items):
        handler = {"WILL": ("him", True), "WONT": ("him", False),
                   "DO": ("us", True), "DONT": ("us", False)}
        out = b""
        for item in items:
            if item[0] == "cmd" and item[1] in handler:
                side, enable = handler[item[1]]
                q = self.option(item[2])
                cmd = q.received_enable(side) if enable else q.received_disable(side)
                if cmd is not None:
                    out += bytes([IAC, cmd, item[2]])
        return out


def negotiate(items, will_do=("SGA",), will_accept=("ECHO", "SGA")):
    """Reply bytes to one batch of commands from a fresh connection (client side).
    will_do: options we agree to perform when asked DO; will_accept: options we
    let the server perform when it says WILL.  Everything else is refused."""
    return Negotiator(will_do, will_accept).receive(items)


def escape_data(data):
    return data.replace(b"\xff", b"\xff\xff")


def describe(items):
    lines = []
    for it in items:
        if it[0] == "data":
            lines.append(f"DATA {it[1]!r}")
        elif it[1] == "SB":
            lines.append(f"IAC SB {OPTS.get(it[2], it[2])} {it[3].hex()} IAC SE")
        elif it[2] is None:
            lines.append(f"IAC {it[1]}")
        else:
            lines.append(f"IAC {it[1]} {OPTS.get(it[2], it[2])}")
    return lines


if __name__ == "__main__":
    server_hello = bytes([IAC, DO, 24, IAC, WILL, 1, IAC, WILL, 3, IAC, DO, 31]) + b"login: "
    items = parse_stream(server_hello)
    print("\n".join(describe(items)))
    print("reply:", "\n".join(describe(parse_stream(negotiate(items)))))
